"""首頁 UI

此模組實作系統首頁的所有UI邏輯。
"""
import streamlit as st
from typing import TYPE_CHECKING

from src.services.document_service import DocumentService
from src.services.tracking_service import TrackingService
from src.ui.styles.theme import Theme
from src.config.constants import UIConstants

if TYPE_CHECKING:
    from src.data_access.google_sheets import DocumentRepository


class HomePage:
    """首頁類別"""
    
    def __init__(self, repository: 'DocumentRepository'):
        """初始化
        
        Args:
            repository: DocumentRepository 實例
        """
        self.doc_service = DocumentService(repository)
        self.tracking_service = TrackingService(repository)
    
    def render(self):
        """渲染首頁"""
        # 套用樣式
        st.markdown(Theme.get_global_css(), unsafe_allow_html=True)
        
        st.markdown("## 📊 系統概覽")
        
        # 取得資料
        all_docs = self.doc_service.repository.get_all()
        urgent_list, normal_list = self.tracking_service.get_pending_replies()
        
        # 統計卡片
        self._render_metrics(all_docs, urgent_list, normal_list)
        
        # 緊急警示
        if urgent_list:
            self._render_urgent_alerts(urgent_list)
        
        st.markdown("---")
        
        # 功能磚塊
        self._render_function_tiles(len(urgent_list))
        
        st.markdown("---")
        
        # 近期活動
        self._render_recent_activity(all_docs[:5])
    
    def _render_metrics(self, all_docs, urgent_list, normal_list):
        """渲染統計卡片"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="📚 總公文數",
                value=len(all_docs)
            )
        
        with col2:
            pending_count = len(urgent_list) + len(normal_list)
            delta = f"+{len(urgent_list)}" if urgent_list else None
            st.metric(
                label="⏳ 待回覆",
                value=pending_count,
                delta=delta,
                delta_color="inverse"
            )
        
        with col3:
            completed = [doc for doc in all_docs if doc.parent_id]
            st.metric(
                label="✅ 已完成",
                value=len(completed)
            )
        
        with col4:
            from src.config.constants import OCRStatus
            pending_ocr = [doc for doc in all_docs if doc.ocr_status == OCRStatus.PENDING]
            st.metric(
                label="📝 待辨識",
                value=len(pending_ocr)
            )
    
    def _render_urgent_alerts(self, urgent_list):
        """渲染緊急警示"""
        st.markdown("---")
        st.markdown(f"""
        <div class="alert-card-urgent">
            <h3>⚠️ 緊急提醒: {len(urgent_list)} 筆公文超過 7 天未回覆</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # 顯示前 3 筆
        for doc, status in urgent_list[:3]:
            st.markdown(
                f"🔴 **{doc.id}** | {doc.agency} | "
                f"已等待 **{status.days_waiting}** 天 | {doc.subject[:30]}..."
            )
        
        if len(urgent_list) > 3:
            st.caption(f"...還有 {len(urgent_list) - 3} 筆")
    
    def _render_function_tiles(self, urgent_count):
        """渲染功能磚塊"""
        st.markdown("### 🎯 快速功能")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #F5F1E8 0%, #E8DCC8 100%); 
                        border-radius: 16px; padding: 40px; text-align: center;
                        min-height: 180px; display: flex; flex-direction: column; justify-content: center;">
                <div style="font-size: 48px;">➕</div>
                <div style="font-size: 20px; font-weight: 600; margin: 12px 0;">新增公文</div>
                <div style="font-size: 14px; color: #666;">上傳 PDF 建立新案件</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("點擊進入", key="tile_add", use_container_width=True):
                st.session_state[UIConstants.SESSION_CURRENT_PAGE] = UIConstants.PAGE_ADD_DOCUMENT
                st.rerun()
        
        with col2:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #F5F1E8 0%, #E8DCC8 100%); 
                        border-radius: 16px; padding: 40px; text-align: center;
                        min-height: 180px; display: flex; flex-direction: column; justify-content: center;">
                <div style="font-size: 48px;">🔍</div>
                <div style="font-size: 20px; font-weight: 600; margin: 12px 0;">查詢公文</div>
                <div style="font-size: 14px; color: #666;">搜尋與檢視公文</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("點擊進入", key="tile_search", use_container_width=True):
                st.session_state[UIConstants.SESSION_CURRENT_PAGE] = UIConstants.PAGE_SEARCH
                st.rerun()
        
        col3, col4 = st.columns(2)
        
        with col3:
            badge = f" ({urgent_count}筆)" if urgent_count else ""
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #FFF3F3 0%, #FFE5E5 100%); 
                        border-radius: 16px; padding: 40px; text-align: center;
                        min-height: 180px; display: flex; flex-direction: column; justify-content: center;">
                <div style="font-size: 48px;">⏰</div>
                <div style="font-size: 20px; font-weight: 600; margin: 12px 0;">追蹤回覆</div>
                <div style="font-size: 14px; color: #666;">監控待回覆公文{badge}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("點擊進入", key="tile_tracking", use_container_width=True):
                st.session_state[UIConstants.SESSION_CURRENT_PAGE] = UIConstants.PAGE_TRACKING
                st.rerun()
        
        with col4:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #F5F1E8 0%, #E8DCC8 100%); 
                        border-radius: 16px; padding: 40px; text-align: center;
                        min-height: 180px; display: flex; flex-direction: column; justify-content: center;">
                <div style="font-size: 48px;">📝</div>
                <div style="font-size: 20px; font-weight: 600; margin: 12px 0;">處理辨識</div>
                <div style="font-size: 14px; color: #666;">OCR 文字辨識</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("點擊進入", key="tile_ocr", use_container_width=True):
                st.session_state[UIConstants.SESSION_CURRENT_PAGE] = UIConstants.PAGE_OCR
                st.rerun()
    
    def _render_recent_activity(self, recent_docs):
        """渲染近期活動"""
        st.markdown("### 📋 近期活動 (最新 5 筆)")
        
        if not recent_docs:
            st.info("尚無公文資料")
            return
        
        for doc in recent_docs:
            col1, col2 = st.columns([4, 1])
            
            with col1:
                icon = "📤" if doc.is_outgoing() else "📥"
                st.markdown(
                    f"{icon} **{doc.id}** | {doc.date.strftime('%Y-%m-%d')} | "
                    f"{doc.agency} | {doc.subject[:40]}..."
                )
            
            with col2:
                if st.button("👁️ 查看", key=f"view_recent_{doc.id}"):
                    st.session_state[UIConstants.SESSION_SELECTED_DOC_ID] = doc.id
                    st.session_state[UIConstants.SESSION_CURRENT_PAGE] = UIConstants.PAGE_SEARCH
                    st.session_state[UIConstants.SESSION_SHOW_DETAIL] = True
                    st.rerun()
