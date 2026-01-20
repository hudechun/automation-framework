"""
文件服务API路由
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import StreamingResponse, FileResponse
from typing import List, Optional
import io

from ...files.storage import file_storage

router = APIRouter()


@router.post("/upload", response_model=dict)
async def upload_file(
    file: UploadFile = File(...),
    file_type: str = Query("screenshot", regex="^(screenshot|log|video|export)$")
):
    """上传文件"""
    try:
        file_data = await file.read()
        result = await file_storage.save_file(
            file_data=file_data,
            filename=file.filename,
            file_type=file_type,
            metadata={"content_type": file.content_type}
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/upload-multiple", response_model=List[dict])
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    file_type: str = Query("screenshot", regex="^(screenshot|log|video|export)$")
):
    """批量上传文件"""
    results = []
    for file in files:
        try:
            file_data = await file.read()
            result = await file_storage.save_file(
                file_data=file_data,
                filename=file.filename,
                file_type=file_type,
                metadata={"content_type": file.content_type}
            )
            results.append(result)
        except Exception as e:
            results.append({"error": str(e), "filename": file.filename})
    return results


@router.get("/{file_id}/download")
async def download_file(file_id: str):
    """下载文件"""
    file_data = await file_storage.get_file(file_id)
    if not file_data:
        raise HTTPException(status_code=404, detail="File not found")
    
    return StreamingResponse(
        io.BytesIO(file_data),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={file_id}"}
    )


@router.get("/{file_id}/preview")
async def preview_file(file_id: str):
    """预览文件"""
    file_data = await file_storage.get_file(file_id)
    if not file_data:
        raise HTTPException(status_code=404, detail="File not found")
    
    # 根据文件类型设置media_type
    media_type = "image/png"  # 默认为图片
    
    return StreamingResponse(
        io.BytesIO(file_data),
        media_type=media_type
    )


@router.get("", response_model=List[dict])
async def list_files(
    file_type: Optional[str] = Query(None, regex="^(screenshot|log|video|export)$"),
    limit: int = Query(100, ge=1, le=1000)
):
    """列出文件"""
    files = await file_storage.list_files(file_type=file_type, limit=limit)
    return files


@router.delete("/{file_id}")
async def delete_file(file_id: str):
    """删除文件"""
    success = await file_storage.delete_file(file_id)
    if not success:
        raise HTTPException(status_code=404, detail="File not found")
    return {"message": "File deleted successfully"}


@router.get("/stats/storage")
async def get_storage_stats():
    """获取存储统计"""
    stats = await file_storage.get_storage_stats()
    return stats


@router.post("/cleanup")
async def cleanup_old_files(days: int = Query(30, ge=1, le=365)):
    """清理过期文件"""
    deleted_count = await file_storage.cleanup_old_files(days=days)
    return {"message": f"Deleted {deleted_count} files", "deleted_count": deleted_count}
