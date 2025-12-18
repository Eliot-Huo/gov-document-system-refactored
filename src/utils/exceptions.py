"""自訂例外類別模組

此模組定義系統中所有的自訂例外，
提供更精確的錯誤處理機制。
"""


class AppException(Exception):
    """應用程式基礎例外"""
    pass


class DatabaseConnectionError(AppException):
    """資料庫連線錯誤
    
    當無法連接到 Google Sheets 或其他資料來源時拋出
    """
    pass


class RecordNotFoundError(AppException):
    """找不到記錄
    
    當查詢的資料不存在時拋出
    """
    pass


class ValidationError(AppException):
    """驗證錯誤
    
    當輸入資料驗證失敗時拋出
    """
    pass


class BusinessLogicError(AppException):
    """業務邏輯錯誤
    
    當業務邏輯規則被違反時拋出
    """
    pass


class AuthenticationError(AppException):
    """驗證失敗
    
    當使用者登入失敗時拋出
    """
    pass


class AuthorizationError(AppException):
    """授權失敗
    
    當使用者沒有權限執行操作時拋出
    """
    pass


class FileUploadError(AppException):
    """檔案上傳錯誤
    
    當檔案上傳到 Google Drive 失敗時拋出
    """
    pass


class OCRProcessingError(AppException):
    """OCR 處理錯誤
    
    當 OCR 辨識失敗時拋出
    """
    pass


class AIServiceError(AppException):
    """AI 服務錯誤
    
    當 AI 摘要服務失敗時拋出
    """
    pass
