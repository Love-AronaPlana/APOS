#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APOS 日志工具
"""

import logging
import sys
from datetime import datetime
from config.settings import Config

class ColoredFormatter(logging.Formatter):
    """彩色日志格式化器"""
    
    # 颜色代码
    COLORS = {
        'DEBUG': '\033[36m',    # 青色
        'INFO': '\033[32m',     # 绿色
        'WARNING': '\033[33m',  # 黄色
        'ERROR': '\033[31m',    # 红色
        'CRITICAL': '\033[35m', # 紫色
    }
    RESET = '\033[0m'
    
    def format(self, record):
        # 添加颜色
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        
        # 格式化时间
        record.asctime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return super().format(record)

def setup_logger():
    """设置日志配置"""
    
    # 创建根日志器
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, Config.LOG_LEVEL))
    
    # 清除现有处理器
    logger.handlers.clear()
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, Config.LOG_LEVEL))
    
    # 设置格式
    formatter = ColoredFormatter(
        '%(asctime)s | %(levelname)s | %(name)s | %(message)s'
    )
    console_handler.setFormatter(formatter)
    
    # 添加处理器
    logger.addHandler(console_handler)
    
    print("📝 日志系统初始化完成")

def get_logger(name):
    """获取日志器"""
    return logging.getLogger(name)

