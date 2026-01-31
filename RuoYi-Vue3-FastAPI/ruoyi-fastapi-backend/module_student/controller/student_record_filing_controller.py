"""
学籍备案表管理：学历证书电子注册备案表（模板2），与学籍验证报告独立
"""
import io
import os
import re
import tempfile
import zipfile
from urllib.parse import quote
from typing import Annotated

import qrcode
from fastapi import Body, File, Form, Query, Request, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from common.aspect.db_seesion import DBSessionDependency
from common.aspect.pre_auth import PreAuthDependency
from common.router import APIRouterPro
from common.vo import PageModel, PageResponseModel
from exceptions.exception import ServiceException
from module_student.entity.vo.student_record_filing_vo import StudentRecordFilingListVO, StudentRecordFilingUpdateDTO
from module_student.service.student_record_filing_service import StudentRecordFilingService
from config.env import AppConfig
from utils.log_util import logger
from utils.response_util import ResponseUtil

student_record_filing_controller = APIRouterPro(
    prefix="/student/record-filing",
    order_num=51,
    tags=["学籍验证-学历备案表"],
    dependencies=[PreAuthDependency()],
)


def _verify_base_url() -> str:
    return (getattr(AppConfig, "verify_base_url", None) or "http://localhost:80").rstrip("/")


def _safe_filename(name: str, code: str) -> str:
    safe_name = re.sub(r'[/\\:*?"<>|]', "_", (name or "").strip()) or "未命名"
    return f"{safe_name}_{(code or '').strip()}.png"


@student_record_filing_controller.get(
    "/list",
    summary="备案表列表",
    response_model=PageResponseModel[StudentRecordFilingListVO],
)
async def list_students(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    page_num: Annotated[int, Query(ge=1, alias="pageNum")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, alias="pageSize")] = 10,
    name: Annotated[str | None, Query()] = None,
    verification_code: Annotated[str | None, Query(alias="verificationCode")] = None,
):
    q = {"page_num": page_num, "page_size": page_size}
    if name:
        q["name"] = name
    if verification_code:
        q["verification_code"] = verification_code
    result = await StudentRecordFilingService.list_students(query_db, q, is_page=True)
    if hasattr(result, "rows") and result.rows:
        clean_rows = [
            StudentRecordFilingListVO.model_validate(r).model_dump(by_alias=True)
            for r in result.rows
        ]
        result = PageModel(
            rows=clean_rows,
            pageNum=result.page_num,
            pageSize=result.page_size,
            total=result.total,
            hasNext=result.has_next,
        )
    return ResponseUtil.success(model_content=result)


@student_record_filing_controller.get("/{student_id}", summary="备案表详情")
async def get_student(
    request: Request,
    student_id: int,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
):
    obj = await StudentRecordFilingService.get_by_id(query_db, student_id)
    if not obj:
        raise ServiceException(message="记录不存在")
    data = StudentRecordFilingListVO.model_validate(obj)
    return ResponseUtil.success(data=data.model_dump(by_alias=True))


@student_record_filing_controller.put("/{student_id}", summary="编辑备案表记录")
async def update_student(
    request: Request,
    student_id: int,
    body: StudentRecordFilingUpdateDTO,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
):
    data = body.model_dump(by_alias=False, exclude_none=True)
    if not data:
        raise ServiceException(message="未提供任何修改字段")
    await StudentRecordFilingService.update_student(query_db, student_id, data)
    await query_db.commit()
    return ResponseUtil.success(msg="修改成功")


@student_record_filing_controller.post("/import", summary="Excel 导入")
async def import_students(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    file: Annotated[UploadFile, File(description="Excel 文件")],
):
    if not file.filename or not file.filename.lower().endswith((".xlsx", ".xls")):
        raise ServiceException(message="请上传 Excel 文件（.xlsx 或 .xls）")
    ext = ".xlsx" if file.filename.lower().endswith(".xlsx") else ".xls"
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    try:
        result = await StudentRecordFilingService.import_from_excel(query_db, tmp_path)
        await query_db.commit()
        msg = f"导入成功 {result['success']} 条，失败 {result['fail']} 条"
        if result.get("fail_details"):
            msg += "；失败原因：" + "；".join(result["fail_details"])
        return ResponseUtil.success(data=result, msg=msg)
    except Exception as e:
        await query_db.rollback()
        logger.exception("import_students: %s", e)
        raise ServiceException(message=str(e) or "导入失败")
    finally:
        if os.path.isfile(tmp_path):
            try:
                os.unlink(tmp_path)
            except Exception:
                pass


