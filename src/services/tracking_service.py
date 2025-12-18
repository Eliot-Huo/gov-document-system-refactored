"""追蹤回覆業務邏輯服務

此模組處理公文追蹤回覆的所有業務邏輯。
"""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Tuple, Optional

from src.models.document import Document
from src.data_access.google_sheets import DocumentRepository
from src.config.constants import DocumentType, BusinessRules


@dataclass
class TrackingStatus:
    """追蹤狀態資料類別
    
    Attributes:
        has_reply: 是否已有回覆
        days_waiting: 等待天數
        need_tracking: 是否需要追蹤 (超過門檻天數)
        reply_count: 回覆數量
        latest_reply_date: 最新回覆日期
    """
    has_reply: bool
    days_waiting: int
    need_tracking: bool
    reply_count: int
    latest_reply_date: Optional[datetime] = None


class TrackingService:
    """追蹤回覆業務邏輯服務"""
    
    def __init__(self, repository: DocumentRepository):
        """初始化
        
        Args:
            repository: DocumentRepository 實例
        """
        self.repository = repository
    
    def check_reply_status(
        self,
        doc_id: str,
        doc_type: DocumentType,
        doc_date: datetime
    ) -> TrackingStatus:
        """檢查公文回覆狀態
        
        Args:
            doc_id: 公文 ID
            doc_type: 公文類型
            doc_date: 公文日期
            
        Returns:
            TrackingStatus 物件
        """
        # 只追蹤我方發文
        if doc_type not in [DocumentType.OUTGOING, DocumentType.LETTER]:
            return TrackingStatus(
                has_reply=False,
                days_waiting=0,
                need_tracking=False,
                reply_count=0
            )
        
        # 找出所有回覆
        all_docs = self.repository.get_all()
        replies = [doc for doc in all_docs if doc.parent_id == doc_id]
        
        # 計算等待天數
        days_waiting = (datetime.now() - doc_date).days
        
        # 判斷是否需要追蹤
        need_tracking = (
            len(replies) == 0 and 
            days_waiting > BusinessRules.TRACKING_THRESHOLD_DAYS
        )
        
        # 找出最新回覆日期
        latest_reply_date = None
        if replies:
            latest_reply_date = max(reply.date for reply in replies)
        
        return TrackingStatus(
            has_reply=len(replies) > 0,
            days_waiting=days_waiting,
            need_tracking=need_tracking,
            reply_count=len(replies),
            latest_reply_date=latest_reply_date
        )
    
    def get_pending_replies(
        self
    ) -> Tuple[List[Tuple[Document, TrackingStatus]], List[Tuple[Document, TrackingStatus]]]:
        """取得所有待回覆公文
        
        Returns:
            (urgent_list, normal_list) 元組
            - urgent_list: 需緊急追蹤的公文 (超過門檻天數)
            - normal_list: 等待中的公文 (未超過門檻天數)
        """
        all_docs = self.repository.get_all()
        
        # 只檢查我方發文
        outgoing_docs = [
            doc for doc in all_docs
            if doc.type in [DocumentType.OUTGOING, DocumentType.LETTER]
        ]
        
        urgent_list = []
        normal_list = []
        
        for doc in outgoing_docs:
            status = self.check_reply_status(doc.id, doc.type, doc.date)
            
            # 只關注尚未有回覆的公文
            if not status.has_reply:
                if status.need_tracking:
                    urgent_list.append((doc, status))
                else:
                    normal_list.append((doc, status))
        
        # 依等待天數排序 (從多到少)
        urgent_list.sort(key=lambda x: x[1].days_waiting, reverse=True)
        normal_list.sort(key=lambda x: x[1].days_waiting, reverse=True)
        
        return urgent_list, normal_list
    
    def get_tracking_statistics(self) -> dict:
        """取得追蹤統計資訊
        
        Returns:
            統計資訊字典
        """
        urgent_list, normal_list = self.get_pending_replies()
        
        return {
            'total_pending': len(urgent_list) + len(normal_list),
            'urgent_count': len(urgent_list),
            'normal_count': len(normal_list),
            'max_waiting_days': urgent_list[0][1].days_waiting if urgent_list else 0
        }
