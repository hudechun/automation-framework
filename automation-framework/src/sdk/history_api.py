"""历史记录API"""
from typing import Dict, Any, List


class HistoryAPI:
    """历史记录API"""
    
    def __init__(self, client):
        self.client = client
    
    async def list(self, skip: int = 0, limit: int = 100, **filters) -> List[Dict[str, Any]]:
        """列出执行记录"""
        params = {"skip": skip, "limit": limit, **filters}
        return await self.client.request("GET", "/api/executions", params=params)
    
    async def get(self, execution_id: str) -> Dict[str, Any]:
        """获取执行详情"""
        return await self.client.request("GET", f"/api/executions/{execution_id}")
    
    async def export(self, format: str = "json", **filters) -> bytes:
        """导出历史记录"""
        params = {"format": format, **filters}
        response = await self.client.http_client.post("/api/executions/export", params=params)
        return response.content
