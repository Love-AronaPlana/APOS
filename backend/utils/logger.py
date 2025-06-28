#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APOS 日志工具
"""

import logging
import sys
import os
import re
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
    
    # 创建日志目录
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # 生成日志文件名 (年月日时分秒)
    log_filename = datetime.now().strftime("%Y%m%d%H%M%S") + ".log"
    log_filepath = os.path.join(log_dir, log_filename)
    
    # 创建文件处理器
    file_handler = logging.FileHandler(log_filepath, encoding='utf-8')
    
    # 根据DEBUG设置文件日志级别
    if Config.DEBUG:
        file_handler.setLevel(logging.DEBUG)
    else:
        file_handler.setLevel(getattr(logging, Config.LOG_LEVEL))
    
    # 设置文件日志格式 (无颜色)
    class FileFormatter(logging.Formatter):
        """文件日志格式化器，移除ANSI转义序列"""
        ANSI_ESCAPE_PATTERN = re.compile(r'\x1b\[[0-9;]*[mK]')

        def format(self, record):
            message = super().format(record)
            return self.ANSI_ESCAPE_PATTERN.sub('', message)

    file_formatter = FileFormatter(
        '%(asctime)s | %(levelname)s | %(name)s | %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    
    # 添加文件处理器
    logger.addHandler(file_handler)

def get_logger(name):
    """获取日志器"""
    return logging.getLogger(name)

