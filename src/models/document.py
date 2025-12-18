"""公文資料模型

此模組定義公文的領域模型 (Domain Model)，
提供型別安全的資料結構和轉換方法。
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any

from src.config.constants import DocumentType, OCRStatus, FieldNames


@dataclass
class Document:
    """公文資料模型
    
    Attributes:
        id: 公文字號
        date: 公文日期
        type: 公文類型
        agency: 機關單位
        subject: 主旨
        parent_id: 父公文 ID (回覆案件才有)
        drive_file_id: Google Drive 檔案 ID
        created_at: 建立時間
        created_by: 建立者
        ocr_status: OCR 狀態
        ocr_text: OCR 辨識文字
        ocr_date: OCR 完成時間
    """
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
    
    @classmethod
    def from_sheet_row(cls, row: Dict[str, Any]) -> 'Document':
        """從 Google Sheets 列資料建立 Document 物件
        
        Args:
            row: Sheet 列資料 (dict 格式)
            
        Returns:
            Document 物件
            
        Raises:
            ValueError: 當資料格式不正確時
        """
        try:
            return cls(
                id=row[FieldNames.ID],
                date=datetime.strptime(row[FieldNames.DATE], '%Y-%m-%d'),
                type=DocumentType(row[FieldNames.TYPE]),
                agency=row[FieldNames.AGENCY],
                subject=row[FieldNames.SUBJECT],
                parent_id=row.get(FieldNames.PARENT_ID) or None,
                drive_file_id=row.get(FieldNames.DRIVE_FILE_ID) or None,
                created_at=cls._parse_datetime(row.get(FieldNames.CREATED_AT)),
                created_by=row.get(FieldNames.CREATED_BY),
                ocr_status=OCRStatus(row.get(FieldNames.OCR_STATUS, 'pending')),
                ocr_text=row.get(FieldNames.OCR_TEXT),
                ocr_date=cls._parse_datetime(row.get(FieldNames.OCR_DATE))
            )
        except (KeyError, ValueError) as e:
            raise ValueError(f"無法解析 Sheet 資料: {str(e)}")
    
    def to_sheet_row(self) -> Dict[str, str]:
        """轉換為 Google Sheets 列資料
        
        Returns:
            dict 格式的列資料
        """
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
    def _parse_datetime(date_str: Optional[str]) -> Optional[datetime]:
        """解析日期時間字串
        
        Args:
            date_str: ISO 格式的日期時間字串
            
        Returns:
            datetime 物件，如果輸入為空則回傳 None
        """
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str)
        except (ValueError, AttributeError):
            return None
    
    def is_reply(self) -> bool:
        """判斷是否為回覆案件
        
        Returns:
            True 如果有 parent_id，否則 False
        """
        return self.parent_id is not None
    
    def is_outgoing(self) -> bool:
        """判斷是否為我方發文
        
        Returns:
            True 如果是發文或函，否則 False
        """
        return self.type in [DocumentType.OUTGOING, DocumentType.LETTER]
    
    def __repr__(self) -> str:
        """字串表示"""
        return f"Document(id='{self.id}', type={self.type.value}, agency='{self.agency}')"
