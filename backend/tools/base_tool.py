#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APOS 工具基类
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseTool(ABC):
    """工具基类"""
    
    def __init__(self):
        self.name = self.__class__.__name__.replace('Tool', '').lower()
    
    @abstractmethod
    def execute(self, parameters: Dict[str, Any]) -> Any:
        """执行工具"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """获取工具描述"""
        pass
    
    def get_parameters(self) -> Dict[str, Any]:
        """获取工具参数定义"""
        return {}
    
    def validate_parameters(self, parameters: Dict[str, Any], required: list = None) -> bool:
        """验证参数"""
        if required:
            for param in required:
                if param not in parameters:
                    raise ValueError(f"缺少必需参数: {param}")
        return True

