"""新增公文頁面 (修正版 v2.2)"""
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
        
        # 顯示成功訊息 (Toast)
        if st.session_state.get("doc_created"):
            st.toast(f"✅ 公文新增成功！文號：{st.session_state.doc_created}", icon="🎉")
            del st.session_state["doc_created"]

        with st.form("add_document_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                doc_type = st.selectbox(
                    "公文類型 *",
                    options=[
                        DocumentType.INCOMING.value,
                        DocumentType.OUTGOING.value,
                        DocumentType.MEMO.value  # 修正：將 INTERNAL 改為 MEMO
                    ],
                    # 讓選項顯示更友善的名稱
                    format_func=lambda x: {
                        DocumentType.INCOMING.value: "來文 (收文)",
                        DocumentType.OUTGOING.value: "發文",
                        DocumentType.MEMO.value: "內部簽呈"  # 對應 MEMO
                    }.get(x, x)
                )
                sender = st.text_input("發文機關 *")
                send_date = st.date_input("發文日期 *", value=date.today())
                document_number = st.text_input("發文字號")
            
            with col2:
                subject = st.text_area("主旨 *", height=100)
                # 這裡加個防呆，如果 session 中沒有 user 資訊，預設為空字串
                current_user = st.session_state.get("user", {})
                handler_default = current_user.get("display_name", "") if current_user else ""
                
                handler = st.text_input("承辦人", value=handler_default)
                notes = st.text_area("備註", height=100)
            
            st.markdown("### 📎 回覆資訊 (選填)")
            col3, col4 = st.columns(2)
            with col3:
                parent_id = st.text_input("回覆的公文文號")
            with col4:
                is_final_reply = st.checkbox("這是最終回覆")
            
            # 因為上面修好了，程式現在能執行到這裡，Submit Button 警告就會消失
            submitted = st.form_submit_button("✅ 新增公文", use_container_width=True)
            
            if submitted:
                try:
                    # 反查 Enum
                    type_enum = next(t for t in DocumentType if t.value == doc_type)
                    
                    user_info = st.session_state.get("user", {})
                    created_by = user_info.get("username", "system") if user_info else "system"

                    doc = self.document_service.create_document(
                        date=send_date,
                        doc_type=type_enum,
                        agency=sender,
                        subject=subject,
                        created_by=created_by,
                        parent_id=parent_id if parent_id else None,
                        manual_id=None
                    )
                    
                    st.session_state["doc_created"] = doc.id
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ 新增失敗：{str(e)}")
