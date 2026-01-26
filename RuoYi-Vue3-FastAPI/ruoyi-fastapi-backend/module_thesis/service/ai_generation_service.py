"""
AI生成服务 - 调用AI模型生成论文内容
统一使用 automation-framework 的 AI 模型接口
"""
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions.exception import ServiceException
from module_admin.service.ai_model_service import AiModelService
from utils.log_util import logger

# 确保 automation-framework 在 Python 路径中
automation_framework_src = None
try:
    from mount_automation import AutomationFrameworkPathManager
    automation_path = AutomationFrameworkPathManager.setup_path()
    # AutomationFrameworkPathManager 将 automation-framework 目录添加到路径
    # 所以需要导入 src.ai
    automation_framework_src = automation_path / 'src'
    logger.info(f"已设置 automation-framework 路径: {automation_path}")
except Exception as e:
    logger.warning(f"无法自动设置 automation-framework 路径: {e}")
    # 手动添加路径
    current_file = Path(__file__).resolve()
    automation_framework_path = current_file.parent.parent.parent.parent / 'automation-framework'
    if automation_framework_path.exists():
        automation_framework_src = automation_framework_path / 'src'
        if str(automation_framework_src) not in sys.path:
            sys.path.insert(0, str(automation_framework_src))
            logger.info(f"手动添加 automation-framework/src 到路径: {automation_framework_src}")
    else:
        # 尝试其他可能的路径
        automation_framework_path = current_file.parent.parent.parent / 'automation-framework'
        if automation_framework_path.exists():
            automation_framework_src = automation_framework_path / 'src'
            if str(automation_framework_src) not in sys.path:
                sys.path.insert(0, str(automation_framework_src))
                logger.info(f"手动添加 automation-framework/src 到路径（备用路径）: {automation_framework_src}")

# 导入统一的 AI 接口
# 注意：避免导入整个 ai 模块，只导入需要的函数和类，避免循环导入
try:
    # 首先尝试从 src.ai.llm 和 src.ai.config 直接导入（避免导入 __init__.py 中的 agent）
    try:
        from src.ai.llm import create_llm_provider, LLMProvider
        from src.ai.config import ModelConfig, ModelProvider, model_config_from_db_model
        logger.info("✅ 成功导入 automation-framework 的统一 AI 接口 (from src.ai.llm/config)")
    except ImportError:
        # 如果失败，尝试从 ai.llm 和 ai.config 直接导入
        # 确保 src 目录在路径中
        if automation_framework_src and str(automation_framework_src) not in sys.path:
            sys.path.insert(0, str(automation_framework_src))
            logger.info(f"添加 automation-framework/src 到路径: {automation_framework_src}")
        
        from ai.llm import create_llm_provider, LLMProvider
        from ai.config import ModelConfig, ModelProvider, model_config_from_db_model
        logger.info("✅ 成功导入 automation-framework 的统一 AI 接口 (from ai.llm/config)")
        
except ImportError as e:
    logger.error(f"❌ 无法导入 automation-framework 的 AI 接口: {e}")
    logger.error(f"当前 sys.path 中的相关路径: {[p for p in sys.path if 'automation' in p.lower()]}")
    logger.error(f"automation_framework_src: {automation_framework_src}")
    if automation_framework_src:
        logger.error(f"automation_framework_src 是否存在: {automation_framework_src.exists()}")
        ai_dir = automation_framework_src / 'ai'
        logger.error(f"ai 目录是否存在: {ai_dir.exists() if automation_framework_src.exists() else False}")
        llm_file = automation_framework_src / 'ai' / 'llm.py'
        logger.error(f"llm.py 文件是否存在: {llm_file.exists() if automation_framework_src.exists() else False}")
    logger.error("请确保 automation-framework 在正确的位置，并且路径已配置")
    raise


