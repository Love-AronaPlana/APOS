#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APOS 文件操作工具
"""

import os
from typing import Dict, Any
from tools.base_tool import BaseTool
from utils.logger import get_logger

class FileOperationsTool(BaseTool):
    """文件操作工具"""
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
    
    def execute(self, parameters: Dict[str, Any]) -> Any:
        """执行文件操作"""
        self.validate_parameters(parameters, ['operation'])
        
        operation = parameters['operation']
        
        self.logger.info(f"📁 执行文件操作: {operation}")
        
        try:
            if operation == 'read':
                return self._read_file(parameters)
            elif operation == 'write':
                return self._write_file(parameters)
            elif operation == 'list':
                return self._list_directory(parameters)
            elif operation == 'exists':
                return self._check_exists(parameters)
            else:
                raise ValueError(f"不支持的操作: {operation}")
                
        except Exception as e:
            self.logger.error(f"❌ 文件操作失败: {str(e)}")
            return {
                'error': f'文件操作失败: {str(e)}',
                'operation': operation
            }
    
    def _read_file(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """读取文件"""
        self.validate_parameters(parameters, ['path'])
        
        file_path = parameters['path']
        encoding = parameters.get('encoding', 'utf-8')
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        with open(file_path, 'r', encoding=encoding) as f:
            content = f.read()
        
        return {
            'operation': 'read',
            'path': file_path,
            'content': content,
            'size': len(content)
        }
    
    def _write_file(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """写入文件"""
        self.validate_parameters(parameters, ['path', 'content'])
        
        file_path = parameters['path']
        content = parameters['content']
        encoding = parameters.get('encoding', 'utf-8')
        mode = parameters.get('mode', 'w')  # 'w' 或 'a'
        
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, mode, encoding=encoding) as f:
            f.write(content)
        
        return {
            'operation': 'write',
            'path': file_path,
            'size': len(content),
            'mode': mode
        }
    
    def _list_directory(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """列出目录内容"""
        self.validate_parameters(parameters, ['path'])
        
        dir_path = parameters['path']
        
        if not os.path.exists(dir_path):
            raise FileNotFoundError(f"目录不存在: {dir_path}")
        
        if not os.path.isdir(dir_path):
            raise ValueError(f"路径不是目录: {dir_path}")
        
        items = []
        for item in os.listdir(dir_path):
            item_path = os.path.join(dir_path, item)
            items.append({
                'name': item,
                'path': item_path,
                'type': 'directory' if os.path.isdir(item_path) else 'file',
                'size': os.path.getsize(item_path) if os.path.isfile(item_path) else None
            })
        
        return {
            'operation': 'list',
            'path': dir_path,
            'items': items,
            'count': len(items)
        }
    
    def _check_exists(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """检查文件/目录是否存在"""
        self.validate_parameters(parameters, ['path'])
        
        path = parameters['path']
        exists = os.path.exists(path)
        
        result = {
            'operation': 'exists',
            'path': path,
            'exists': exists
        }
        
        if exists:
            result['type'] = 'directory' if os.path.isdir(path) else 'file'
            if os.path.isfile(path):
                result['size'] = os.path.getsize(path)
        
        return result
    
    def get_description(self) -> str:
        """获取工具描述"""
        return "执行文件和目录操作，包括读取、写入、列出目录内容等"
    
    def get_parameters(self) -> Dict[str, Any]:
        """获取工具参数定义"""
        return {
            'operation': {
                'type': 'string',
                'description': '操作类型: read, write, list, exists',
                'required': True
            },
            'path': {
                'type': 'string',
                'description': '文件或目录路径',
                'required': True
            },
            'content': {
                'type': 'string',
                'description': '写入的内容（仅用于 write 操作）',
                'required': False
            },
            'encoding': {
                'type': 'string',
                'description': '文件编码',
                'default': 'utf-8',
                'required': False
            },
            'mode': {
                'type': 'string',
                'description': '写入模式: w (覆盖) 或 a (追加)',
                'default': 'w',
                'required': False
            }
        }

