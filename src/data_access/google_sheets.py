"""Google Sheets 資料存取層

此模組實作與 Google Sheets 的所有互動邏輯。
"""
from typing import List, Optional, Dict, Any
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

from src.models.document import Document
from src.models.user import User
from src.data_access.base import BaseRepository
from src.config.settings import GoogleSheetsConfig
from src.config.constants import FieldNames
from src.utils.exceptions import (
    DatabaseConnectionError,
    RecordNotFoundError,
    ValidationError
)


class GoogleSheetsConnection:
    """Google Sheets 連線管理器"""
    
    def __init__(self, credentials: Dict[str, Any]):
        """初始化連線
        
        Args:
            credentials: GCP 服務帳號憑證
        """
        self.credentials = credentials
        self._client = None
    
    def get_client(self) -> gspread.Client:
        """取得 Google Sheets 客戶端
        
        Returns:
            gspread.Client 物件
            
        Raises:
            DatabaseConnectionError: 連線失敗
        """
        if self._client is None:
            try:
                scope = [
                    'https://spreadsheets.google.com/feeds',
                    'https://www.googleapis.com/auth/drive'
                ]
                creds = ServiceAccountCredentials.from_json_keyfile_dict(
                    self.credentials,
                    scope
                )
                self._client = gspread.authorize(creds)
            except Exception as e:
                raise DatabaseConnectionError(f"無法連接到 Google Sheets: {str(e)}")
        
        return self._client


class DocumentRepository(BaseRepository[Document]):
    """公文資料倉儲
    
    負責所有公文資料的 CRUD 操作。
    """
    
    def __init__(self, config: GoogleSheetsConfig, credentials: Dict[str, Any]):
        """初始化
        
        Args:
            config: Google Sheets 設定
            credentials: GCP 服務帳號憑證
        """
        self.config = config
        self.connection = GoogleSheetsConnection(credentials)
        self._worksheet = None
        self._connect()
    
    def _connect(self) -> None:
        """連接到 Google Sheets"""
        try:
            client = self.connection.get_client()
            sheet = client.open_by_url(self.config.sheet_url)
            self._worksheet = sheet.worksheet(self.config.docs_worksheet)
        except Exception as e:
            raise DatabaseConnectionError(f"無法連接到公文工作表: {str(e)}")
    
    def get_all(self) -> List[Document]:
        """取得所有公文
        
        Returns:
            公文列表
            
        Raises:
            DatabaseConnectionError: 讀取失敗
        """
        try:
            records = self._worksheet.get_all_records()
            
            if not records:
                return []
            
            df = pd.DataFrame(records)
            documents = []
            
            for _, row in df.iterrows():
                try:
                    doc = Document.from_sheet_row(row.to_dict())
                    documents.append(doc)
                except ValueError as e:
                    # 跳過無效的列
                    print(f"警告: 跳過無效的列資料: {str(e)}")
                    continue
            
            return documents
            
        except Exception as e:
            raise DatabaseConnectionError(f"讀取公文資料失敗: {str(e)}")
    
    def get_by_id(self, doc_id: str) -> Optional[Document]:
        """依 ID 取得公文
        
        Args:
            doc_id: 公文字號
            
        Returns:
            Document 物件，如果不存在則回傳 None
            
        Raises:
            DatabaseConnectionError: 查詢失敗
        """
        try:
            cell = self._worksheet.find(doc_id)
            if not cell:
                return None
            
            row_data = self._worksheet.row_values(cell.row)
            headers = self._worksheet.row_values(1)
            row_dict = dict(zip(headers, row_data))
            
            return Document.from_sheet_row(row_dict)
            
        except ValueError:
            return None
        except Exception as e:
            raise DatabaseConnectionError(f"查詢公文失敗: {str(e)}")
    
    def create(self, document: Document) -> bool:
        """新增公文
        
        Args:
            document: Document 物件
            
        Returns:
            True 如果成功
            
        Raises:
            DatabaseConnectionError: 新增失敗
            ValidationError: 資料驗證失敗
        """
        try:
            # 檢查是否已存在
            existing = self.get_by_id(document.id)
            if existing:
                raise ValidationError(f"公文字號已存在: {document.id}")
            
            # 轉換為列資料
            row_data = document.to_sheet_row()
            
            # 確保欄位順序正確
            headers = self._worksheet.row_values(1)
            values = [row_data.get(header, '') for header in headers]
            
            # 新增到 Sheet
            self._worksheet.append_row(values)
            return True
            
        except ValidationError:
            raise
        except Exception as e:
            raise DatabaseConnectionError(f"新增公文失敗: {str(e)}")
    
    def update(self, document: Document) -> bool:
        """更新公文
        
        Args:
            document: Document 物件
            
        Returns:
            True 如果成功
            
        Raises:
            DatabaseConnectionError: 更新失敗
            RecordNotFoundError: 找不到公文
        """
        try:
            cell = self._worksheet.find(document.id)
            if not cell:
                raise RecordNotFoundError(f"找不到公文: {document.id}")
            
            # 轉換為列資料
            row_data = document.to_sheet_row()
            
            # 確保欄位順序正確
            headers = self._worksheet.row_values(1)
            values = [row_data.get(header, '') for header in headers]
            
            # 更新列
            range_notation = f'A{cell.row}:{chr(65 + len(headers) - 1)}{cell.row}'
            self._worksheet.update(range_notation, [values])
            
            return True
            
        except RecordNotFoundError:
            raise
        except Exception as e:
            raise DatabaseConnectionError(f"更新公文失敗: {str(e)}")
    
    def delete(self, doc_id: str) -> bool:
        """刪除公文
        
        Args:
            doc_id: 公文字號
            
        Returns:
            True 如果成功
            
        Raises:
            DatabaseConnectionError: 刪除失敗
            RecordNotFoundError: 找不到公文
        """
        try:
            cell = self._worksheet.find(doc_id)
            if not cell:
                raise RecordNotFoundError(f"找不到公文: {doc_id}")
            
            self._worksheet.delete_rows(cell.row)
            return True
            
        except RecordNotFoundError:
            raise
        except Exception as e:
            raise DatabaseConnectionError(f"刪除公文失敗: {str(e)}")
    
    def find_by_criteria(self, **kwargs) -> List[Document]:
        """依條件查詢公文
        
        Args:
            **kwargs: 查詢條件 (例如 type='發文', agency='教育部')
            
        Returns:
            符合條件的公文列表
        """
        all_docs = self.get_all()
        
        # 動態篩選
        filtered = all_docs
        for key, value in kwargs.items():
            if value is not None:
                filtered = [
                    doc for doc in filtered 
                    if getattr(doc, key, None) == value
                ]
        
        return filtered