class AiGenerationService:
    """
    AI生成服务类 - 负责调用AI模型生成论文内容
    """

    @classmethod
    async def _get_ai_provider(cls, query_db: AsyncSession, config_id: Optional[int] = None, model_type: str = 'language'):
        """
        获取AI提供商实例
        
        注意：AI论文生成功能只使用语言模型（language），不使用视觉模型（vision）
        
        :param query_db: 数据库会话
        :param config_id: 配置ID（可选，不传则使用默认配置）
        :param model_type: 模型类型（language=语言模型/vision=视觉模型），默认为language
        :return: (LLM提供商实例, 配置信息) 元组
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
                    
                    # 注意：现在 module_admin 的 DO 模型和 VO 模型都已经有 api_base_url 字段
                    # model_validate 会自动映射 api_base_url 字段，无需特殊处理
                    
                    # 记录信息日志（不是警告），说明使用了fallback逻辑
                    logger.info(
                        f'未找到默认{model_type}类型AI模型（is_default=1），'
                        f'使用第一个启用的配置作为fallback: {config.model_name} (Config ID: {config.config_id})'
                    )
        
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
        
        # 使用统一的 model_config_from_db_model 转换配置
        # model_config_from_db_model 现在支持 model_version 字段
        
        # 确保 provider 字段存在
        provider_value = config.provider or config.model_code
        if not provider_value:
            raise ServiceException(message='AI模型提供商未配置，请配置provider或model_code字段')
        
        # 创建适配对象，确保字段名正确
        # 从 VO 模型获取 api_base_url 和 api_endpoint（现在 VO 模型已经有 api_base_url 字段）
        api_base_url_raw = config.api_base_url if hasattr(config, 'api_base_url') else None
        api_endpoint_raw = config.api_endpoint if hasattr(config, 'api_endpoint') else None
        
        # 处理空字符串：如果值为空字符串，则设为 None
        api_base_url = None
        if api_base_url_raw:
            if isinstance(api_base_url_raw, str):
                api_base_url = api_base_url_raw.strip() if api_base_url_raw.strip() else None
            else:
                api_base_url = api_base_url_raw
        
        api_endpoint = None
        if api_endpoint_raw:
            if isinstance(api_endpoint_raw, str):
                api_endpoint = api_endpoint_raw.strip() if api_endpoint_raw.strip() else None
            else:
                api_endpoint = api_endpoint_raw
        
        # 记录调试信息 - 打印 api_base_url 和 config 对象的所有属性
        logger.info(
            f"配置原始值 - Config ID: {config.config_id}, "
            f"api_base_url 原始值: {repr(api_base_url_raw)}, "
            f"api_base_url 处理后: {repr(api_base_url)}, "
            f"api_endpoint 原始值: {repr(api_endpoint_raw)}, "
            f"api_endpoint 处理后: {repr(api_endpoint)}, "
            f"config 对象类型: {type(config)}, "
            f"config 对象属性: {[attr for attr in dir(config) if not attr.startswith('_') and 'api' in attr.lower()]}"
        )
        
        class ConfigAdapter:
            """配置适配器，将 VO 模型适配为 model_config_from_db_model 期望的格式"""
            def __init__(self, config_obj, api_base_url_val, api_endpoint_val):
                self.provider = (config_obj.provider or config_obj.model_code or '').lower()
                self.model_version = config_obj.model_version  # 使用 model_version
                self.api_key = config_obj.api_key
                self.api_base_url = api_base_url_val  # 使用处理后的值
                self.api_endpoint = api_endpoint_val  # 使用处理后的值
                self.params = params
        
        # 创建适配对象
        config_adapter = ConfigAdapter(config, api_base_url, api_endpoint)
        
        # 使用统一的转换函数
        try:
            model_config = model_config_from_db_model(config_adapter)
            logger.info(
                f"创建AI提供商 - Provider: {model_config.provider.value}, "
                f"Model: {model_config.model}, "
                f"API Base URL: {model_config.api_base or '(使用默认)'}, "
                f"Config ID: {config.config_id}, "
                f"API Key: {'已配置' if model_config.api_key else '未配置'}, "
                f"原始 api_base_url: {repr(api_base_url)}, "
                f"原始 api_endpoint: {repr(api_endpoint)}"
            )
            
            # 如果 API base 为空，记录警告
            if not model_config.api_base:
                logger.warning(
                    f"⚠️  API端点未配置 (Config ID: {config.config_id})，将使用Provider默认端点。"
                    f"如需自定义端点，请在AI模型配置中设置API Base URL。"
                )
            
            # 使用统一的 create_llm_provider 创建提供商
            provider = create_llm_provider(model_config)
            return provider, config
            
        except ValueError as e:
            logger.error(f"创建LLM提供商失败: {str(e)}, provider={provider_value}")
            raise ServiceException(message=f'不支持的AI模型提供商: {provider_value}，支持的提供商: openai, anthropic, qwen')
        except Exception as e:
            logger.error(f"创建LLM提供商时发生错误: {str(e)}", exc_info=True)
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
            
            # 获取AI提供商（返回provider和config）
            llm_provider, config = await cls._get_ai_provider(query_db, config_id)
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
        research_direction = thesis_info.get('research_direction', '')
        keywords = thesis_info.get('keywords', '')
        
        # 学历从模板获取，如果模板中没有则使用默认值
        # 注意：大纲生成时可能还没有选择模板，所以这里使用默认值
        degree_text = '本科'  # 默认值，实际应该从模板获取，但大纲生成时可能还没有模板
        
        prompt = f"""请为以下论文生成详细的大纲：

