"""常數定義模組

此模組定義系統中所有的常數，包括：
- 列舉型別 (Enum)
- 欄位名稱
- 業務規則常數
- API 端點
"""
from enum import Enum
from typing import Final


class DocumentType(Enum):
    """公文類型列舉"""
    OUTGOING = "發文"
    INCOMING = "收文"
    MEMO = "簽呈"
    LETTER = "函"


class OCRStatus(Enum):
    """OCR 狀態列舉"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class UserRole(Enum):
    """使用者角色列舉"""
    ADMIN = "admin"
    USER = "user"


class FieldNames:
    """資料表欄位名稱常數"""
    
    # 公文欄位
    ID: Final = "ID"
    DATE: Final = "Date"
    TYPE: Final = "Type"
    AGENCY: Final = "Agency"
    SUBJECT: Final = "Subject"
    PARENT_ID: Final = "Parent_ID"
    DRIVE_FILE_ID: Final = "Drive_File_ID"
    CREATED_AT: Final = "Created_At"
    CREATED_BY: Final = "Created_By"
    OCR_STATUS: Final = "OCR_Status"
    OCR_TEXT: Final = "OCR_Text"
    OCR_DATE: Final = "OCR_Date"
    
    # 使用者欄位
    USERNAME: Final = "Username"
    PASSWORD: Final = "Password"
    DISPLAY_NAME: Final = "Display_Name"
    ROLE: Final = "Role"
    
    # 刪除紀錄欄位
    DELETED_AT: Final = "Deleted_At"
    DELETED_BY: Final = "Deleted_By"


class BusinessRules:
    """業務規則常數"""
    
    # 追蹤回覆
    TRACKING_THRESHOLD_DAYS: Final = 7
    
    # 時間篩選
    RECENT_MONTHS_FILTER: Final = 3
    
    # OCR 設定
    MAX_OCR_PAGES: Final = 20
    MAX_TEXT_LENGTH: Final = 45000
    OCR_DPI: Final = 300
    
    # 文號前綴
    ID_PREFIX_GENERAL: Final = "金展詢"
    ID_PREFIX_REPLY: Final = "金展回"
    
    # Cache TTL
    CACHE_TTL_SECONDS: Final = 3600


class APIEndpoints:
    """API 端點常數"""
    
    # Gemini AI
    GEMINI_MODEL_PRIMARY: Final = "gemini-3.0-flash-preview"
    GEMINI_MODEL_FALLBACK: Final = "gemini-2.0-flash-exp"
    
    # Google Compute Metadata
    METADATA_SERVER: Final = "metadata.google.internal"


class UIConstants:
    """UI 常數"""
    
    # 頁面名稱
    PAGE_HOME: Final = "home"
    PAGE_ADD_DOCUMENT: Final = "add_document"
    PAGE_SEARCH: Final = "search"
    PAGE_TRACKING: Final = "tracking"
    PAGE_OCR: Final = "ocr"
    PAGE_ADMIN: Final = "admin"
    
    # Session State Keys
    SESSION_USER: Final = "user"
    SESSION_CURRENT_PAGE: Final = "current_page"
    SESSION_SELECTED_DOC_ID: Final = "selected_doc_id"
    SESSION_SHOW_DETAIL: Final = "show_detail"
    SESSION_SEARCH_PERFORMED: Final = "search_performed"
    SESSION_FORM_KEY: Final = "form_key"
    SESSION_UPLOADER_KEY: Final = "uploader_key"
