"""使用者資料模型

此模組定義使用者的領域模型。
"""
from dataclasses import dataclass
from typing import Dict, Any

from src.config.constants import UserRole, FieldNames


@dataclass
class User:
    """使用者資料模型
    
    Attributes:
        username: 使用者帳號
        password: 密碼 (雜湊後)
        display_name: 顯示名稱
        role: 使用者角色
    """
    username: str
    password: str
    display_name: str
    role: UserRole
    
    @classmethod
    def from_sheet_row(cls, row: Dict[str, Any]) -> 'User':
        """從 Google Sheets 列資料建立 User 物件
        
        Args:
            row: Sheet 列資料
            
        Returns:
            User 物件
            
        Raises:
            ValueError: 當資料格式不正確時
        """
        try:
            return cls(
                username=row[FieldNames.USERNAME],
                password=row[FieldNames.PASSWORD],
                display_name=row[FieldNames.DISPLAY_NAME],
                role=UserRole(row[FieldNames.ROLE])
            )
        except (KeyError, ValueError) as e:
            raise ValueError(f"無法解析使用者資料: {str(e)}")
    
    def to_sheet_row(self) -> Dict[str, str]:
        """轉換為 Google Sheets 列資料
        
        Returns:
            dict 格式的列資料
        """
        return {
            FieldNames.USERNAME: self.username,
            FieldNames.PASSWORD: self.password,
            FieldNames.DISPLAY_NAME: self.display_name,
            FieldNames.ROLE: self.role.value
        }
    
    def is_admin(self) -> bool:
        """判斷是否為管理員
        
        Returns:
            True 如果是管理員，否則 False
        """
        return self.role == UserRole.ADMIN
    
    def to_dict(self) -> Dict[str, str]:
        """轉換為字典 (用於 session state)
        
        Returns:
            字典格式，不包含密碼
        """
        return {
            'username': self.username,
            'display_name': self.display_name,
            'role': self.role.value
        }
    
    def __repr__(self) -> str:
        """字串表示"""
        return f"User(username='{self.username}', role={self.role.value})"
