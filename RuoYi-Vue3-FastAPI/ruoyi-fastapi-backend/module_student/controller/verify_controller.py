"""
学籍验证对外接口（无需登录）：验证查询、报告图
- /verify/* 查询 student_verification（学籍验证报告表）
- /verify/filing/* 查询 student_record_filing（学籍备案表）
"""
from datetime import date
from typing import Annotated

from fastapi import Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from common.aspect.db_seesion import DBSessionDependency
from common.router import APIRouterPro
from config.env import AppConfig
from exceptions.exception import ServiceException
from module_student.entity.vo.student_verification_vo import VerifyCheckVO
from module_student.service.student_verification_service import StudentVerificationService
from module_student.service.student_record_filing_service import StudentRecordFilingService
from utils.response_util import ResponseUtil

verify_controller = APIRouterPro(
    prefix="/verify",
    order_num=51,
    tags=["学籍验证-对外"],
    dependencies=[],  # 不校验登录
)


def _verify_base_url() -> str:
    return (AppConfig.verify_base_url or "").rstrip("/") or "http://localhost:80"


@verify_controller.get(
    "/check",
    summary="根据验证码查询学籍（H5 用）",
    response_model=None,
)
async def verify_check(
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    code: Annotated[str, Query(description="16 位验证码")] = "",
):
    if not code or len(code) != 16:
        return ResponseUtil.success(
            data=VerifyCheckVO(
                expired=True,
                message="验证码无效",
            ).model_dump(by_alias=True),
        )
    obj = await StudentVerificationService.get_by_code(query_db, code.strip())
    if not obj:
        return ResponseUtil.success(
            data=VerifyCheckVO(
                expired=True,
                message="未找到该验证码对应的学籍信息",
            ).model_dump(by_alias=True),
        )
    expired = obj.valid_until and obj.valid_until < date.today()
    base = _verify_base_url()
    api_prefix = getattr(AppConfig, "app_root_path", "") or ""
    report_image_url = f"{base.rstrip('/')}{api_prefix}/verify/report/image?code={obj.verification_code}" if not expired else None
    return ResponseUtil.success(
        data=VerifyCheckVO(
            expired=expired,
            name=obj.name,
            report_image_url=report_image_url,
            message="已过期，无法查看报告" if expired else None,
        ).model_dump(by_alias=True),
    )


@verify_controller.get(
    "/report/image",
    summary="根据验证码获取学籍报告图（PNG，对外）",
    response_class=StreamingResponse,
)
async def verify_report_image(
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    code: Annotated[str, Query(description="16 位验证码")] = "",
):
    if not code or len(code) != 16:
        raise ServiceException(message="验证码无效")
    obj = await StudentVerificationService.get_by_code(query_db, code.strip())
    if not obj:
        raise ServiceException(message="未找到该验证码对应的学籍信息")
    if obj.valid_until and obj.valid_until < date.today():
        raise ServiceException(message="该学籍验证已过期，无法查看报告")
    base = _verify_base_url()
    png_bytes = StudentVerificationService.render_report_image(obj, base)
    return StreamingResponse(
        iter([png_bytes]),
        media_type="image/png",
        headers={"Content-Disposition": "inline; filename=report.png"},
    )


# ========== 学籍备案表验证（查询 student_record_filing） ==========
@verify_controller.get(
    "/filing/check",
    summary="根据验证码查询学籍备案表（H5 用）",
)
async def verify_filing_check(
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    code: Annotated[str, Query(description="16 位验证码")] = "",
):
    if not code or len(code) != 16:
        return ResponseUtil.success(
            data=VerifyCheckVO(
                expired=True,
                message="验证码无效",
            ).model_dump(by_alias=True),
        )
    obj = await StudentRecordFilingService.get_by_code(query_db, code.strip())
    if not obj:
        return ResponseUtil.success(
            data=VerifyCheckVO(
                expired=True,
                message="未找到该验证码对应的备案信息",
            ).model_dump(by_alias=True),
        )
    expired = obj.valid_until and obj.valid_until < date.today()
    base = _verify_base_url()
    api_prefix = getattr(AppConfig, "app_root_path", "") or ""
    report_image_url = f"{base.rstrip('/')}{api_prefix}/verify/filing/report/image?code={obj.verification_code}" if not expired else None
    return ResponseUtil.success(
        data=VerifyCheckVO(
            expired=expired,
            name=obj.name,
            report_image_url=report_image_url,
            message="已过期，无法查看报告" if expired else None,
        ).model_dump(by_alias=True),
    )


@verify_controller.get(
    "/filing/report/image",
    summary="根据验证码获取备案表报告图（PNG，对外）",
    response_class=StreamingResponse,
)
async def verify_filing_report_image(
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    code: Annotated[str, Query(description="16 位验证码")] = "",
):
    if not code or len(code) != 16:
        raise ServiceException(message="验证码无效")
    obj = await StudentRecordFilingService.get_by_code(query_db, code.strip())
    if not obj:
        raise ServiceException(message="未找到该验证码对应的备案信息")
    if obj.valid_until and obj.valid_until < date.today():
        raise ServiceException(message="该备案验证已过期，无法查看报告")
    base = _verify_base_url()
    png_bytes = StudentRecordFilingService.render_report_image(obj, base)
    return StreamingResponse(
        iter([png_bytes]),
        media_type="image/png",
        headers={"Content-Disposition": "inline; filename=record_filing_report.png"},
    )
