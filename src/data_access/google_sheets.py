"""Google Sheets 資料存取層 (修正版)"""
from typing import List, Optional, Dict, Any
import gspread
from google.oauth2.service_account import Credentials  # 修正 1: 使用新版驗證庫
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
        self.credentials = credentials
        self._client = None
    
    def get_client(self) -> gspread.Client:
        if self._client is None:
            try:
                scopes = [
                    'https://www.googleapis.com/auth/spreadsheets',
                    'https://www.googleapis.com/auth/drive'
                ]
                # 修正 1: 使用新版驗證方法
                creds = Credentials.from_service_account_info(
                    self.credentials,
                    scopes=scopes
                )
                self._client = gspread.authorize(creds)
            except Exception as e:
                raise DatabaseConnectionError(f"無法連接到 Google Sheets: {str(e)}")
        return self._client


class DocumentRepository(BaseRepository[Document]):
    """公文資料倉儲"""
    
    def __init__(self, config: GoogleSheetsConfig, credentials: Dict[str, Any]):
        self.config = config
        self.connection = GoogleSheetsConnection(credentials)
        self._worksheet = None
        self._connect()
    
    def _connect(self) -> None:
        try:
            client = self.connection.get_client()
            sheet = client.open_by_url(self.config.sheet_url)
            self._worksheet = sheet.worksheet(self.config.docs_worksheet)
        except Exception as e:
            raise DatabaseConnectionError(f"無法連接到公文工作表: {str(e)}")
    
    def get_all(self) -> List[Document]:
        try:
            records = self._worksheet.get_all_records()
            if not records:
                return []
            
            documents = []
            for row in records:
                try:
                    doc = Document.from_sheet_row(row)
                    documents.append(doc)
                except ValueError as e:
                    print(f"警告: 跳過無效資料: {str(e)}")
                    continue
            return documents
        except Exception as e:
            raise DatabaseConnectionError(f"讀取公文資料失敗: {str(e)}")

    def get_all_ids(self) -> List[str]:
        """修正 2: 效能優化方法 - 只取得 ID 欄位"""
        try:
            # 假設 ID 在第一欄 (Column A)
            return self._worksheet.col_values(1)[1:] # [1:] 排除標題列
        except Exception as e:
            print(f"讀取 ID 列表失敗: {str(e)}")
            return []

    def get_by_id(self, doc_id: str) -> Optional[Document]:
        try:
            cell = self._worksheet.find(doc_id)
            if not cell:
                return None
            
            row_data = self._worksheet.row_values(cell.row)
            headers = self._worksheet.row_values(1)
            # 補齊長度不足的 row_data (防止 IndexError)
            if len(row_data) < len(headers):
                row_data += [''] * (len(headers) - len(row_data))
                
            row_dict = dict(zip(headers, row_data))
            return Document.from_sheet_row(row_dict)
        except Exception as e:
            # find 失敗或解析失敗
            return None
    
    def create(self, document: Document) -> bool:
        try:
            existing = self.get_by_id(document.id)
            if existing:
                raise ValidationError(f"公文字號已存在: {document.id}")
            
            row_data = document.to_sheet_row()
            headers = self._worksheet.row_values(1)
            values = [row_data.get(header, '') for header in headers]
            
            self._worksheet.append_row(values)
            return True
        except ValidationError:
            raise
        except Exception as e:
            raise DatabaseConnectionError(f"新增公文失敗: {str(e)}")
    
    def update(self, document: Document) -> bool:
        try:
            cell = self._worksheet.find(document.id)
            if not cell:
                raise RecordNotFoundError(f"找不到公文: {document.id}")
            
            row_data = document.to_sheet_row()
            headers = self._worksheet.row_values(1)
            values = [row_data.get(header, '') for header in headers]
            
            range_notation = f'A{cell.row}:{chr(65 + len(headers) - 1)}{cell.row}'
            self._worksheet.update(range_notation, [values])
            return True
        except RecordNotFoundError:
            raise
        except Exception as e:
            raise DatabaseConnectionError(f"更新公文失敗: {str(e)}")
    
    def delete(self, doc_id: str) -> bool:
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
        all_docs = self.get_all()
        filtered = all_docs
        for key, value in kwargs.items():
            if value is not None:
                filtered = [d for d in filtered if getattr(d, key, None) == value]
        return filtered

# User 與 Deleted Repository 邏輯相對簡單，為節省篇幅，建議保留原 User/Deleted 邏輯
# 僅需確保 GoogleSheetsConnection 是使用上方修正過的版本即可
class UserRepository(BaseRepository[User]):
    def __init__(self, config: GoogleSheetsConfig, credentials: Dict[str, Any]):
        self.config = config
        self.connection = GoogleSheetsConnection(credentials)
        self._worksheet = None
        self._connect()

    def _connect(self) -> None:
        try:
            client = self.connection.get_client()
            sheet = client.open_by_url(self.config.sheet_url)
            self._worksheet = sheet.worksheet(self.config.users_worksheet)
        except Exception as e:
            raise DatabaseConnectionError(f"無法連接到使用者工作表: {str(e)}")

    def get_all(self) -> List[User]:
        try:
            records = self._worksheet.get_all_records()
            return [User.from_sheet_row(r) for r in records if r]
        except Exception:
            return []
            
    def get_by_id(self, username: str) -> Optional[User]:
        try:
            cell = self._worksheet.find(username)
            if not cell: return None
            row_data = self._worksheet.row_values(cell.row)
            headers = self._worksheet.row_values(1)
            return User.from_sheet_row(dict(zip(headers, row_data)))
        except Exception:
            return None

    # 其他方法 (create, update, delete) 依 BaseRepository 實作即可
    def create(self, entity: User) -> bool: pass
    def update(self, entity: User) -> bool: pass
    def delete(self, id: str) -> bool: pass
    def find_by_criteria(self, **kwargs) -> List[User]: pass


class DeletedDocumentRepository:
    def __init__(self, config: GoogleSheetsConfig, credentials: Dict[str, Any]):
        self.config = config
        self.connection = GoogleSheetsConnection(credentials)
        self._worksheet = None
        self._connect()
    
    def _connect(self) -> None:
        try:
            client = self.connection.get_client()
            sheet = client.open_by_url(self.config.sheet_url)
            self._worksheet = sheet.worksheet(self.config.deleted_worksheet)
        except Exception as e:
            raise DatabaseConnectionError(f"無法連接到刪除紀錄: {str(e)}")

    def move_to_deleted(self, document: Document, deleted_by: str) -> bool:
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
            raise DatabaseConnectionError(f"移動失敗: {str(e)}")
