"""
AI论文写作系统 - 数据库实体类（DO）
"""

# 会员管理相关实体
from .member_do import (
    AiWriteMemberPackage,
    AiWriteUserMembership,
    AiWriteUserFeatureQuota,
    AiWriteQuotaRecord,
)

# 论文管理相关实体
from .thesis_do import (
    AiWriteThesis,
    AiWriteThesisOutline,
    AiWriteThesisChapter,
    AiWriteThesisVersion,
)

# 格式模板相关实体
from .template_do import (
    AiWriteFormatTemplate,
    AiWriteTemplateFormatRule,
)

# 大纲提示词模板相关实体
from .outline_prompt_template_do import AiWriteOutlinePromptTemplate

# 订单和支付相关实体
from .order_do import (
    AiWriteOrder,
    AiWriteFeatureService,
    AiWriteExportRecord,
)

__all__ = [
    # 会员管理
    'AiWriteMemberPackage',
    'AiWriteUserMembership',
    'AiWriteUserFeatureQuota',
    'AiWriteQuotaRecord',
    # 论文管理
    'AiWriteThesis',
    'AiWriteThesisOutline',
    'AiWriteThesisChapter',
    'AiWriteThesisVersion',
    # 格式模板
    'AiWriteFormatTemplate',
    'AiWriteTemplateFormatRule',
    # 大纲提示词模板
    'AiWriteOutlinePromptTemplate',
    # 订单支付
    'AiWriteOrder',
    'AiWriteFeatureService',
    'AiWriteExportRecord',
]
