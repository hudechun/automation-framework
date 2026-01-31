"""
学籍验证学生管理：列表、详情、导入、导出、下载二维码
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
from common.vo import DataResponseModel, PageModel, PageResponseModel
from exceptions.exception import ServiceException
from module_student.entity.vo.student_verification_vo import StudentVerificationListVO, StudentVerificationUpdateDTO
from module_student.service.student_verification_service import StudentVerificationService
from config.env import AppConfig
from utils.log_util import logger
from utils.response_util import ResponseUtil

student_verification_controller = APIRouterPro(
    prefix="/student/verification",
    order_num=50,
    tags=["学籍验证-学生管理"],
    dependencies=[PreAuthDependency()],
)


def _verify_base_url() -> str:
    return (getattr(AppConfig, "verify_base_url", None) or "http://localhost:80").rstrip("/")


def _safe_filename(name: str, code: str) -> str:
    """生成安全的二维码文件名：姓名_验证码.png"""
    safe_name = re.sub(r'[/\\:*?"<>|]', "_", (name or "").strip()) or "未命名"
    return f"{safe_name}_{(code or '').strip()}.png"


@student_verification_controller.get(
    "/list",
    summary="学生列表",
    response_model=PageResponseModel[StudentVerificationListVO],
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
    result = await StudentVerificationService.list_students(query_db, q, is_page=True)
    # 排除 photo_blob，避免 JSON 序列化 binary 时 utf-8 解码报错
    if hasattr(result, "rows") and result.rows:
        clean_rows = [
            StudentVerificationListVO.model_validate(r).model_dump(by_alias=True)
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


@student_verification_controller.get(
    "/{student_id}",
    summary="学生详情",
)
async def get_student(
    request: Request,
    student_id: int,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
):
    obj = await StudentVerificationService.get_by_id(query_db, student_id)
    if not obj:
        raise ServiceException(message="学生不存在")
    data = StudentVerificationListVO.model_validate(obj)
    return ResponseUtil.success(data=data.model_dump(by_alias=True))


@student_verification_controller.put(
    "/{student_id}",
    summary="编辑学生记录",
)
async def update_student(
    request: Request,
    student_id: int,
    body: StudentVerificationUpdateDTO,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
):
    data = body.model_dump(by_alias=False, exclude_none=True)
    if not data:
        raise ServiceException(message="未提供任何修改字段")
    await StudentVerificationService.update_student(query_db, student_id, data)
    await query_db.commit()
    return ResponseUtil.success(msg="修改成功")


@student_verification_controller.post(
    "/import",
    summary="Excel 导入学生",
)
async def import_students(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    file: Annotated[UploadFile, File(description="Excel 文件，一行一条记录，列含姓名、性别、…、照片、验证有效日期")],
):
    if not file.filename or not file.filename.lower().endswith((".xlsx", ".xls")):
        raise ServiceException(message="请上传 Excel 文件（.xlsx 或 .xls）")
    ext = ".xlsx" if file.filename.lower().endswith(".xlsx") else ".xls"
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    try:
        result = await StudentVerificationService.import_from_excel(query_db, tmp_path)
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


@student_verification_controller.post(
    "/upload-photo",
    summary="上传学生照片（按验证码存储到 uploads/pic/photo/{验证码}.png）",
)
async def upload_photo(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    verification_code: Annotated[str, Form(description="16 位验证码")],
    file: Annotated[UploadFile, File(description="照片文件，支持 png/jpg/jpeg")],
):
    code = (verification_code or "").strip()
    if len(code) != 16:
        raise ServiceException(message="验证码必须为 16 位")
    obj = await StudentVerificationService.get_by_code(query_db, code)
    if not obj:
        raise ServiceException(message="未找到该验证码对应的学生")
    fn = (file.filename or "").lower()
    if not fn.endswith((".png", ".jpg", ".jpeg")):
        raise ServiceException(message="照片格式需为 png、jpg 或 jpeg")
    content = await file.read()
    if not content:
        raise ServiceException(message="照片文件为空")
    try:
        path = StudentVerificationService.save_photo_file(code, content)
        await StudentVerificationService.update_photo_blob(query_db, obj.id, content)
        await query_db.commit()
        logger.info("upload_photo success: code=%s path=%s size=%d (saved to DB)", code, path, len(content))
        return ResponseUtil.success(msg="上传成功（已存入文件和数据库）", data={"path": path})
    except OSError as e:
        await query_db.rollback()
        logger.exception("upload_photo OSError: code=%s err=%s", code, e)
        raise ServiceException(message=f"保存文件失败：{e}" if e.strerror else str(e))
    except Exception as e:
        await query_db.rollback()
        logger.exception("upload_photo: code=%s err=%s", code, e)
        raise ServiceException(message=str(e) or "上传失败")


@student_verification_controller.get(
    "/report/image/{student_id}",
    summary="获取报告图（PNG 流）",
    response_class=StreamingResponse,
)
async def get_report_image(
    request: Request,
    student_id: int,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
):
    obj = await StudentVerificationService.get_by_id(query_db, student_id)
    if not obj:
        raise ServiceException(message="学生不存在")
    base_url = _verify_base_url()
    png_bytes = StudentVerificationService.render_report_image(obj, base_url)
    return StreamingResponse(
        iter([png_bytes]),
        media_type="image/png",
        headers={"Content-Disposition": "inline; filename=report.png"},
    )


def _make_qr_png(url: str) -> bytes:
    """生成二维码 PNG 二进制"""
    qr = qrcode.QRCode(version=1, box_size=10, border=1)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@student_verification_controller.get(
    "/qr/image/{student_id}",
    summary="下载二维码图片（PNG），文件名：姓名_验证码.png",
    response_class=StreamingResponse,
)
async def get_qr_image(
    request: Request,
    student_id: int,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
):
    obj = await StudentVerificationService.get_by_id(query_db, student_id)
    if not obj:
        raise ServiceException(message="学生不存在")
    base = _verify_base_url()
    url = f"{base.rstrip('/')}/verify?code={obj.verification_code}"
    png_bytes = _make_qr_png(url)
    filename = _safe_filename(obj.name, obj.verification_code)
    return StreamingResponse(
        iter([png_bytes]),
        media_type="image/png",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quote(filename)}"},
    )


@student_verification_controller.post(
    "/qr/batch-download",
    summary="批量下载二维码（ZIP），每张命名为 姓名_验证码.png",
    response_class=StreamingResponse,
)
async def batch_download_qr(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    student_ids: Annotated[list[int], Body(embed=True, alias="studentIds")],
):
    if not student_ids:
        raise ServiceException(message="请选择要下载的学生")
    if len(student_ids) > 200:
        raise ServiceException(message="单次最多下载 200 个")
    base = _verify_base_url()
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for sid in student_ids:
            obj = await StudentVerificationService.get_by_id(query_db, sid)
            if not obj:
                continue
            url = f"{base.rstrip('/')}/verify?code={obj.verification_code}"
            png_bytes = _make_qr_png(url)
            filename = _safe_filename(obj.name, obj.verification_code)
            zf.writestr(filename, png_bytes)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=qrcodes.zip"},
    )


@student_verification_controller.post(
    "/report/batch-download",
    summary="批量下载验证报告图（ZIP），每张命名为 姓名_验证码.png",
    response_class=StreamingResponse,
)
async def batch_download_report(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    student_ids: Annotated[list[int], Body(embed=True, alias="studentIds")],
):
    if not student_ids:
        raise ServiceException(message="请选择要下载的学生")
    if len(student_ids) > 50:
        raise ServiceException(message="单次最多下载 50 个报告（生成较慢）")
    base = _verify_base_url()
    buf = io.BytesIO()
    count = 0
    try:
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for sid in student_ids:
                obj = await StudentVerificationService.get_by_id(query_db, sid)
                if not obj:
                    continue
                try:
                    png_bytes = StudentVerificationService.render_report_image(obj, base)
                except Exception as e:
                    logger.warning("batch_download_report skip id=%s: %s", sid, e)
                    continue
                filename = _safe_filename(obj.name, obj.verification_code)
                zf.writestr(filename, png_bytes)
                count += 1
        if count == 0:
            raise ServiceException(message="未能生成任何报告，请检查模板和照片配置")
    except ServiceException:
        raise
    except Exception as e:
        logger.exception("batch_download_report failed: %s", e)
        raise ServiceException(message=f"批量生成报告失败：{str(e)}")
    buf.seek(0)
    filename_utf8 = quote("学籍验证报告.zip", safe="")
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename_utf8}"},
    )
