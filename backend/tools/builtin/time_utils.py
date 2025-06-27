#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APOS 时间工具
"""

from datetime import datetime, timedelta
import pytz
from typing import Dict, Any
from tools.base_tool import BaseTool
from utils.logger import get_logger

class TimeUtilsTool(BaseTool):
    """时间工具"""
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
    
    def execute(self, parameters: Dict[str, Any]) -> Any:
        """执行时间操作"""
        self.validate_parameters(parameters, ['operation'])
        
        operation = parameters['operation']
        
        self.logger.info(f"⏰ 执行时间操作: {operation}")
        
        try:
            if operation == 'current_time':
                return self._get_current_time(parameters)
            elif operation == 'format_time':
                return self._format_time(parameters)
            elif operation == 'time_diff':
                return self._calculate_time_diff(parameters)
            elif operation == 'add_time':
                return self._add_time(parameters)
            elif operation == 'timezone_convert':
                return self._convert_timezone(parameters)
            else:
                raise ValueError(f"不支持的操作: {operation}")
                
        except Exception as e:
            self.logger.error(f"❌ 时间操作失败: {str(e)}")
            return {
                'error': f'时间操作失败: {str(e)}',
                'operation': operation
            }
    
    def _get_current_time(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """获取当前时间"""
        timezone = parameters.get('timezone', 'Asia/Shanghai')
        
        try:
            tz = pytz.timezone(timezone)
            current_time = datetime.now(tz)
        except:
            # 如果时区无效，使用本地时间
            current_time = datetime.now()
        
        return {
            'operation': 'current_time',
            'datetime': current_time.isoformat(),
            'timestamp': current_time.timestamp(),
            'timezone': timezone,
            'formatted': current_time.strftime('%Y-%m-%d %H:%M:%S'),
            'date': current_time.strftime('%Y-%m-%d'),
            'time': current_time.strftime('%H:%M:%S'),
            'weekday': current_time.strftime('%A'),
            'weekday_cn': ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][current_time.weekday()]
        }
    
    def _format_time(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """格式化时间"""
        self.validate_parameters(parameters, ['datetime'])
        
        datetime_str = parameters['datetime']
        format_str = parameters.get('format', '%Y-%m-%d %H:%M:%S')
        
        # 尝试解析时间
        try:
            dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        except:
            dt = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
        
        formatted = dt.strftime(format_str)
        
        return {
            'operation': 'format_time',
            'original': datetime_str,
            'formatted': formatted,
            'format': format_str
        }
    
    def _calculate_time_diff(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """计算时间差"""
        self.validate_parameters(parameters, ['start_time', 'end_time'])
        
        start_str = parameters['start_time']
        end_str = parameters['end_time']
        
        # 解析时间
        try:
            start_dt = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
        except:
            start_dt = datetime.strptime(start_str, '%Y-%m-%d %H:%M:%S')
        
        try:
            end_dt = datetime.fromisoformat(end_str.replace('Z', '+00:00'))
        except:
            end_dt = datetime.strptime(end_str, '%Y-%m-%d %H:%M:%S')
        
        diff = end_dt - start_dt
        
        return {
            'operation': 'time_diff',
            'start_time': start_str,
            'end_time': end_str,
            'difference': {
                'total_seconds': diff.total_seconds(),
                'days': diff.days,
                'hours': diff.seconds // 3600,
                'minutes': (diff.seconds % 3600) // 60,
                'seconds': diff.seconds % 60
            },
            'human_readable': str(diff)
        }
    
    def _add_time(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """时间加减"""
        self.validate_parameters(parameters, ['datetime'])
        
        datetime_str = parameters['datetime']
        days = parameters.get('days', 0)
        hours = parameters.get('hours', 0)
        minutes = parameters.get('minutes', 0)
        seconds = parameters.get('seconds', 0)
        
        # 解析时间
        try:
            dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        except:
            dt = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
        
        # 添加时间
        new_dt = dt + timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
        
        return {
            'operation': 'add_time',
            'original': datetime_str,
            'added': {
                'days': days,
                'hours': hours,
                'minutes': minutes,
                'seconds': seconds
            },
            'result': new_dt.isoformat(),
            'formatted': new_dt.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _convert_timezone(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """时区转换"""
        self.validate_parameters(parameters, ['datetime', 'from_timezone', 'to_timezone'])
        
        datetime_str = parameters['datetime']
        from_tz = parameters['from_timezone']
        to_tz = parameters['to_timezone']
        
        # 解析时间和时区
        from_timezone = pytz.timezone(from_tz)
        to_timezone = pytz.timezone(to_tz)
        
        # 如果输入时间没有时区信息，假设它是 from_timezone 的时间
        try:
            dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            if dt.tzinfo is None:
                dt = from_timezone.localize(dt)
        except:
            dt = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
            dt = from_timezone.localize(dt)
        
        # 转换时区
        converted_dt = dt.astimezone(to_timezone)
        
        return {
            'operation': 'timezone_convert',
            'original': datetime_str,
            'from_timezone': from_tz,
            'to_timezone': to_tz,
            'result': converted_dt.isoformat(),
            'formatted': converted_dt.strftime('%Y-%m-%d %H:%M:%S %Z')
        }
    
    def get_description(self) -> str:
        """获取工具描述"""
        return "时间相关操作，包括获取当前时间、格式化时间、计算时间差、时间加减、时区转换等"
    
    def get_parameters(self) -> Dict[str, Any]:
        """获取工具参数定义"""
        return {
            'operation': {
                'type': 'string',
                'description': '操作类型: current_time, format_time, time_diff, add_time, timezone_convert',
                'required': True
            },
            'datetime': {
                'type': 'string',
                'description': '时间字符串 (ISO格式或 YYYY-MM-DD HH:MM:SS)',
                'required': False
            },
            'timezone': {
                'type': 'string',
                'description': '时区名称，如 Asia/Shanghai, UTC, America/New_York',
                'default': 'Asia/Shanghai',
                'required': False
            },
            'format': {
                'type': 'string',
                'description': '时间格式字符串',
                'default': '%Y-%m-%d %H:%M:%S',
                'required': False
            }
        }