论文标题：{title}
专业：{major}
学位级别：{degree_text}
研究方向：{research_direction}
关键词：{keywords}

## 内容要求：
1. 生成完整的论文大纲，包括摘要、引言、文献综述、研究方法、研究结果、讨论、结论、参考文献等章节
2. 每个章节需要包含2-4个小节
3. 大纲要符合{degree_text}论文的学术规范
4. 大纲要紧扣论文主题和研究方向

## 格式要求（必须严格遵守）：
**必须返回纯JSON格式，不要包含任何其他文字说明、markdown代码块标记或解释。**

**JSON结构必须严格按照以下格式：**
{{
  "title": "论文标题（字符串）",
  "chapters": [
    {{
      "chapter_number": 1,  // 整数，章节编号，从1开始递增
      "chapter_title": "章节标题（字符串）",
      "sections": [  // 数组，每个章节包含2-4个小节
        {{
          "section_number": "1.1",  // 字符串，小节编号格式：章节号.小节号
          "section_title": "小节标题（字符串）",
          "content_outline": "小节内容概要（字符串，简要描述该小节的主要内容）"
        }}
      ]
    }}
  ]
}}

## 重要约束：
1. **必须返回有效的JSON格式**，可以直接被 `json.loads()` 解析
2. **不要使用markdown代码块**（不要包含 ```json 或 ```）
3. **不要添加任何说明文字**，只返回JSON对象
4. **字段类型必须正确**：
   - `title`: 字符串
   - `chapters`: 数组
   - `chapter_number`: 整数
   - `chapter_title`: 字符串
   - `sections`: 数组
   - `section_number`: 字符串（格式：章节号.小节号，如 "1.1", "2.3"）
   - `section_title`: 字符串
   - `content_outline`: 字符串
5. **所有字符串字段必须使用双引号**，不要使用单引号
6. **确保JSON格式完整**，所有括号和引号正确配对

