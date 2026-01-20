"""会话管理API"""
from typing import Dict, Any, List


class SessionAPI:
    """会话管理API"""
    
    def __init__(self, client):
        self.client = client
    
    async def list(self, **filters) -> List[Dict[str, Any]]:
        """列出会话"""
        return await self.client.request("GET", "/api/sessions", params=filters)
    
    async def get(self, session_id: str) -> Dict[str, Any]:
        """获取会话详情"""
        return await self.client.request("GET", f"/api/sessions/{session_id}")
    
    async def restore(self, session_id: str) -> Dict[str, Any]:
        """恢复会话"""
        return await self.client.request("POST", f"/api/sessions/{session_id}/restore")
