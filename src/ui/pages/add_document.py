"""新增公文頁面 (修正版)"""
import streamlit as st
from datetime import date
from typing import Optional

from src.services.document_service import DocumentService
from src.models.document import DocumentType
from src.config.constants import UIConstants

class AddDocumentPage:
    def __init__(self, document_service: DocumentService):
        self.document_service = document_service
    
    def render(self) -> None:
        st.title("📝 新增公文")
        
        # 修正 5: 使用 session_state 來重置表單，而不是 sleep + rerun
        # 如果有上傳成功的標記，顯示 toast
        if st.session_state.get("doc_created"):
            st.toast(f"✅ 公文新增成功！文號：{st.session_state.doc_created}", icon="🎉")
            # 清除標記
            del st.session_state["doc_created"]

        with st.form("add_document_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                doc_type = st.selectbox(
                    "公文類型 *",
                    options=[
                        DocumentType.INCOMING.value,
                        DocumentType.OUTGOING.value,
                        DocumentType.INTERNAL.value
                    ]
                )
                sender = st.text_input("發文機關 *")
                send_date = st.date_input("發文日期 *", value=date.today())
                document_number = st.text_input("發文字號")
            
            with col2:
                subject = st.text_area("主旨 *", height=100)
                handler = st.text_input("承辦人", value=st.session_state.get("user", {}).get("display_name", ""))
                notes = st.text_area("備註", height=100)
            
            st.markdown("### 📎 回覆資訊 (選填)")
            col3, col4 = st.columns(2)
            with col3:
                parent_id = st.text_input("回覆的公文文號")
            with col4:
                is_final_reply = st.checkbox("這是最終回覆")
            
            submitted = st.form_submit_button("✅ 新增公文", use_container_width=True)
            
            if submitted:
                try:
                    # 轉換 Enum
                    type_enum = next(t for t in DocumentType if t.value == doc_type)
                    
                    doc = self.document_service.create_document(
                        date=send_date,
                        doc_type=type_enum,
                        agency=sender,
                        subject=subject,
                        created_by=st.session_state.get("user", {}).get("username", "system"),
                        parent_id=parent_id if parent_id else None,
                        manual_id=None, # 自動生成
                        # 其他欄位如 handler, notes 需視 Model 擴充狀況處理，暫時忽略
                    )
                    
                    # 設定成功狀態並重整
                    st.session_state["doc_created"] = doc.id
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ 新增失敗：{str(e)}")
