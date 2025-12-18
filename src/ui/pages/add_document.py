"""新增公文頁面

此模組提供新增公文的介面。
"""

import streamlit as st
from datetime import date, datetime
from typing import Optional

from ...services.document_service import DocumentService
from ...models.document import DocumentType


class AddDocumentPage:
    """新增公文頁面"""
    
    def __init__(self, document_service: DocumentService):
        """初始化
        
        Args:
            document_service: 公文服務
        """
        self.document_service = document_service
    
    def render(self) -> None:
        """渲染頁面"""
        st.title("📝 新增公文")
        st.markdown("---")
        
        # 建立表單
        with st.form("add_document_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                # 公文類型
                doc_type = st.selectbox(
                    "公文類型 *",
                    options=[
                        DocumentType.INCOMING.value,
                        DocumentType.OUTGOING.value,
                        DocumentType.INTERNAL.value
                    ],
                    format_func=lambda x: {
                        DocumentType.INCOMING.value: "來文",
                        DocumentType.OUTGOING.value: "發文",
                        DocumentType.INTERNAL.value: "內部簽呈"
                    }[x]
                )
                
                # 發文機關
                sender = st.text_input("發文機關 *", placeholder="例如：財政部")
                
                # 發文日期
                send_date = st.date_input(
                    "發文日期 *",
                    value=date.today()
                )
                
                # 發文字號
                document_number = st.text_input(
                    "發文字號",
                    placeholder="例如：台財稅字第1130123456號"
                )
            
            with col2:
                # 主旨
                subject = st.text_area(
                    "主旨 *",
                    placeholder="請輸入公文主旨...",
                    height=100
                )
                
                # 承辦人
                handler = st.text_input(
                    "承辦人",
                    value=st.session_state.get("user", {}).get("full_name", "")
                )
                
                # 備註
                notes = st.text_area(
                    "備註",
                    placeholder="其他需要記錄的資訊...",
                    height=100
                )
            
            # 回覆相關（選填）
            st.markdown("### 📎 回覆資訊（如果是回覆其他公文）")
            
            col3, col4 = st.columns(2)
            
            with col3:
                parent_id = st.text_input(
                    "回覆的公文文號",
                    placeholder="例如：金展詢1131218001"
                )
            
            with col4:
                is_final_reply = st.checkbox("這是最終回覆", value=False)
            
            # 提交按鈕
            st.markdown("---")
            submitted = st.form_submit_button("✅ 新增公文", use_container_width=True)
            
            if submitted:
                self._handle_submit(
                    doc_type=doc_type,
                    sender=sender,
                    send_date=send_date,
                    document_number=document_number,
                    subject=subject,
                    handler=handler,
                    notes=notes,
                    parent_id=parent_id if parent_id else None,
                    is_final_reply=is_final_reply
                )
    
    def _handle_submit(
        self,
        doc_type: str,
        sender: str,
        send_date: date,
        document_number: str,
        subject: str,
        handler: str,
        notes: str,
        parent_id: Optional[str],
        is_final_reply: bool
    ) -> None:
        """處理表單提交
        
        Args:
            doc_type: 公文類型
            sender: 發文機關
            send_date: 發文日期
            document_number: 發文字號
            subject: 主旨
            handler: 承辦人
            notes: 備註
            parent_id: 父公文ID
            is_final_reply: 是否為最終回覆
        """
        # 驗證必填欄位
        if not sender or not subject:
            st.error("❌ 請填寫所有必填欄位（標記 * 者）")
            return
        
        try:
            # 建立公文
            document = self.document_service.create_document(
                doc_type=doc_type,
                sender=sender,
                subject=subject,
                send_date=send_date,
                document_number=document_number,
                handler=handler,
                notes=notes,
                parent_id=parent_id,
                is_final_reply=is_final_reply,
                created_by=st.session_state.get("username", "")
            )
            
            st.success(f"✅ 公文新增成功！文號：{document.document_id}")
            
            # 顯示公文資訊
            with st.expander("📄 查看新增的公文", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**文號：** {document.document_id}")
                    st.write(f"**類型：** {document.doc_type}")
                    st.write(f"**發文機關：** {document.sender}")
                
                with col2:
                    st.write(f"**發文日期：** {document.send_date}")
                    st.write(f"**承辦人：** {document.handler}")
                    st.write(f"**建立時間：** {document.created_at}")
            
            # 清空表單（透過 rerun）
            st.info("💡 頁面將在 2 秒後重新整理...")
            import time
            time.sleep(2)
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ 新增失敗：{str(e)}")
