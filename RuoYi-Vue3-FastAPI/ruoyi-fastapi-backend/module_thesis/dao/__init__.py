"""
论文写作系统DAO层
"""
from module_thesis.dao.ai_model_dao import AiModelConfigDao
from module_thesis.dao.member_dao import (
    MemberPackageDao,
    QuotaRecordDao,
    UserFeatureQuotaDao,
    UserMembershipDao,
)
from module_thesis.dao.order_dao import ExportRecordDao, FeatureServiceDao, OrderDao
from module_thesis.dao.template_dao import FormatTemplateDao, TemplateFormatRuleDao, UniversalInstructionSystemDao
from module_thesis.dao.outline_prompt_template_dao import OutlinePromptTemplateDao
from module_thesis.dao.thesis_dao import ThesisChapterDao, ThesisDao, ThesisOutlineDao, ThesisVersionDao

__all__ = [
    # AI模型相关DAO
    'AiModelConfigDao',
    # 会员相关DAO
    'MemberPackageDao',
    'UserMembershipDao',
    'UserFeatureQuotaDao',
    'QuotaRecordDao',
    # 论文相关DAO
    'ThesisDao',
    'ThesisOutlineDao',
    'ThesisChapterDao',
    'ThesisVersionDao',
    # 模板相关DAO
    'FormatTemplateDao',
    'TemplateFormatRuleDao',
    'UniversalInstructionSystemDao',
    # 大纲提示词模板
    'OutlinePromptTemplateDao',
    # 订单相关DAO
    'OrderDao',
    'FeatureServiceDao',
    'ExportRecordDao',
]

# 支付相关DAO
from module_thesis.dao.payment_config_dao import PaymentConfigDao
from module_thesis.dao.payment_transaction_dao import PaymentTransactionDao

__all__.extend([
    'PaymentConfigDao',
    'PaymentTransactionDao',
])
