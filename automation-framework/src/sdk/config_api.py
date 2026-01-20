"""配置管理API"""
from typing import Dict, Any, List


class ConfigAPI:
    """配置管理API"""
    
    def __init__(self, client):
        self.client = client
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """列出模型配置"""
        return await self.client.request("GET", "/api/configs/models")
    
    async def create_model(self, **config) -> Dict[str, Any]:
        """创建模型配置"""
        return await self.client.request("POST", "/api/configs/models", json=config)
    
    async def update_model(self, config_id: str, **updates) -> Dict[str, Any]:
        """更新模型配置"""
        return await self.client.request("PUT", f"/api/configs/models/{config_id}", json=updates)
