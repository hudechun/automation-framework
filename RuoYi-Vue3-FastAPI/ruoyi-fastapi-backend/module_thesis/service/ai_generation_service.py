"""
AI生成服务 - 调用AI模型生成论文内容
"""
import json
import asyncio
from typing import Dict, Any, Optional, List
from enum import Enum
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions.exception import ServiceException
from module_admin.service.ai_model_service import AiModelService
from utils.log_util import logger


class ModelProvider(Enum):
    """模型提供商"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    QWEN = "qwen"
    CUSTOM = "custom"


class LLMProvider:
    """LLM提供商基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """聊天接口"""
        raise NotImplementedError


class OpenAIProvider(LLMProvider):
    """OpenAI API提供商"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        try:
            import openai
            self.client = openai.AsyncOpenAI(
                api_key=config['api_key'],
                base_url=config.get('api_base')
            )
        except ImportError:
            raise ImportError("openai package is not installed. Install it with: pip install openai")
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """OpenAI聊天接口（带重试）"""
        max_retries = 3
        base_delay = 1.0
        
        for attempt in range(max_retries):
            try:
                params = {
                    "model": self.config['model'],
                    "messages": messages,
                    **self.config.get('params', {}),
                    **kwargs
                }
                
                response = await self.client.chat.completions.create(**params)
                return response.choices[0].message.content
                
            except Exception as e:
                error_str = str(e).lower()
                
                if "429" in error_str or "rate limit" in error_str:
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        logger.warning(f"Rate limit exceeded. Retrying after {delay:.1f} seconds...")
                        await asyncio.sleep(delay)
                        continue
                    else:
                        raise ServiceException(message=f"Rate limit exceeded after {max_retries} attempts")
                
                raise


class AnthropicProvider(LLMProvider):
    """Anthropic API提供商"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        try:
            import anthropic
            self.client = anthropic.AsyncAnthropic(
                api_key=config['api_key'],
                base_url=config.get('api_base')
            )
        except ImportError:
            raise ImportError("anthropic package is not installed. Install it with: pip install anthropic")
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Anthropic聊天接口（带重试）"""
        max_retries = 3
        base_delay = 1.0
        
        for attempt in range(max_retries):
            try:
                # 转换消息格式
                system_message = None
                converted_messages = []
                
                for msg in messages:
                    if msg["role"] == "system":
                        system_message = msg["content"]
                    else:
                        converted_messages.append({
                            "role": msg["role"],
                            "content": msg["content"]
                        })
                
                params = {
                    "model": self.config['model'],
                    "messages": converted_messages,
                    "max_tokens": kwargs.get("max_tokens", 4096),
                    **self.config.get('params', {}),
                }
                
                if system_message:
                    params["system"] = system_message
                
                response = await self.client.messages.create(**params)
                return response.content[0].text
                
            except Exception as e:
                error_str = str(e).lower()
                
                if "429" in error_str or "rate limit" in error_str:
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        logger.warning(f"Rate limit exceeded. Retrying after {delay:.1f} seconds...")
                        await asyncio.sleep(delay)
                        continue
                    else:
                        raise ServiceException(message=f"Rate limit exceeded after {max_retries} attempts")
                
                raise


class QwenProvider(LLMProvider):
    """Qwen模型提供商（通过OpenAI兼容API）"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        try:
            import openai
            self.client = openai.AsyncOpenAI(
                api_key=config['api_key'],
                base_url=config.get('api_base') or "https://dashscope.aliyuncs.com/compatible-mode/v1"
            )
        except ImportError:
            raise ImportError("openai package is not installed. Install it with: pip install openai")
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Qwen聊天接口（带重试）"""
        max_retries = 3
        base_delay = 1.0
        
        for attempt in range(max_retries):
            try:
                params = {
                    "model": self.config['model'],
                    "messages": messages,
                    **self.config.get('params', {}),
                    **kwargs
                }
                
                response = await self.client.chat.completions.create(**params)
                return response.choices[0].message.content
                
            except Exception as e:
                error_str = str(e).lower()
                
                if "429" in error_str or "rate limit" in error_str or "请求过于频繁" in error_str:
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        logger.warning(f"Rate limit exceeded. Retrying after {delay:.1f} seconds...")
                        await asyncio.sleep(delay)
                        continue
                    else:
                        raise ServiceException(message=f"Rate limit exceeded after {max_retries} attempts")
                
                raise


def create_llm_provider(config: Dict[str, Any]) -> LLMProvider:
    """创建LLM提供商"""
    provider = ModelProvider(config['provider'])
    
    if provider == ModelProvider.OPENAI:
        return OpenAIProvider(config)
    elif provider == ModelProvider.ANTHROPIC:
        return AnthropicProvider(config)
    elif provider == ModelProvider.QWEN:
        return QwenProvider(config)
    else:
        raise ValueError(f"Unsupported provider: {provider}")


class AiGenerationService:
    """
    AI生成服务类 - 负责调用AI模型生成论文内容
    """

    @classmethod
    async def _get_ai_provider(cls, query_db: AsyncSession, config_id: Optional[int] = None, model_type: str = 'language'):
        """
        获取AI提供商实例
        
        :param query_db: 数据库会话
        :param config_id: 配置ID（可选，不传则使用默认配置）
        :param model_type: 模型类型（language/vision），默认为language
        :return: LLM提供商实例
        """
        # 获取AI模型配置
        if config_id:
            config = await AiModelService.get_config_detail(query_db, config_id)
        else:
            # 根据模型类型获取默认配置
            config = await AiModelService.get_default_config(query_db, model_type)
            
            # 如果没有默认配置，尝试获取第一个启用的配置作为fallback
            if not config:
                # 直接从DAO获取，避免转换问题
                from module_admin.dao.ai_model_dao import AiModelConfigDao
                enabled_configs = await AiModelConfigDao.get_enabled_configs(query_db, model_type)
                if enabled_configs:
                    # 使用第一个启用的配置，直接转换为VO模型
                    from module_admin.entity.vo.ai_model_vo import AiModelConfigModel
                    db_config = enabled_configs[0]
                    # 直接使用from_attributes，不进行字段名转换
                    config = AiModelConfigModel.model_validate(db_config)
                    logger.warning(f'未找到默认{model_type}类型AI模型，使用第一个启用的配置: {config.model_name}')
        
        if not config:
            raise ServiceException(message=f'未配置{model_type}类型的AI模型，请先在AI模型管理中配置并启用')
        
        if config.is_enabled != '1':
            raise ServiceException(message='AI模型未启用，请先启用')
        
        if not config.api_key:
            raise ServiceException(message='AI模型API Key未配置，请先配置')
        
        # 解析参数
        params = {}
        if config.params:
            try:
                params = json.loads(config.params) if isinstance(config.params, str) else config.params
            except:
                params = {}
        
        # 验证必要字段
        if not config.provider and not config.model_code:
            raise ServiceException(message='AI模型提供商未配置，请配置provider或model_code字段')
        
        if not config.model_version:
            raise ServiceException(message='AI模型版本未配置，请配置model_version字段')
        
        # 创建配置字典
        provider_value = config.provider or config.model_code
        # 确保provider值是小写，与ModelProvider枚举匹配
        provider_value = provider_value.lower() if provider_value else None
        
        llm_config = {
            'provider': provider_value,
            'model': config.model_version,
            'api_key': config.api_key,
            'api_base': config.api_endpoint,
            'params': params
        }
        
        # 创建LLM提供商
        try:
            return create_llm_provider(llm_config)
        except ValueError as e:
            logger.error(f"创建LLM提供商失败: {str(e)}, provider={provider_value}, config={llm_config}")
            raise ServiceException(message=f'不支持的AI模型提供商: {provider_value}，支持的提供商: openai, anthropic, qwen')
        except Exception as e:
            logger.error(f"创建LLM提供商时发生错误: {str(e)}, config={llm_config}")
            raise ServiceException(message=f'创建AI模型提供商失败: {str(e)}')

    @classmethod
    async def generate_outline(
        cls,
        query_db: AsyncSession,
        thesis_info: Dict[str, Any],
        config_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        生成论文大纲
        
        :param query_db: 数据库会话
        :param thesis_info: 论文信息（标题、专业、学位级别、研究方向、关键词等）
        :param config_id: AI模型配置ID（可选）
        :return: 大纲内容
        """
        try:
            logger.info(f"开始生成论文大纲，论文标题: {thesis_info.get('title')}, config_id: {config_id}")
            
            # 获取AI提供商
            llm_provider = await cls._get_ai_provider(query_db, config_id)
            logger.info(f"AI提供商创建成功")
            
            # 构建提示词
            prompt = cls._build_outline_prompt(thesis_info)
            logger.debug(f"提示词长度: {len(prompt)}")
            
            # 调用AI生成
            messages = [
                {"role": "system", "content": "你是一位专业的学术论文写作助手，擅长根据论文主题生成结构化的论文大纲。"},
                {"role": "user", "content": prompt}
            ]
            
            logger.info(f"开始调用AI生成大纲...")
            try:
                response = await llm_provider.chat(messages, temperature=0.7, max_tokens=2000)
                logger.info(f"AI响应接收完成，响应长度: {len(response) if response else 0}")
            except Exception as api_error:
                error_msg = str(api_error)
                error_type = type(api_error).__name__
                
                # 记录详细的错误信息
                logger.error(
                    f"AI API调用失败: {error_msg} (类型: {error_type})",
                    exc_info=True
                )
                
                # 根据错误类型提供更友好的错误信息
                if "connection" in error_msg.lower() or "timeout" in error_msg.lower():
                    raise ServiceException(
                        message=f'无法连接到AI服务: {error_msg}。'
                        f'请检查: 1) 网络连接 2) API端点配置 3) 防火墙/代理设置'
                    )
                elif "401" in error_msg or "unauthorized" in error_msg.lower():
                    raise ServiceException(
                        message=f'AI服务认证失败: API Key可能无效或已过期。请检查AI模型配置中的API Key。'
                    )
                elif "429" in error_msg or "rate limit" in error_msg.lower():
                    raise ServiceException(
                        message=f'请求频率过高，请稍后再试。'
                    )
                else:
                    raise ServiceException(message=f'AI服务调用失败: {error_msg}')
            
            # 解析大纲内容
            outline_data = cls._parse_outline_response(response)
            logger.info(f"大纲解析完成，章节数: {len(outline_data.get('chapters', []))}")
            
            return outline_data
            
        except ServiceException as e:
            logger.error(f"生成论文大纲失败（业务异常）: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"生成论文大纲失败（系统异常）: {str(e)}", exc_info=True)
            raise ServiceException(message=f'生成论文大纲失败: {str(e)}')

    @classmethod
    def _build_outline_prompt(cls, thesis_info: Dict[str, Any]) -> str:
        """构建大纲生成提示词"""
        title = thesis_info.get('title', '')
        major = thesis_info.get('major', '')
        degree_level = thesis_info.get('degree_level', '')
        research_direction = thesis_info.get('research_direction', '')
        keywords = thesis_info.get('keywords', '')
        
        degree_map = {
            'bachelor': '本科',
            'master': '硕士',
            'doctor': '博士'
        }
        degree_text = degree_map.get(degree_level, degree_level)
        
        prompt = f"""请为以下论文生成详细的大纲：

论文标题：{title}
专业：{major}
学位级别：{degree_text}
研究方向：{research_direction}
关键词：{keywords}

要求：
1. 生成完整的论文大纲，包括摘要、引言、文献综述、研究方法、研究结果、讨论、结论、参考文献等章节
2. 每个章节需要包含2-4个小节
3. 大纲要符合{degree_text}论文的学术规范
4. 大纲要紧扣论文主题和研究方向
5. 以JSON格式返回，格式如下：
{{
  "title": "论文标题",
  "chapters": [
    {{
      "chapter_number": 1,
      "chapter_title": "章节标题",
      "sections": [
        {{
          "section_number": "1.1",
          "section_title": "小节标题",
          "content_outline": "小节内容概要"
        }}
      ]
    }}
  ]
}}

请直接返回JSON格式的大纲，不要包含其他说明文字。"""
        
        return prompt

    @classmethod
    def _parse_outline_response(cls, response: str) -> Dict[str, Any]:
        """解析AI返回的大纲内容"""
        try:
            # 尝试提取JSON内容
            response = response.strip()
            
            # 移除可能的markdown代码块标记
            if response.startswith('```json'):
                response = response[7:]
            elif response.startswith('```'):
                response = response[3:]
            
            if response.endswith('```'):
                response = response[:-3]
            
            response = response.strip()
            
            # 解析JSON
            outline_data = json.loads(response)
            
            # 验证必要字段
            if 'chapters' not in outline_data:
                raise ValueError('大纲缺少chapters字段')
            
            return outline_data
            
        except json.JSONDecodeError as e:
            logger.error(f"解析大纲JSON失败: {str(e)}, 原始响应: {response}")
            # 如果JSON解析失败，返回原始文本
            return {
                "title": "论文大纲",
                "content": response,
                "chapters": []
            }
        except Exception as e:
            logger.error(f"解析大纲失败: {str(e)}")
            return {
                "title": "论文大纲",
                "content": response,
                "chapters": []
            }

    @classmethod
    async def generate_chapter(
        cls,
        query_db: AsyncSession,
        thesis_info: Dict[str, Any],
        chapter_info: Dict[str, Any],
        outline_context: Optional[str] = None,
        config_id: Optional[int] = None
    ) -> str:
        """
        生成论文章节内容
        
        :param query_db: 数据库会话
        :param thesis_info: 论文信息
        :param chapter_info: 章节信息（章节号、章节标题、小节信息等）
        :param outline_context: 大纲上下文（可选）
        :param config_id: AI模型配置ID（可选）
        :return: 章节内容
        """
        try:
            # 获取AI提供商
            llm_provider = await cls._get_ai_provider(query_db, config_id)
            
            # 构建提示词
            prompt = cls._build_chapter_prompt(thesis_info, chapter_info, outline_context)
            
            # 调用AI生成
            messages = [
                {"role": "system", "content": "你是一位专业的学术论文写作助手，擅长撰写高质量的学术论文章节内容。"},
                {"role": "user", "content": prompt}
            ]
            
            logger.info(f"开始生成章节: {chapter_info.get('chapter_title')}")
            response = await llm_provider.chat(messages, temperature=0.7, max_tokens=4000)
            logger.info(f"章节生成完成")
            
            return response
            
        except ServiceException:
            raise
        except Exception as e:
            logger.error(f"生成章节内容失败: {str(e)}")
            raise ServiceException(message=f'生成章节内容失败: {str(e)}')

    @classmethod
    def _build_chapter_prompt(
        cls,
        thesis_info: Dict[str, Any],
        chapter_info: Dict[str, Any],
        outline_context: Optional[str] = None
    ) -> str:
        """构建章节生成提示词"""
        title = thesis_info.get('title', '')
        major = thesis_info.get('major', '')
        degree_level = thesis_info.get('degree_level', '')
        keywords = thesis_info.get('keywords', '')
        
        chapter_number = chapter_info.get('chapter_number', '')
        chapter_title = chapter_info.get('chapter_title', '')
        sections = chapter_info.get('sections', [])
        
        degree_map = {
            'bachelor': '本科',
            'master': '硕士',
            'doctor': '博士'
        }
        degree_text = degree_map.get(degree_level, degree_level)
        
        prompt = f"""请为以下论文撰写章节内容：

论文标题：{title}
专业：{major}
学位级别：{degree_text}
关键词：{keywords}

章节信息：
第{chapter_number}章 {chapter_title}
"""
        
        if sections:
            prompt += "\n小节结构：\n"
            for section in sections:
                section_number = section.get('section_number', '')
                section_title = section.get('section_title', '')
                content_outline = section.get('content_outline', '')
                prompt += f"{section_number} {section_title}\n"
                if content_outline:
                    prompt += f"  内容概要：{content_outline}\n"
        
        if outline_context:
            prompt += f"\n论文大纲上下文：\n{outline_context}\n"
        
        prompt += f"""
要求：
1. 内容要符合{degree_text}论文的学术规范和写作要求
2. 语言要专业、严谨、逻辑清晰
3. 适当引用相关文献（可以使用[1]、[2]等标记）
4. 内容要充实，每个小节至少500字
5. 保持学术客观性，避免主观臆断
6. 使用Markdown格式，包含适当的标题层级

请直接返回章节内容，不要包含其他说明文字。"""
        
        return prompt

    @classmethod
    async def test_ai_connection(
        cls,
        query_db: AsyncSession,
        config_id: int,
        test_prompt: str = "你好，请简单介绍一下你自己。"
    ) -> Dict[str, Any]:
        """
        测试AI模型连接
        
        :param query_db: 数据库会话
        :param config_id: AI模型配置ID
        :param test_prompt: 测试提示词
        :return: 测试结果
        """
        import time
        start_time = time.time()
        
        try:
            # 获取AI提供商
            llm_provider = await cls._get_ai_provider(query_db, config_id)
            
            # 调用AI
            messages = [
                {"role": "user", "content": test_prompt}
            ]
            
            response = await llm_provider.chat(messages, max_tokens=200)
            
            response_time = time.time() - start_time
            
            return {
                "success": True,
                "response_text": response,
                "response_time": round(response_time, 2)
            }
            
        except Exception as e:
            response_time = time.time() - start_time
            return {
                "success": False,
                "error_message": str(e),
                "response_time": round(response_time, 2)
            }
