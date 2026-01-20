"""
配置管理API路由
"""
from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel

router = APIRouter()


class ModelConfigCreate(BaseModel):
    """模型配置创建模型"""
    name: str
    provider: str
    model: str
    api_key: str
    params: dict = {}


@router.get("/models", response_model=List[dict])
async def list_model_configs():
    """列出模型配置"""
    # TODO: 实现列出模型配置逻辑
    return []


@router.post("/models", response_model=dict)
async def create_model_config(config: ModelConfigCreate):
    """创建模型配置"""
    # TODO: 实现创建模型配置逻辑
    return config.dict()


@router.put("/models/{config_id}", response_model=dict)
async def update_model_config(config_id: str, config: ModelConfigCreate):
    """更新模型配置"""
    # TODO: 实现更新模型配置逻辑
    return config.dict()


@router.delete("/models/{config_id}")
async def delete_model_config(config_id: str):
    """删除模型配置"""
    # TODO: 实现删除模型配置逻辑
    return {"message": "Config deleted"}
