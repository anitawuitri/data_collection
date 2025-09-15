"""抽象數據收集器基礎類

定義所有數據收集器的共同介面和行為。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BaseCollector(ABC):
    """抽象數據收集器"""
    
    def __init__(self, config: Any):
        """初始化收集器
        
        Args:
            config: 配置物件
        """
        self.config = config
        self.logger = logger
    
    @abstractmethod
    async def collect(self, start_time: datetime, end_time: datetime, **kwargs) -> Dict[str, Any]:
        """收集數據
        
        Args:
            start_time: 開始時間
            end_time: 結束時間
            **kwargs: 額外參數
            
        Returns:
            收集到的數據字典
            
        Raises:
            CollectionError: 數據收集失敗時拋出
        """
        pass
    
    @abstractmethod
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """驗證數據格式和完整性
        
        Args:
            data: 要驗證的數據
            
        Returns:
            驗證結果
        """
        pass
    
    def handle_error(self, error: Exception, context: str = "") -> None:
        """統一錯誤處理
        
        Args:
            error: 異常物件
            context: 錯誤上下文資訊
        """
        error_msg = f"{self.__class__.__name__} 錯誤"
        if context:
            error_msg += f" [{context}]"
        error_msg += f": {str(error)}"
        
        self.logger.error(error_msg)
    
    def log_collection_start(self, target: str) -> None:
        """記錄收集開始"""
        self.logger.info(f"開始收集 {target} 的數據...")
    
    def log_collection_success(self, target: str, record_count: int = 0) -> None:
        """記錄收集成功"""
        msg = f"成功收集 {target} 的數據"
        if record_count > 0:
            msg += f"，共 {record_count} 筆記錄"
        self.logger.info(msg)
    
    def log_collection_failure(self, target: str, error: str) -> None:
        """記錄收集失敗"""
        self.logger.error(f"收集 {target} 數據失敗: {error}")


class CollectionError(Exception):
    """數據收集異常"""
    
    def __init__(self, message: str, collector_type: str = None, target: str = None):
        self.message = message
        self.collector_type = collector_type
        self.target = target
        
        full_message = message
        if collector_type:
            full_message = f"[{collector_type}] {full_message}"
        if target:
            full_message = f"{full_message} (目標: {target})"
            
        super().__init__(full_message)