"""追蹤回覆頁面

此模組提供追蹤待回覆公文的功能。
"""

import streamlit as st
from typing import List, Tuple

from ...services.tracking_service import TrackingService
from ...models.document import Document


class TrackingPage:
    """追蹤回覆頁面"""
    
    def __init__(self, tracking_service: TrackingService):
        """初始化
        
        Args:
            tracking_service: 追蹤服務
        """
        self.tracking_service = tracking_service
    
    def render(self) -> None:
        """渲染頁面"""
        st.title("⏰ 追蹤回覆")
        st.markdown("---")
        
        try:
            # 取得待回覆公文
            urgent_docs, normal_docs = self.tracking_service.get_pending_replies()
            
            # 顯示統計
            self._display_statistics(urgent_docs, normal_docs)
            
            # 顯示緊急公文
            if urgent_docs:
                st.markdown("## 🚨 緊急待回覆（超過 7 天）")
                self._display_documents(urgent_docs, is_urgent=True)
            
            # 顯示一般待回覆
            if normal_docs:
                st.markdown("## ⚠️ 一般待回覆（7 天內）")
                self._display_documents(normal_docs, is_urgent=False)
            
            # 如果沒有待回覆公文
            if not urgent_docs and not normal_docs:
                st.success("🎉 太棒了！目前沒有待回覆的公文！")
        
        except Exception as e:
            st.error(f"❌ 載入失敗：{str(e)}")
    
    def _display_statistics(
        self,
        urgent_docs: List[Tuple[Document, int]],
        normal_docs: List[Tuple[Document, int]]
    ) -> None:
        """顯示統計資訊
        
        Args:
            urgent_docs: 緊急公文列表
            normal_docs: 一般公文列表
        """
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "總待回覆",
                len(urgent_docs) + len(normal_docs),
                delta=None
            )
        
        with col2:
            st.metric(
                "緊急（>7天）",
                len(urgent_docs),
                delta=None,
                delta_color="inverse"
            )
        
        with col3:
            st.metric(
                "一般（≤7天）",
                len(normal_docs),
                delta=None
            )
        
        st.markdown("---")
    
    def _display_documents(
        self,
        docs: List[Tuple[Document, int]],
        is_urgent: bool
    ) -> None:
        """顯示公文列表
        
        Args:
            docs: 公文列表（公文, 等待天數）
            is_urgent: 是否為緊急
        """
        # 按等待天數排序（從長到短）
        docs = sorted(docs, key=lambda x: x[1], reverse=True)
        
        for doc, days_waiting in docs:
            # 決定卡片顏色
            if is_urgent:
                card_class = "alert-card-urgent"
                icon = "🚨"
            else:
                card_class = "alert-card-warning"
                icon = "⚠️"
            
            # 顯示公文卡片
            with st.container():
                st.markdown(f"""
                <div class="{card_class}">
                    <h4>{icon} {doc.document_id} - 已等待 {days_waiting} 天</h4>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**主旨：** {doc.subject}")
                    st.markdown(f"**發文機關：** {doc.sender}")
                    st.markdown(f"**發文日期：** {doc.send_date}")
                    
                    if doc.handler:
                        st.markdown(f"**承辦人：** {doc.handler}")
                
                with col2:
                    st.markdown(f"**類型：** {doc.doc_type}")
                    st.markdown(f"**收文日期：** {doc.created_at.strftime('%Y-%m-%d')}")
                    
                    # 操作按鈕
                    col_btn1, col_btn2 = st.columns(2)
                    
                    with col_btn1:
                        if st.button("📝 立即回覆", key=f"reply_{doc.document_id}"):
                            st.session_state["page"] = "ADD_DOCUMENT"
                            st.session_state["reply_to"] = doc.document_id
                            st.rerun()
                    
                    with col_btn2:
                        if st.button("📄 查看詳情", key=f"detail_{doc.document_id}"):
                            self._show_document_detail(doc)
                
                st.markdown("---")
    
    def _show_document_detail(self, doc: Document) -> None:
        """顯示公文詳情
        
        Args:
            doc: 公文
        """
        with st.expander(f"📄 {doc.document_id} 詳細資訊", expanded=True):
            st.markdown(f"**文號：** {doc.document_id}")
            st.markdown(f"**類型：** {doc.doc_type}")
            st.markdown(f"**發文機關：** {doc.sender}")
            st.markdown(f"**主旨：** {doc.subject}")
            st.markdown(f"**發文日期：** {doc.send_date}")
            
            if doc.document_number:
                st.markdown(f"**發文字號：** {doc.document_number}")
            
            if doc.handler:
                st.markdown(f"**承辦人：** {doc.handler}")
            
            if doc.notes:
                st.markdown(f"**備註：** {doc.notes}")
            
            st.markdown(f"**建立時間：** {doc.created_at}")
            st.markdown(f"**建立人：** {doc.created_by}")
