#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APOS 天气工具
"""

import requests
from typing import Dict, Any
from tools.base_tool import BaseTool
from utils.logger import get_logger

class WeatherTool(BaseTool):
    """天气工具"""
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
    
    def execute(self, parameters: Dict[str, Any]) -> Any:
        """获取天气信息"""
        self.validate_parameters(parameters, ['location'])
        
        location = parameters['location']
        
        self.logger.info(f"🌤️ 获取天气信息: {location}")
        
        try:
            # 这里使用模拟数据，实际使用时可以接入真实的天气 API
            # 如 OpenWeatherMap、和风天气等
            
            weather_data = {
                'location': location,
                'temperature': 22,
                'humidity': 65,
                'weather': '晴天',
                'wind_speed': 5.2,
                'wind_direction': '东南风',
                'pressure': 1013,
                'visibility': 10,
                'uv_index': 6,
                'forecast': [
                    {
                        'date': '今天',
                        'weather': '晴天',
                        'high': 25,
                        'low': 18
                    },
                    {
                        'date': '明天',
                        'weather': '多云',
                        'high': 23,
                        'low': 16
                    },
                    {
                        'date': '后天',
                        'weather': '小雨',
                        'high': 20,
                        'low': 14
                    }
                ]
            }
            
            self.logger.info(f"✅ 获取天气信息成功: {location}")
            
            return weather_data
            
        except Exception as e:
            self.logger.error(f"❌ 获取天气信息失败: {str(e)}")
            return {
                'error': f'获取天气信息失败: {str(e)}',
                'location': location
            }
    
    def get_description(self) -> str:
        """获取工具描述"""
        return "获取指定地点的天气信息，包括当前天气和未来几天的预报"
    
    def get_parameters(self) -> Dict[str, Any]:
        """获取工具参数定义"""
        return {
            'location': {
                'type': 'string',
                'description': '地点名称，如城市名或地区名',
                'required': True,
                'examples': ['北京', '上海', '广州', 'Beijing', 'Shanghai']
            }
        }

