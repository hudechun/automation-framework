"""
论文写作系统Controller层
"""
from module_thesis.controller.ai_model_controller import ai_model_controller
from module_thesis.controller.member_controller import member_controller
from module_thesis.controller.order_controller import order_controller
from module_thesis.controller.outline_prompt_template_controller import outline_prompt_template_controller
from module_thesis.controller.template_controller import template_controller
from module_thesis.controller.thesis_controller import thesis_controller

__all__ = [
    'ai_model_controller',
    'member_controller',
    'thesis_controller',
    'template_controller',
    'order_controller',
    'outline_prompt_template_controller',
]
