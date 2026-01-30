"""
学籍验证学生管理：列表、详情、导入、导出、下载二维码
"""
import os
import tempfile
from typing import Annotated

import qrcode
from fastapi import File, Query, Request, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from common.aspect.db_seesion import DBSessionDependency
from common.aspect.pre_auth import PreAuthDependency
from common.router import APIRouterPro
from common.vo import DataResponseModel, PageResponseModel
from exceptions.exception import ServiceException
from module_student.entity.vo.student_verification_vo import StudentVerificationListVO
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


@student_verification_controller.get(
    "/list",
    summary="学生列表",
    response_model=PageResponseModel[StudentVerificationListVO],
)
async def list_students(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    page_num: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 10,
    name: Annotated[str | None, Query()] = None,
    verification_code: Annotated[str | None, Query()] = None,
):
    q = {"page_num": page_num, "page_size": page_size}
    if name:
        q["name"] = name
    if verification_code:
        q["verification_code"] = verification_code
    result = await StudentVerificationService.list_students(query_db, q, is_page=True)
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


@student_verification_controller.get(
    "/qr/image/{student_id}",
    summary="下载二维码图片（PNG）",
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
    qr = qrcode.QRCode(version=1, box_size=10, border=1)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    import io
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="image/png",
        headers={"Content-Disposition": "attachment; filename=qr.png"},
    )