class UserRepository(BaseRepository[User]):
    """使用者資料倉儲"""
    
    def __init__(self, config: GoogleSheetsConfig, credentials: Dict[str, Any]):
        """初始化
        
        Args:
            config: Google Sheets 設定
            credentials: GCP 服務帳號憑證
        """
        self.config = config
        self.connection = GoogleSheetsConnection(credentials)
        self._worksheet = None
        self._connect()
    
    def _connect(self) -> None:
        """連接到 Google Sheets"""
        try:
            client = self.connection.get_client()
            sheet = client.open_by_url(self.config.sheet_url)
            self._worksheet = sheet.worksheet(self.config.users_worksheet)
        except Exception as e:
            raise DatabaseConnectionError(f"無法連接到使用者工作表: {str(e)}")
    
    def get_all(self) -> List[User]:
        """取得所有使用者"""
        try:
            records = self._worksheet.get_all_records()
            
            if not records:
                return []
            
            users = []
            for record in records:
                try:
                    user = User.from_sheet_row(record)
                    users.append(user)
                except ValueError:
                    continue
            
            return users
            
        except Exception as e:
            raise DatabaseConnectionError(f"讀取使用者資料失敗: {str(e)}")
    
    def get_by_id(self, username: str) -> Optional[User]:
        """依使用者名稱取得使用者"""
        try:
            cell = self._worksheet.find(username)
            if not cell:
                return None
            
            row_data = self._worksheet.row_values(cell.row)
            headers = self._worksheet.row_values(1)
            row_dict = dict(zip(headers, row_data))
            
            return User.from_sheet_row(row_dict)
            
        except ValueError:
            return None
        except Exception as e:
            raise DatabaseConnectionError(f"查詢使用者失敗: {str(e)}")
    
    def create(self, user: User) -> bool:
        """新增使用者"""
        try:
            existing = self.get_by_id(user.username)
            if existing:
                raise ValidationError(f"使用者名稱已存在: {user.username}")
            
            row_data = user.to_sheet_row()
            headers = self._worksheet.row_values(1)
            values = [row_data.get(header, '') for header in headers]
            
            self._worksheet.append_row(values)
            return True
            
        except ValidationError:
            raise
        except Exception as e:
            raise DatabaseConnectionError(f"新增使用者失敗: {str(e)}")
    
    def update(self, user: User) -> bool:
        """更新使用者"""
        try:
            cell = self._worksheet.find(user.username)
            if not cell:
                raise RecordNotFoundError(f"找不到使用者: {user.username}")
            
            row_data = user.to_sheet_row()
            headers = self._worksheet.row_values(1)
            values = [row_data.get(header, '') for header in headers]
            
            range_notation = f'A{cell.row}:{chr(65 + len(headers) - 1)}{cell.row}'
            self._worksheet.update(range_notation, [values])
            
            return True
            
        except RecordNotFoundError:
            raise
        except Exception as e:
            raise DatabaseConnectionError(f"更新使用者失敗: {str(e)}")
    
    def delete(self, username: str) -> bool:
        """刪除使用者"""
        try:
            cell = self._worksheet.find(username)
            if not cell:
                raise RecordNotFoundError(f"找不到使用者: {username}")
            
            self._worksheet.delete_rows(cell.row)
            return True
            
        except RecordNotFoundError:
            raise
        except Exception as e:
            raise DatabaseConnectionError(f"刪除使用者失敗: {str(e)}")
    
    def find_by_criteria(self, **kwargs) -> List[User]:
        """依條件查詢使用者"""
        all_users = self.get_all()
        
        filtered = all_users
        for key, value in kwargs.items():
            if value is not None:
                filtered = [
                    user for user in filtered
                    if getattr(user, key, None) == value
                ]
        
        return filtered


