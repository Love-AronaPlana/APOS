#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APOS 计算器工具
"""

import math
import re
from typing import Dict, Any
from tools.base_tool import BaseTool
from utils.logger import get_logger

class CalculatorTool(BaseTool):
    """计算器工具"""
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
    
    def execute(self, parameters: Dict[str, Any]) -> Any:
        """执行计算"""
        self.validate_parameters(parameters, ['expression'])
        
        expression = parameters['expression']
        
        self.logger.info(f"🧮 执行计算: {expression}")
        
        try:
            # 安全的数学表达式计算
            result = self._safe_eval(expression)
            
            self.logger.info(f"✅ 计算结果: {result}")
            
            return {
                'expression': expression,
                'result': result,
                'type': type(result).__name__
            }
            
        except Exception as e:
            self.logger.error(f"❌ 计算失败: {str(e)}")
            return {
                'error': f'计算失败: {str(e)}',
                'expression': expression
            }
    
    def _safe_eval(self, expression: str) -> float:
        """安全的表达式计算"""
        # 移除空格
        expression = expression.replace(' ', '')
        
        # 允许的字符和函数
        allowed_chars = set('0123456789+-*/().^')
        allowed_functions = {
            'sin', 'cos', 'tan', 'asin', 'acos', 'atan',
            'log', 'log10', 'exp', 'sqrt', 'abs', 'ceil', 'floor',
            'pi', 'e'
        }
        
        # 检查表达式安全性
        if not all(c in allowed_chars or c.isalpha() for c in expression):
            raise ValueError("表达式包含不允许的字符")
        
        # 替换数学常数
        expression = expression.replace('pi', str(math.pi))
        expression = expression.replace('e', str(math.e))
        
        # 替换 ^ 为 **
        expression = expression.replace('^', '**')
        
        # 替换数学函数
        for func in allowed_functions:
            if func in ['pi', 'e']:
                continue
            expression = re.sub(f'\\b{func}\\b', f'math.{func}', expression)
        
        # 创建安全的命名空间
        safe_dict = {
            "__builtins__": {},
            "math": math
        }
        
        # 计算结果
        result = eval(expression, safe_dict)
        
        return result
    
    def get_description(self) -> str:
        """获取工具描述"""
        return "执行数学计算，支持基本运算和常用数学函数"
    
    def get_parameters(self) -> Dict[str, Any]:
        """获取工具参数定义"""
        return {
            'expression': {
                'type': 'string',
                'description': '数学表达式，支持 +, -, *, /, ^, sin, cos, tan, log, sqrt 等',
                'required': True,
                'examples': ['2 + 3 * 4', 'sin(pi/2)', 'sqrt(16)', 'log(10)']
            }
        }

