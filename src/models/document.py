"""公文資料模型 (修正版)"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any, Union

from src.config.constants import DocumentType, OCRStatus, FieldNames

@dataclass
class Document:
    """公文資料模型"""
    id: str
    date: datetime
    type: DocumentType
    agency: str
    subject: str
    parent_id: Optional[str] = None
    drive_file_id: Optional[str] = None
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    ocr_status: OCRStatus = OCRStatus.PENDING
    ocr_text: Optional[str] = None
    ocr_date: Optional[datetime] = None
    
    @staticmethod
    def _parse_smart_date(date_val: Any) -> datetime:
        """修正 3: 強健的日期解析"""
        if not date_val:
            return datetime.now()
        
        if isinstance(date_val, datetime):
            return date_val
            
        if isinstance(date_val, str):
            # 嘗試多種常見格式
            formats = ['%Y-%m-%d', '%Y/%m/%d', '%Y%m%d', '%d-%b-%Y']
            for fmt in formats:
                try:
                    return datetime.strptime(date_val, fmt)
                except ValueError:
                    continue
        
        # 兜底：如果真的解析不了，回傳現在，避免 crash，但印出警告
        print(f"Warning: 無法解析日期 '{date_val}'，使用當前時間。")
        return datetime.now()

    @classmethod
    def from_sheet_row(cls, row: Dict[str, Any]) -> 'Document':
        try:
            return cls(
                id=str(row.get(FieldNames.ID, '')),
                # 使用修正後的日期解析
                date=cls._parse_smart_date(row.get(FieldNames.DATE)),
                type=DocumentType(row.get(FieldNames.TYPE, '收文')), # 預設值
                agency=str(row.get(FieldNames.AGENCY, '')),
                subject=str(row.get(FieldNames.SUBJECT, '')),
                parent_id=str(row.get(FieldNames.PARENT_ID, '')) or None,
                drive_file_id=str(row.get(FieldNames.DRIVE_FILE_ID, '')) or None,
                created_at=cls._parse_datetime(str(row.get(FieldNames.CREATED_AT, ''))),
                created_by=str(row.get(FieldNames.CREATED_BY, '')),
                ocr_status=OCRStatus(row.get(FieldNames.OCR_STATUS, 'pending')),
                ocr_text=str(row.get(FieldNames.OCR_TEXT, '')),
                ocr_date=cls._parse_datetime(str(row.get(FieldNames.OCR_DATE, '')))
            )
        except Exception as e:
            raise ValueError(f"解析 Document 失敗: {str(e)}, Row: {row}")
    
    def to_sheet_row(self) -> Dict[str, str]:
        return {
            FieldNames.ID: self.id,
            FieldNames.DATE: self.date.strftime('%Y-%m-%d'),
            FieldNames.TYPE: self.type.value,
            FieldNames.AGENCY: self.agency,
            FieldNames.SUBJECT: self.subject,
            FieldNames.PARENT_ID: self.parent_id or '',
            FieldNames.DRIVE_FILE_ID: self.drive_file_id or '',
            FieldNames.CREATED_AT: self.created_at.isoformat() if self.created_at else '',
            FieldNames.CREATED_BY: self.created_by or '',
            FieldNames.OCR_STATUS: self.ocr_status.value,
            FieldNames.OCR_TEXT: self.ocr_text or '',
            FieldNames.OCR_DATE: self.ocr_date.isoformat() if self.ocr_date else ''
        }
    
    @staticmethod
    def _parse_datetime(date_str: str) -> Optional[datetime]:
        if not date_str: return None
        try: return datetime.fromisoformat(date_str)
        except: return None
    
    def is_reply(self) -> bool:
        return self.parent_id is not None
        
    def is_outgoing(self) -> bool:
        return self.type in [DocumentType.OUTGOING, DocumentType.LETTER]