class DeletedDocumentRepository:
    """刪除紀錄倉儲"""
    
    def __init__(self, config: GoogleSheetsConfig, credentials: Dict[str, Any]):
        """初始化"""
        self.config = config
        self.connection = GoogleSheetsConnection(credentials)
        self._worksheet = None
        self._connect()
    
    def _connect(self) -> None:
        """連接到 Google Sheets"""
        try:
            client = self.connection.get_client()
            sheet = client.open_by_url(self.config.sheet_url)
            self._worksheet = sheet.worksheet(self.config.deleted_worksheet)
        except Exception as e:
            raise DatabaseConnectionError(f"無法連接到刪除紀錄工作表: {str(e)}")
    
    def move_to_deleted(
        self,
        document: Document,
        deleted_by: str
    ) -> bool:
        """將公文移到刪除紀錄
        
        Args:
            document: Document 物件
            deleted_by: 刪除者
            
        Returns:
            True 如果成功
        """
        try:
            from datetime import datetime
            
            row_data = document.to_sheet_row()
            row_data[FieldNames.DELETED_AT] = datetime.now().isoformat()
            row_data[FieldNames.DELETED_BY] = deleted_by
            
            headers = self._worksheet.row_values(1)
            values = [row_data.get(header, '') for header in headers]
            
            self._worksheet.append_row(values)
            return True
            
        except Exception as e:
            raise DatabaseConnectionError(f"移動到刪除紀錄失敗: {str(e)}")
    
    def get_all_deleted(self) -> pd.DataFrame:
        """取得所有刪除紀錄
        
        Returns:
            DataFrame
        """
        try:
            records = self._worksheet.get_all_records()
            return pd.DataFrame(records)
        except Exception as e:
            raise DatabaseConnectionError(f"讀取刪除紀錄失敗: {str(e)}")
