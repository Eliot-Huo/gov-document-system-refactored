"""公文業務邏輯服務 (功能補完版)"""
from datetime import datetime
from typing import Optional, List, Any
import io

from src.models.document import Document
from src.data_access.google_sheets import DocumentRepository
from src.data_access.google_drive import DriveRepository
from src.config.constants import DocumentType, BusinessRules
from src.utils.exceptions import ValidationError, BusinessLogicError
from src.utils.watermark import add_watermark 

class DocumentService:
    # ✨ 建構子加入了 drive_repository
    def __init__(self, repository: DocumentRepository, drive_repository: DriveRepository = None):
        self.repository = repository
        self.drive_repository = drive_repository 
    
    def generate_document_id(self, date: datetime, is_reply: bool, parent_id: Optional[str] = None) -> str:
        """生成流水號"""
        if is_reply and not parent_id:
            raise ValidationError("回覆案件必須提供父公文 ID")
        
        all_ids = self.repository.get_all_ids()
        
        if is_reply:
            prefix = BusinessRules.ID_PREFIX_REPLY
            relevant_ids = [eid for eid in all_ids if eid.startswith(prefix) and parent_id in eid]
            sequence = len(relevant_ids) + 1
            return f"{prefix}{sequence:02d}{parent_id}"
        else:
            date_str = date.strftime('%Y%m%d')
            prefix = f"{BusinessRules.ID_PREFIX_GENERAL}{date_str}"
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
        manual_id: Optional[str] = None,
        file_obj: Optional[Any] = None, # ✨ 接收檔案物件
        **kwargs
    ) -> Document:
        
        if not agency or not subject:
            raise ValidationError("機關單位和主旨為必填欄位")
        
        # 1. 產生 ID
        if manual_id:
            existing = self.repository.get_by_id(manual_id)
            if existing:
                raise BusinessLogicError(f"文號已存在: {manual_id}")
            doc_id = manual_id
        else:
            is_reply = parent_id is not None
            doc_id = self.generate_document_id(date, is_reply, parent_id)
            
        drive_file_id = None
        
        # 2. 處理檔案 (如果有上傳)
        if file_obj and self.drive_repository:
            try:
                # 讀取檔案內容
                file_bytes = file_obj.getvalue()
                
                # 判斷是否為 PDF 並加浮水印
                if file_obj.name.lower().endswith('.pdf'):
                    watermark_text = f"{doc_id} - {created_by}"
                    file_bytes = add_watermark(file_bytes, watermark_text)
                
                # 上傳到 Google Drive
                filename = f"{doc_id}_{file_obj.name}"
                drive_file_id = self.drive_repository.upload_file(
                    file_bytes=file_bytes,
                    filename=filename,
                    mime_type=file_obj.type
                )
            except Exception as e:
                print(f"檔案處理警告: {str(e)}")
        
        # 3. 建立 Document 物件
        document = Document(
            id=doc_id,
            date=date,
            type=DocumentType(doc_type) if isinstance(doc_type, str) else doc_type,
            agency=agency,
            subject=subject,
            parent_id=parent_id,
            drive_file_id=drive_file_id, # 寫入 Drive ID
            created_at=datetime.now(),
            created_by=created_by
        )
        
        # 4. 寫入資料庫
        if not self.repository.create(document):
            raise BusinessLogicError("儲存公文失敗")
            
        return document

    def search_documents(self, keyword=None, **kwargs):
        return self.repository.find_by_criteria(**kwargs)
