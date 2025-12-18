"""公文業務邏輯服務 (修正版)"""
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from src.models.document import Document
from src.data_access.google_sheets import DocumentRepository
from src.config.constants import DocumentType, BusinessRules
from src.utils.exceptions import ValidationError, BusinessLogicError

class DocumentService:
    
    def __init__(self, repository: DocumentRepository):
        self.repository = repository
    
    def generate_document_id(
        self,
        date: datetime,
        is_reply: bool,
        parent_id: Optional[str] = None
    ) -> str:
        """修正 4: 效能優化版流水號生成"""
        if is_reply and not parent_id:
            raise ValidationError("回覆案件必須提供父公文 ID")
        
        # 使用新方法只抓取所有 ID，不抓取完整資料，速度快很多
        all_ids = self.repository.get_all_ids()
        
        if is_reply:
            # 格式: 金展回{序號}{父公文ID}
            prefix = BusinessRules.ID_PREFIX_REPLY
            # 計算目前這個父公文已有多少回覆
            # 這裡稍微複雜，因為 ID 包含 ParentID，我們需要過濾
            # 但因為回覆量通常不大，這裡用字串比對尚可
            relevant_ids = [
                eid for eid in all_ids 
                if eid.startswith(prefix) and parent_id in eid
            ]
            sequence = len(relevant_ids) + 1
            return f"{prefix}{sequence:02d}{parent_id}"
        else:
            # 格式: 金展詢{日期}{序號}
            date_str = date.strftime('%Y%m%d')
            prefix = f"{BusinessRules.ID_PREFIX_GENERAL}{date_str}"
            
            # 直接計算前綴符合的數量
            count = len([eid for eid in all_ids if eid.startswith(prefix)])
            sequence = count + 1
            return f"{prefix}{sequence:03d}"
    
    def create_document(
        self,
        date: datetime,
        doc_type: DocumentType,
        agency: str,
        subject: str,
        created_by: str,
        parent_id: Optional[str] = None,
        drive_file_id: Optional[str] = None,
        manual_id: Optional[str] = None,
        **kwargs  # 處理可能的額外參數
    ) -> Document:
        
        if not agency or not subject:
            raise ValidationError("機關單位和主旨為必填欄位")
        
        # 產生 ID
        if manual_id:
            existing = self.repository.get_by_id(manual_id)
            if existing:
                raise BusinessLogicError(f"文號已存在: {manual_id}")
            doc_id = manual_id
        else:
            is_reply = parent_id is not None
            # 這裡會呼叫優化後的 ID 生成邏輯
            doc_id = self.generate_document_id(date, is_reply, parent_id)
        
        document = Document(
            id=doc_id,
            date=date,
            type=DocumentType(doc_type) if isinstance(doc_type, str) else doc_type,
            agency=agency,
            subject=subject,
            parent_id=parent_id,
            drive_file_id=drive_file_id,
            created_at=datetime.now(),
            created_by=created_by,
            # 處理額外欄位如 handler, notes (如果 Model 支援的話)
        )
        
        if not self.repository.create(document):
            raise BusinessLogicError("儲存公文失敗")
            
        return document

    # ... (search_documents, get_conversation_thread 等其他方法保持不變)
    def search_documents(self, keyword=None, **kwargs):
        # 簡單實作搜尋轉發
        return self.repository.find_by_criteria(**kwargs)