@student_record_filing_controller.post("/upload-photo", summary="上传学生照片")
async def upload_photo(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    verification_code: Annotated[str, Form(description="16 位验证码")],
    file: Annotated[UploadFile, File(description="照片文件")],
):
    code = (verification_code or "").strip()
    if len(code) != 16:
        raise ServiceException(message="验证码必须为 16 位")
    obj = await StudentRecordFilingService.get_by_code(query_db, code)
    if not obj:
        raise ServiceException(message="未找到该验证码对应的记录")
    fn = (file.filename or "").lower()
    if not fn.endswith((".png", ".jpg", ".jpeg")):
        raise ServiceException(message="照片格式需为 png、jpg 或 jpeg")
    content = await file.read()
    if not content:
        raise ServiceException(message="照片文件为空")
    try:
        path = StudentRecordFilingService.save_photo_file(code, content)
        await StudentRecordFilingService.update_photo_blob(query_db, obj.id, content)
        await query_db.commit()
        return ResponseUtil.success(msg="上传成功", data={"path": path})
    except Exception as e:
        await query_db.rollback()
        logger.exception("upload_photo: %s", e)
        raise ServiceException(message=str(e) or "上传失败")


@student_record_filing_controller.get(
    "/report/image/{student_id}",
    summary="获取备案表报告图（PNG）",
    response_class=StreamingResponse,
)
async def get_report_image(
    request: Request,
    student_id: int,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
):
    obj = await StudentRecordFilingService.get_by_id(query_db, student_id)
    if not obj:
        raise ServiceException(message="记录不存在")
    base_url = _verify_base_url()
    png_bytes = StudentRecordFilingService.render_report_image(obj, base_url)
    return StreamingResponse(
        iter([png_bytes]),
        media_type="image/png",
        headers={"Content-Disposition": "inline; filename=record_filing_report.png"},
    )


def _make_qr_png(url: str) -> bytes:
    qr = qrcode.QRCode(version=1, box_size=10, border=1)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@student_record_filing_controller.get(
    "/qr/image/{student_id}",
    summary="下载二维码图片",
    response_class=StreamingResponse,
)
async def get_qr_image(
    request: Request,
    student_id: int,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
):
    obj = await StudentRecordFilingService.get_by_id(query_db, student_id)
    if not obj:
        raise ServiceException(message="记录不存在")
    base = _verify_base_url()
    url = f"{base.rstrip('/')}/verify-filing?code={obj.verification_code}"
    png_bytes = _make_qr_png(url)
    filename = _safe_filename(obj.name, obj.verification_code)
    return StreamingResponse(
        iter([png_bytes]),
        media_type="image/png",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quote(filename)}"},
    )


@student_record_filing_controller.post(
    "/qr/batch-download",
    summary="批量下载二维码（ZIP）",
    response_class=StreamingResponse,
)
async def batch_download_qr(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    student_ids: Annotated[list[int], Body(embed=True, alias="studentIds")],
):
    if not student_ids:
        raise ServiceException(message="请选择要下载的记录")
    if len(student_ids) > 200:
        raise ServiceException(message="单次最多 200 个")
    base = _verify_base_url()
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for sid in student_ids:
            obj = await StudentRecordFilingService.get_by_id(query_db, sid)
            if not obj:
                continue
            url = f"{base.rstrip('/')}/verify-filing?code={obj.verification_code}"
            png_bytes = _make_qr_png(url)
            filename = _safe_filename(obj.name, obj.verification_code)
            zf.writestr(filename, png_bytes)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=qrcodes_filing.zip"},
    )


@student_record_filing_controller.post(
    "/report/batch-download",
    summary="批量下载备案表报告（ZIP）",
    response_class=StreamingResponse,
)
async def batch_download_report(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    student_ids: Annotated[list[int], Body(embed=True, alias="studentIds")],
):
    if not student_ids:
        raise ServiceException(message="请选择要下载的记录")
    if len(student_ids) > 50:
        raise ServiceException(message="单次最多下载 50 个报告")
    base = _verify_base_url()
    buf = io.BytesIO()
    count = 0
    try:
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for sid in student_ids:
                obj = await StudentRecordFilingService.get_by_id(query_db, sid)
                if not obj:
                    continue
                try:
                    png_bytes = StudentRecordFilingService.render_report_image(obj, base)
                except Exception as e:
                    logger.warning("batch_download_report skip id=%s: %s", sid, e)
                    continue
                filename = _safe_filename(obj.name, obj.verification_code)
                zf.writestr(filename, png_bytes)
                count += 1
        if count == 0:
            raise ServiceException(message="未能生成任何报告")
    except ServiceException:
        raise
    except Exception as e:
        logger.exception("batch_download_report failed: %s", e)
        raise ServiceException(message=f"批量生成报告失败：{str(e)}")
    buf.seek(0)
    filename_utf8 = quote("学历备案表报告.zip", safe="")
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename_utf8}"},
    )
