"""資料存取層基礎抽象類別

此模組定義資料倉儲 (Repository) 的抽象介面，
所有具體的資料存取實作都應該繼承這個基礎類別。
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Generic, TypeVar, Dict, Any

T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """資料倉儲基礎抽象類別
    
    提供 CRUD 操作的標準介面。
    所有具體的 Repository 都應該實作這些方法。
    
    Type Parameters:
        T: 資料模型型別
    """
    
    @abstractmethod
    def get_all(self) -> List[T]:
        """取得所有資料
        
        Returns:
            資料列表
            
        Raises:
            DatabaseConnectionError: 資料庫連線失敗
        """
        pass
    
    @abstractmethod
    def get_by_id(self, id: str) -> Optional[T]:
        """依 ID 取得單筆資料
        
        Args:
            id: 資料 ID
            
        Returns:
            資料物件，如果不存在則回傳 None
            
        Raises:
            DatabaseConnectionError: 資料庫連線失敗
        """
        pass
    
    @abstractmethod
    def create(self, entity: T) -> bool:
        """新增資料
        
        Args:
            entity: 資料物件
            
        Returns:
            True 如果成功，否則 False
            
        Raises:
            DatabaseConnectionError: 資料庫連線失敗
            ValidationError: 資料驗證失敗
        """
        pass
    
    @abstractmethod
    def update(self, entity: T) -> bool:
        """更新資料
        
        Args:
            entity: 資料物件
            
        Returns:
            True 如果成功，否則 False
            
        Raises:
            DatabaseConnectionError: 資料庫連線失敗
            RecordNotFoundError: 找不到要更新的資料
            ValidationError: 資料驗證失敗
        """
        pass
    
    @abstractmethod
    def delete(self, id: str) -> bool:
        """刪除資料
        
        Args:
            id: 資料 ID
            
        Returns:
            True 如果成功，否則 False
            
        Raises:
            DatabaseConnectionError: 資料庫連線失敗
            RecordNotFoundError: 找不到要刪除的資料
        """
        pass
    
    @abstractmethod
    def find_by_criteria(self, **kwargs) -> List[T]:
        """依條件查詢資料
        
        Args:
            **kwargs: 查詢條件
            
        Returns:
            符合條件的資料列表
            
        Raises:
            DatabaseConnectionError: 資料庫連線失敗
        """
        pass
