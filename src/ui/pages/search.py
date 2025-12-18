"""查詢公文頁面

此模組提供公文查詢和檢視功能。
"""

import streamlit as st
from datetime import date, datetime, timedelta
from typing import List, Optional

from ...services.document_service import DocumentService
from ...models.document import Document


class SearchPage:
    """查詢公文頁面"""
    
    def __init__(self, document_service: DocumentService):
        """初始化
        
        Args:
            document_service: 公文服務
        """
        self.document_service = document_service
    
    def render(self) -> None:
        """渲染頁面"""
        st.title("🔍 查詢公文")
        st.markdown("---")
        
        # 搜尋條件
        with st.expander("🔎 搜尋條件", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                keyword = st.text_input(
                    "關鍵字",
                    placeholder="搜尋主旨、文號、發文機關..."
                )
            
            with col2:
                doc_type = st.selectbox(
                    "公文類型",
                    options=["全部", "來文", "發文", "內部簽呈"]
                )
            
            with col3:
                date_range = st.selectbox(
                    "日期範圍",
                    options=["全部", "今天", "最近7天", "最近30天", "最近90天", "自訂範圍"]
                )
            
            # 自訂日期範圍
            if date_range == "自訂範圍":
                col4, col5 = st.columns(2)
                with col4:
                    start_date = st.date_input(
                        "開始日期",
                        value=date.today() - timedelta(days=30)
                    )
                with col5:
                    end_date = st.date_input(
                        "結束日期",
                        value=date.today()
                    )
            else:
                start_date = None
                end_date = None
            
            # 搜尋按鈕
            search_button = st.button("🔍 搜尋", use_container_width=True)
        
        # 執行搜尋
        if search_button or "search_results" not in st.session_state:
            documents = self._search_documents(
                keyword=keyword if keyword else None,
                doc_type=doc_type if doc_type != "全部" else None,
                date_range=date_range,
                start_date=start_date,
                end_date=end_date
            )
            st.session_state["search_results"] = documents
        
        # 顯示結果
        documents = st.session_state.get("search_results", [])
        
        st.markdown(f"### 📊 搜尋結果（共 {len(documents)} 筆）")
        
        if not documents:
            st.info("🔍 沒有找到符合條件的公文")
        else:
            self._display_results(documents)
    
    def _search_documents(
        self,
        keyword: Optional[str],
        doc_type: Optional[str],
        date_range: str,
        start_date: Optional[date],
        end_date: Optional[date]
    ) -> List[Document]:
        """搜尋公文
        
        Args:
            keyword: 關鍵字
            doc_type: 公文類型
            date_range: 日期範圍
            start_date: 開始日期
            end_date: 結束日期
            
        Returns:
            公文列表
        """
        # 計算日期範圍
        if date_range == "今天":
            start_date = date.today()
            end_date = date.today()
        elif date_range == "最近7天":
            start_date = date.today() - timedelta(days=7)
            end_date = date.today()
        elif date_range == "最近30天":
            start_date = date.today() - timedelta(days=30)
            end_date = date.today()
        elif date_range == "最近90天":
            start_date = date.today() - timedelta(days=90)
            end_date = date.today()
        
        try:
            # 執行搜尋
            documents = self.document_service.search_documents(
                keyword=keyword,
                doc_type=doc_type,
                start_date=start_date,
                end_date=end_date
            )
            return documents
        except Exception as e:
            st.error(f"❌ 搜尋失敗：{str(e)}")
            return []
    
    def _display_results(self, documents: List[Document]) -> None:
        """顯示搜尋結果
        
        Args:
            documents: 公文列表
        """
        # 排序選項
        sort_by = st.selectbox(
            "排序方式",
            options=["最新優先", "最舊優先", "文號排序"],
            key="sort_documents"
        )
        
        # 排序
        if sort_by == "最新優先":
            documents = sorted(documents, key=lambda x: x.created_at, reverse=True)
        elif sort_by == "最舊優先":
            documents = sorted(documents, key=lambda x: x.created_at)
        else:
            documents = sorted(documents, key=lambda x: x.document_id)
        
        # 顯示公文列表
        for i, doc in enumerate(documents):
            with st.expander(f"📄 {doc.document_id} - {doc.subject[:50]}..."):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**主旨：** {doc.subject}")
                    st.markdown(f"**發文機關：** {doc.sender}")
                    st.markdown(f"**發文日期：** {doc.send_date}")
                    
                    if doc.document_number:
                        st.markdown(f"**發文字號：** {doc.document_number}")
                    
                    if doc.handler:
                        st.markdown(f"**承辦人：** {doc.handler}")
                    
                    if doc.notes:
                        st.markdown(f"**備註：** {doc.notes}")
                
                with col2:
                    st.markdown(f"**類型：** {doc.doc_type}")
                    st.markdown(f"**建立時間：** {doc.created_at.strftime('%Y-%m-%d %H:%M')}")
                    st.markdown(f"**建立人：** {doc.created_by}")
                    
                    # 如果有父公文
                    if doc.parent_id:
                        st.markdown(f"**回覆：** {doc.parent_id}")
                    
                    # 查看對話串按鈕
                    if st.button(f"🔗 查看對話串", key=f"thread_{i}"):
                        self._show_conversation_thread(doc.document_id)
    
    def _show_conversation_thread(self, document_id: str) -> None:
        """顯示對話串
        
        Args:
            document_id: 公文ID
        """
        try:
            thread = self.document_service.get_conversation_thread(document_id)
            
            st.markdown("### 💬 對話串")
            
            for doc, level in thread:
                indent = "　" * level
                
                with st.container():
                    st.markdown(f"{indent}📄 **{doc.document_id}**")
                    st.markdown(f"{indent}　　{doc.subject}")
                    st.markdown(f"{indent}　　發文機關：{doc.sender} | 日期：{doc.send_date}")
                    st.markdown("---")
        
        except Exception as e:
            st.error(f"❌ 載入對話串失敗：{str(e)}")
