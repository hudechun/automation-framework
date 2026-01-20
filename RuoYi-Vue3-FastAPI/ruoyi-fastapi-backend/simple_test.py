# -*- coding: utf-8 -*-
import sys
import os
import traceback

# 设置UTF-8编码
os.environ['PYTHONIOENCODING'] = 'utf-8'

print("=== Testing config_controller import ===")
try:
    from module_automation.controller import config_controller
    print("SUCCESS: Import successful!")
    print(f"Route prefix: {config_controller.config_controller.prefix}")
except Exception as e:
    print("FAILED: Import failed!")
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