现在请生成大纲，只返回JSON格式的数据，不要包含任何其他内容。"""
        
        return prompt

    @classmethod
    def _parse_outline_response(cls, response: str) -> Dict[str, Any]:
        """
        解析AI返回的大纲内容
        
        支持多种格式：
        1. 纯JSON格式（推荐）
        2. Markdown代码块格式（```json ... ```）
        3. 包含说明文字的格式（提取JSON部分）
        """
        import re
        
        try:
            # 清理响应内容
            response = response.strip()
            
            # 方法1：尝试直接解析（纯JSON格式）
            try:
                outline_data = json.loads(response)
                # 验证格式
                outline_data = cls._validate_outline_format(outline_data)
                return outline_data
            except json.JSONDecodeError:
                pass
            
            # 方法2：移除markdown代码块标记
            cleaned_response = response
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:].strip()
            elif cleaned_response.startswith('```'):
                cleaned_response = cleaned_response[3:].strip()
            
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3].strip()
            
            # 再次尝试解析
            try:
                outline_data = json.loads(cleaned_response)
                outline_data = cls._validate_outline_format(outline_data)
                return outline_data
            except json.JSONDecodeError:
                pass
            
            # 方法3：使用正则表达式提取JSON对象
            json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            json_matches = re.findall(json_pattern, response, re.DOTALL)
            
            for json_str in json_matches:
                try:
                    outline_data = json.loads(json_str)
                    # 检查是否包含必要字段
                    if 'chapters' in outline_data:
                        outline_data = cls._validate_outline_format(outline_data)
                        return outline_data
                except json.JSONDecodeError:
                    continue
            
            # 如果所有方法都失败，记录错误并返回包装格式
            logger.error(f"解析大纲JSON失败，无法提取有效JSON。原始响应长度: {len(response)}, 前500字符: {response[:500]}")
            return {
                "title": "论文大纲",
                "content": response,
                "chapters": []
            }
            
        except Exception as e:
            logger.error(f"解析大纲失败: {str(e)}, 原始响应长度: {len(response) if response else 0}")
            return {
                "title": "论文大纲",
                "content": response if response else "",
                "chapters": []
            }
    
    @classmethod
    def _validate_outline_format(cls, outline_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证和规范化大纲格式
        
        :param outline_data: 解析后的大纲数据
        :return: 验证和规范化后的大纲数据
        """
        # 确保有 title 字段
        if 'title' not in outline_data:
            outline_data['title'] = '论文大纲'
        
        # 确保有 chapters 字段且是列表
        if 'chapters' not in outline_data:
            outline_data['chapters'] = []
        elif not isinstance(outline_data['chapters'], list):
            logger.warning("大纲chapters字段不是数组，已转换为空数组")
            outline_data['chapters'] = []
        
        # 验证和规范化每个章节
        validated_chapters = []
        for idx, chapter in enumerate(outline_data['chapters']):
            if not isinstance(chapter, dict):
                logger.warning(f"章节 {idx} 不是字典格式，已跳过")
                continue
            
            # 确保必要字段存在
            validated_chapter = {
                'chapter_number': chapter.get('chapter_number', idx + 1),
                'chapter_title': chapter.get('chapter_title', f'章节{idx + 1}'),
                'sections': []
            }
            
            # 验证sections
            sections = chapter.get('sections', [])
            if isinstance(sections, list):
                validated_sections = []
                for sec_idx, section in enumerate(sections):
                    if isinstance(section, dict):
                        validated_section = {
                            'section_number': section.get('section_number', f"{validated_chapter['chapter_number']}.{sec_idx + 1}"),
                            'section_title': section.get('section_title', f'小节{sec_idx + 1}'),
                            'content_outline': section.get('content_outline', '')
                        }
                        validated_sections.append(validated_section)
                validated_chapter['sections'] = validated_sections
            
            validated_chapters.append(validated_chapter)
        
        outline_data['chapters'] = validated_chapters
        return outline_data

    @classmethod
    async def generate_chapter(
        cls,
        query_db: AsyncSession,
        thesis_info: Dict[str, Any],
        chapter_info: Dict[str, Any],
        outline_context: Optional[Union[str, dict]] = None,
        config_id: Optional[int] = None,
        word_count_requirement: Optional[str] = None
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
            llm_provider, _ = await cls._get_ai_provider(query_db, config_id)
            
            # 获取字数要求：根据用户输入的目标总字数和学历（从模板表获取），结合章节数量计算
            if not word_count_requirement:
                word_count_requirement = await cls._calculate_chapter_word_count_requirement(
                    query_db, thesis_info, chapter_info, outline_context
                )
            
            # 构建提示词
            prompt = await cls._build_chapter_prompt(query_db, thesis_info, chapter_info, outline_context, word_count_requirement)
            
            # 调用AI生成
            messages = [
                {"role": "system", "content": "你是一位专业的学术论文写作助手，擅长撰写高质量的学术论文章节内容。"},
                {"role": "user", "content": prompt}
            ]
            
            logger.info(f"开始生成章节: {chapter_info.get('chapter_title')}, 大纲上下文: {'已提供' if outline_context else '未提供'}")
            response = await llm_provider.chat(messages, temperature=0.7, max_tokens=4000)
            logger.info(f"章节生成完成，响应长度: {len(response) if response else 0}")
            
            return response
            
        except ServiceException:
            raise
        except Exception as e:
            logger.error(f"生成章节内容失败: {str(e)}")
            raise ServiceException(message=f'生成章节内容失败: {str(e)}')

    @classmethod
    async def _build_chapter_prompt(
        cls,
        query_db: AsyncSession,
        thesis_info: Dict[str, Any],
        chapter_info: Dict[str, Any],
        outline_context: Optional[Union[str, dict]] = None,
        word_count_requirement: Optional[str] = None
    ) -> str:
        """构建章节生成提示词"""
        import json
        
        title = thesis_info.get('title', '')
        major = thesis_info.get('major', '')
        keywords = thesis_info.get('keywords', '')
        
        chapter_number = chapter_info.get('chapter_number', '')
        chapter_title = chapter_info.get('chapter_title', '')
        sections = chapter_info.get('sections', [])
        
        # 从模板表获取学历（用于显示）
        degree_text = ''
        template_id = thesis_info.get('template_id')
        if template_id:
            try:
                from module_thesis.dao.template_dao import FormatTemplateDao
                template = await FormatTemplateDao.get_template_by_id(query_db, template_id)
                if template and template.degree_level:
                    degree_text = template.degree_level
            except Exception as e:
                logger.debug(f"从模板获取学历失败: {str(e)}")
        
        # 如果模板中没有学历，使用默认值
        if not degree_text:
            degree_text = '本科'  # 默认值
        
        # 如果未提供字数要求，根据目标总字数和学历（从模板表获取）计算
        if not word_count_requirement:
            word_count_requirement = await cls._calculate_chapter_word_count_requirement(
                query_db, thesis_info, chapter_info, outline_context
            )
        
        prompt = f"""请为以下论文撰写章节内容。

## 论文基本信息：
- **论文标题**：{title}
- **专业**：{major}
- **学位级别**：{degree_text}
- **关键词**：{keywords}

## 章节信息：
**第{chapter_number}章 {chapter_title}**
"""
        
        if sections:
            prompt += "\n## 小节结构：\n"
            for idx, section in enumerate(sections, 1):
                section_number = section.get('section_number', f'{chapter_number}.{idx}')
                section_title = section.get('section_title', '')
                content_outline = section.get('content_outline', '')
                prompt += f"\n### {section_number} {section_title}\n"
                if content_outline:
                    prompt += f"**内容概要**：{content_outline}\n"
        
        if outline_context:
            # 如果 outline_context 是字典，转换为 JSON 字符串
            if isinstance(outline_context, dict):
                outline_str = json.dumps(outline_context, ensure_ascii=False, indent=2)
            elif isinstance(outline_context, str):
                outline_str = outline_context
            else:
                outline_str = str(outline_context)
            
            prompt += f"\n## 论文大纲上下文（帮助理解论文整体结构）：\n{outline_str}\n"
        
        prompt += f"""
## 写作要求：

### 1. 学术规范性
- 符合{degree_text}论文的学术规范和写作要求
- 使用学术语言，避免口语化表达
- 保持客观、严谨的学术态度
- 适当引用相关文献（使用[1]、[2]等标记，如：根据研究[1]表明...）

### 2. 内容质量
- **字数要求**：本章节总字数应达到{word_count_requirement}字
- 内容要充实、有深度，不能空洞
- 逻辑清晰，论证充分
- 每个小节至少500字

### 3. 结构要求
- 章节开头要有引言，说明本章的主要内容
- 主体内容要分层次，结构清晰
- 如果有小节，要按照小节结构组织内容
- 章节结尾要有小结或过渡（如适用）

### 4. 格式要求
- 使用Markdown格式
- 使用适当的标题层级（## 表示二级标题，### 表示三级标题）
- 段落之间要有适当的空行
- 重要概念可以加粗（**概念**）

### 5. 内容相关性
- 与论文主题高度相关
- 与大纲结构保持一致
- 与前后章节有逻辑关联
- 关键词要自然融入内容中

## 输出要求（必须严格遵守）：

### 格式要求：
1. **必须使用Markdown格式**
2. **直接返回章节内容**，不要包含以下内容：
   - 不要包含"章节内容："、"以下是章节内容："等说明文字
   - 不要包含章节标题（标题会由系统自动添加）
   - 不要包含章节编号（如"第1章"、"第一章"等）
   - 直接开始写内容即可

### Markdown格式规范：
1. **二级标题**：使用 `## 标题` 表示小节标题（对应大纲中的sections）
   - 如果有小节结构，必须使用 `## 小节标题` 的格式
   - 例如：`## 1.1 研究背景与意义`
2. **三级标题**：使用 `### 标题` 表示更细的层次
3. **加粗文本**：使用 `**文本**` 表示重要概念或关键词
4. **段落**：段落之间用空行分隔
5. **列表**：可以使用 `-` 或 `1.` 表示列表项

### 内容结构要求：
1. **章节开头**：简要介绍本章的主要内容（1-2段）
2. **主体内容**：
   - 如果有小节结构，必须按照大纲中的小节顺序组织内容
   - 每个小节使用 `## 小节标题` 作为二级标题
   - 小节内容要充实，符合字数要求
3. **章节结尾**：适当的小结或过渡（1段）

### 示例格式：
```
本章主要介绍...（章节引言，1-2段）

## 1.1 研究背景与意义

（小节内容，多段文字，符合字数要求）

## 1.2 研究内容与方法

（小节内容，多段文字，符合字数要求）

## 1.3 主要结论

（小节内容，多段文字，符合字数要求）

（章节小结，1段）
```

**重要提示**：
- 如果大纲中提供了小节结构（sections），必须严格按照小节顺序和标题组织内容
- 每个小节必须使用 `## 小节编号 小节标题` 的格式
- 确保内容充实，达到字数要求
- 使用学术语言，保持逻辑清晰

现在请开始撰写章节内容："""
        
        return prompt

    @classmethod
    async def _calculate_chapter_word_count_requirement(
        cls,
        query_db: AsyncSession,
        thesis_info: Dict[str, Any],
        chapter_info: Dict[str, Any],
        outline_context: Optional[Union[str, dict]] = None
    ) -> str:
        """
        根据用户输入的目标总字数和学历（从模板表获取），结合章节数量计算每章节字数要求
        
        :param query_db: 数据库会话
        :param thesis_info: 论文信息（包含total_words和template_id）
        :param chapter_info: 章节信息
        :param outline_context: 大纲上下文（用于计算章节数量）
        :return: 字数要求字符串（如：2000-3000）
        """
        import json
        
        # 获取目标总字数（用户输入的）
        total_words = thesis_info.get('total_words', 0)
        template_id = thesis_info.get('template_id')
        
        # 从模板表获取学历
        degree_text = ''
        if template_id:
            try:
                from module_thesis.dao.template_dao import FormatTemplateDao
                template = await FormatTemplateDao.get_template_by_id(query_db, template_id)
                if template and template.degree_level:
                    degree_text = template.degree_level
            except Exception as e:
                logger.debug(f"从模板获取学历失败: {str(e)}")
        
        # 如果模板中没有学历，使用默认值
        if not degree_text:
            degree_text = '本科'  # 默认值
        
        # 计算章节数量
        chapter_count = 1
        if outline_context:
            try:
                from module_thesis.utils.outline_parser import parse_outline_data, extract_chapters_from_outline
                outline_dict, _ = parse_outline_data(outline_context if isinstance(outline_context, (dict, str)) else str(outline_context))
                chapters_list = extract_chapters_from_outline(outline_dict)
                if chapters_list:
                    chapter_count = len(chapters_list)
            except Exception as e:
                logger.debug(f"解析大纲计算章节数量失败: {str(e)}")
        
        # 如果章节数量为0或1，使用默认值
        if chapter_count <= 1:
            chapter_count = 5  # 默认5章
        
        # 计算每章节平均字数
        if total_words > 0:
            avg_words_per_chapter = total_words // chapter_count
            
            # 根据学历给出合理的范围（±20%）
            variance = int(avg_words_per_chapter * 0.2)
            min_words = max(1000, avg_words_per_chapter - variance)  # 最少1000字
            max_words = avg_words_per_chapter + variance
            
            return f"{min_words}-{max_words}"
        else:
            # 如果没有目标总字数，根据学历使用默认范围
            default_word_count_map = {
                '本科': '2000-3000',
                '硕士': '3000-5000',
                '博士': '5000-8000'
            }
            return default_word_count_map.get(degree_text, '2000-3000')
    
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
            logger.info(f"开始测试AI模型连接 - Config ID: {config_id}, Test Prompt: {test_prompt}")
            
            # 获取AI提供商
            llm_provider, config = await cls._get_ai_provider(query_db, config_id)
            logger.info(f"AI提供商创建成功，开始调用模型...")
            
            # 调用AI
            messages = [
                {"role": "user", "content": test_prompt}
            ]
            
            logger.debug(f"发送测试消息: {test_prompt}")
            response = await llm_provider.chat(messages, max_tokens=200)
            logger.info(f"AI响应接收成功，响应长度: {len(response) if response else 0}")
            
            response_time = time.time() - start_time
            
            result = {
                "success": True,
                "response_text": response,
                "response_time": round(response_time, 2)
            }
            
            logger.info(f"测试成功 - 响应时间: {result['response_time']}秒")
            return result
            
        except Exception as e:
            response_time = time.time() - start_time
            error_msg = str(e)
            error_type = type(e).__name__
            
            logger.error(
                f"AI模型连接测试失败 - Config ID: {config_id}, "
                f"错误类型: {error_type}, 错误信息: {error_msg}",
                exc_info=True
            )
            
            # 根据错误类型提供更友好的错误信息
            if "connection" in error_msg.lower() or "timeout" in error_msg.lower():
                friendly_msg = f"无法连接到AI服务: {error_msg}。请检查: 1) 网络连接 2) API端点配置 3) 防火墙/代理设置"
            elif "401" in error_msg or "unauthorized" in error_msg.lower():
                friendly_msg = "AI服务认证失败: API Key可能无效或已过期。请检查AI模型配置中的API Key。"
            elif "429" in error_msg or "rate limit" in error_msg.lower():
                friendly_msg = "请求频率过高，请稍后再试。"
            else:
                friendly_msg = f"AI服务调用失败: {error_msg}"
            
            return {
                "success": False,
                "error_message": friendly_msg,
                "response_time": round(response_time, 2)
            }
