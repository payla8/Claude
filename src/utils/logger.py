"""Advanced logging system for the trading bot"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


class TradingLogger:
    """Custom logger for trading bot with file and console output"""

    def __init__(self, name: str, log_dir: str = "logs"):
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # Remove existing handlers
        self.logger.handlers.clear()

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)

        # File handler - daily logs
        log_file = self.log_dir / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        self.logger.addHandler(file_handler)

        # Trade-specific log
        trade_log_file = self.log_dir / f"trades_{datetime.now().strftime('%Y%m%d')}.log"
        self.trade_handler = logging.FileHandler(trade_log_file)
        self.trade_handler.setLevel(logging.INFO)

    def get_logger(self):
        return self.logger


def get_logger(name: str) -> logging.Logger:
    """Get or create a logger"""
    trading_logger = TradingLogger(name)
    return trading_logger.get_logger()
