"""公文業務邏輯服務

此模組包含所有公文相關的業務邏輯，包括：
- 流水號生成
- 對話串建立
- 文件篩選
- 文件建立/更新
"""
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from src.models.document import Document
from src.data_access.google_sheets import DocumentRepository
from src.config.constants import DocumentType, BusinessRules
from src.utils.exceptions import ValidationError, BusinessLogicError


class DocumentService:
    """公文業務邏輯服務"""
    
    def __init__(self, repository: DocumentRepository):
        """初始化
        
        Args:
            repository: DocumentRepository 實例
        """
        self.repository = repository
    
    def generate_document_id(
        self,
        date: datetime,
        is_reply: bool,
        parent_id: Optional[str] = None
    ) -> str:
        """產生公文流水號
        
        Args:
            date: 公文日期
            is_reply: 是否為回覆案件
            parent_id: 父公文 ID (回覆案件必填)
            
        Returns:
            公文流水號
            
        Raises:
            ValidationError: 驗證失敗
        """
        if is_reply and not parent_id:
            raise ValidationError("回覆案件必須提供父公文 ID")
        
        date_str = date.strftime('%Y%m%d')
        
        # 取得所有公文
        all_docs = self.repository.get_all()
        
        if is_reply:
            # 回覆案件: 金展回{序號}{父公文ID}
            reply_docs = [
                doc for doc in all_docs
                if doc.parent_id == parent_id 
                and doc.id.startswith(BusinessRules.ID_PREFIX_REPLY)
            ]
            sequence = len(reply_docs) + 1
            return f"{BusinessRules.ID_PREFIX_REPLY}{sequence:02d}{parent_id}"
        else:
            # 一般案件: 金展詢{日期}{序號}
            same_day_docs = [
                doc for doc in all_docs
                if doc.date.strftime('%Y%m%d') == date_str
                and doc.id.startswith(BusinessRules.ID_PREFIX_GENERAL)
            ]
            sequence = len(same_day_docs) + 1
            return f"{BusinessRules.ID_PREFIX_GENERAL}{date_str}{sequence:03d}"
    
    def get_conversation_thread(
        self,
        root_id: str
    ) -> List[Tuple[Document, int]]:
        """取得對話串
        
        Args:
            root_id: 根公文 ID
            
        Returns:
            [(Document, level), ...] 列表，level 表示階層深度
        """
        all_docs = self.repository.get_all()
        doc_dict = {doc.id: doc for doc in all_docs}
        
        def build_thread_recursive(doc_id: str, level: int = 0) -> List[Tuple[Document, int]]:
            """遞迴建立對話串"""
            if doc_id not in doc_dict:
                return []
            
            result = [(doc_dict[doc_id], level)]
            
            # 找出所有回覆此公文的子節點
            children = [doc for doc in all_docs if doc.parent_id == doc_id]
            for child in children:
                result.extend(build_thread_recursive(child.id, level + 1))
            
            return result
        
        return build_thread_recursive(root_id)
    
    def get_recent_documents(
        self,
        months: Optional[int] = None
    ) -> List[Document]:
        """取得近期公文
        
        Args:
            months: 月數，預設使用 BusinessRules.RECENT_MONTHS_FILTER
            
        Returns:
            公文列表
        """
        if months is None:
            months = BusinessRules.RECENT_MONTHS_FILTER
        
        threshold_date = datetime.now() - timedelta(days=months * 30)
        all_docs = self.repository.get_all()
        
        return [doc for doc in all_docs if doc.date >= threshold_date]
    
    def create_document(
        self,
        date: datetime,
        doc_type: DocumentType,
        agency: str,
        subject: str,
        created_by: str,
        parent_id: Optional[str] = None,
        drive_file_id: Optional[str] = None,
        manual_id: Optional[str] = None
    ) -> Document:
        """建立新公文
        
        Args:
            date: 公文日期
            doc_type: 公文類型
            agency: 機關單位
            subject: 主旨
            created_by: 建立者
            parent_id: 父公文 ID (選填)
            drive_file_id: Drive 檔案 ID (選填)
            manual_id: 手動輸入的文號 (選填)
            
        Returns:
            建立的 Document 物件
            
        Raises:
            ValidationError: 驗證失敗
            BusinessLogicError: 業務邏輯錯誤
        """
        # 驗證必填欄位
        if not agency or not subject:
            raise ValidationError("機關單位和主旨為必填欄位")
        
        if len(subject) < 5:
            raise ValidationError("主旨至少需要 5 個字")
        
        # 產生或使用文號
        if manual_id:
            # 檢查文號是否已存在
            existing = self.repository.get_by_id(manual_id)
            if existing:
                raise BusinessLogicError(f"文號已存在: {manual_id}")
            doc_id = manual_id
        else:
            is_reply = parent_id is not None
            doc_id = self.generate_document_id(date, is_reply, parent_id)
        
        # 建立 Document 物件
        document = Document(
            id=doc_id,
            date=date,
            type=doc_type,
            agency=agency,
            subject=subject,
            parent_id=parent_id,
            drive_file_id=drive_file_id,
            created_at=datetime.now(),
            created_by=created_by
        )
        
        # 儲存到資料庫
        success = self.repository.create(document)
        if not success:
            raise BusinessLogicError("儲存公文失敗")
        
        return document
    
    def update_document(self, document: Document) -> bool:
        """更新公文
        
        Args:
            document: Document 物件
            
        Returns:
            True 如果成功
            
        Raises:
            ValidationError: 驗證失敗
        """
        if not document.agency or not document.subject:
            raise ValidationError("機關單位和主旨為必填欄位")
        
        return self.repository.update(document)
    
    def search_documents(
        self,
        keyword: Optional[str] = None,
        date_start: Optional[datetime] = None,
        date_end: Optional[datetime] = None,
        doc_type: Optional[DocumentType] = None,
        agency: Optional[str] = None
    ) -> List[Document]:
        """搜尋公文
        
        Args:
            keyword: 關鍵字 (搜尋主旨)
            date_start: 開始日期
            date_end: 結束日期
            doc_type: 公文類型
            agency: 機關單位
            
        Returns:
            符合條件的公文列表
            
        Raises:
            ValidationError: 驗證失敗
        """
        if keyword and len(keyword) < 2:
            raise ValidationError("關鍵字至少需要 2 個字")
        
        all_docs = self.repository.get_all()
        results = all_docs
        
        # 關鍵字篩選
        if keyword:
            results = [doc for doc in results if keyword in doc.subject]
        
        # 日期篩選
        if date_start:
            results = [doc for doc in results if doc.date >= date_start]
        if date_end:
            results = [doc for doc in results if doc.date <= date_end]
        
        # 類型篩選
        if doc_type:
            results = [doc for doc in results if doc.type == doc_type]
        
        # 機關篩選
        if agency:
            results = [doc for doc in results if agency in doc.agency]
        
        return results
    
    def get_root_documents(self) -> List[Document]:
        """取得所有根節點公文 (沒有 parent_id 的公文)
        
        Returns:
            根節點公文列表
        """
        all_docs = self.repository.get_all()
        return [doc for doc in all_docs if not doc.parent_id]
    
    def soft_delete(
        self,
        doc_id: str,
        deleted_by: str,
        deleted_repo
    ) -> bool:
        """軟刪除公文
        
        Args:
            doc_id: 公文 ID
            deleted_by: 刪除者
            deleted_repo: DeletedDocumentRepository 實例
            
        Returns:
            True 如果成功
            
        Raises:
            BusinessLogicError: 刪除失敗
        """
        # 取得公文
        document = self.repository.get_by_id(doc_id)
        if not document:
            raise BusinessLogicError(f"找不到公文: {doc_id}")
        
        # 移到刪除紀錄
        success = deleted_repo.move_to_deleted(document, deleted_by)
        if not success:
            raise BusinessLogicError("移動到刪除紀錄失敗")
        
        # 從主表刪除
        self.repository.delete(doc_id)
        
        return True
