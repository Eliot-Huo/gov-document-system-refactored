"""新增公文頁面 (功能補完版 v2.3)"""
import streamlit as st
from datetime import date
from src.services.document_service import DocumentService
from src.models.document import DocumentType

class AddDocumentPage:
    def __init__(self, document_service: DocumentService):
        self.document_service = document_service
    
    def render(self) -> None:
        st.title("📝 新增公文")
        
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
                        DocumentType.MEMO.value
                    ],
                    format_func=lambda x: {
                        DocumentType.INCOMING.value: "來文 (收文)",
                        DocumentType.OUTGOING.value: "發文",
                        DocumentType.MEMO.value: "內部簽呈"
                    }.get(x, x)
                )
                sender = st.text_input("發文機關 *")
                send_date = st.date_input("發文日期 *", value=date.today())
                document_number = st.text_input("發文字號")
            
            with col2:
                subject = st.text_area("主旨 *", height=100)
                current_user = st.session_state.get("user", {})
                handler_default = current_user.get("display_name", "") if current_user else ""
                handler = st.text_input("承辦人", value=handler_default)
                notes = st.text_area("備註", height=100)
            
            # === 新增：檔案上傳區塊 ===
            st.markdown("### 📎 附件上傳")
            uploaded_file = st.file_uploader("上傳公文 PDF (系統將自動加入浮水印)", type=["pdf"])
            # ========================

            st.markdown("### 📎 回覆資訊 (選填)")
            col3, col4 = st.columns(2)
            with col3:
                parent_id = st.text_input("回覆的公文文號")
            with col4:
                is_final_reply = st.checkbox("這是最終回覆")
            
            submitted = st.form_submit_button("✅ 新增公文", use_container_width=True)
            
            if submitted:
                try:
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
                        manual_id=None,
                        file_obj=uploaded_file # 傳遞檔案
                    )
                    
                    st.session_state["doc_created"] = doc.id
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ 新增失敗：{str(e)}")
                    # 顯示詳細錯誤以便除錯
                    import traceback
                    st.code(traceback.format_exc())
