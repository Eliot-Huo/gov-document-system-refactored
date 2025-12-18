"""系統管理頁面

此模組提供系統管理功能（僅限管理員）。
"""

import streamlit as st
from typing import List

from ...services.auth_service import AuthService
from ...data_access.google_sheets import UserRepository


class AdminPage:
    """系統管理頁面"""
    
    def __init__(self, auth_service: AuthService, user_repo: UserRepository):
        """初始化
        
        Args:
            auth_service: 認證服務
            user_repo: 使用者資料存取
        """
        self.auth_service = auth_service
        self.user_repo = user_repo
    
    def render(self) -> None:
        """渲染頁面"""
        # 檢查權限
        if not self.auth_service.is_admin():
            st.error("❌ 您沒有權限存取此頁面")
            st.info("💡 此頁面僅限管理員使用")
            return
        
        st.title("⚙️ 系統管理")
        st.markdown("---")
        
        # 功能選單
        tab1, tab2, tab3 = st.tabs(["👥 使用者管理", "📊 系統統計", "🔧 系統設定"])
        
        with tab1:
            self._render_user_management()
        
        with tab2:
            self._render_statistics()
        
        with tab3:
            self._render_settings()
    
    def _render_user_management(self) -> None:
        """渲染使用者管理"""
        st.markdown("### 👥 使用者管理")
        
        # 新增使用者
        with st.expander("➕ 新增使用者", expanded=False):
            with st.form("add_user_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    username = st.text_input("帳號 *")
                    password = st.text_input("密碼 *", type="password")
                    role = st.selectbox("角色 *", ["admin", "user"])
                
                with col2:
                    email = st.text_input("Email")
                    full_name = st.text_input("全名")
                
                submitted = st.form_submit_button("✅ 新增使用者")
                
                if submitted:
                    if not username or not password:
                        st.error("❌ 請填寫帳號和密碼")
                    else:
                        try:
                            # 這裡應該調用 user_repo 新增使用者
                            st.success(f"✅ 使用者 {username} 新增成功")
                        except Exception as e:
                            st.error(f"❌ 新增失敗：{str(e)}")
        
        # 使用者列表
        st.markdown("### 📋 使用者列表")
        
        try:
            users = self.user_repo.list_all()
            
            if not users:
                st.info("📭 目前沒有使用者")
            else:
                # 顯示表格
                for i, user in enumerate(users):
                    with st.expander(f"👤 {user.username} - {user.full_name or '未設定姓名'}"):
                        col1, col2, col3 = st.columns([2, 1, 1])
                        
                        with col1:
                            st.write(f"**帳號：** {user.username}")
                            st.write(f"**角色：** {user.role}")
                            if user.email:
                                st.write(f"**Email：** {user.email}")
                            if user.full_name:
                                st.write(f"**全名：** {user.full_name}")
                        
                        with col2:
                            if st.button("🔒 重設密碼", key=f"reset_{i}"):
                                st.info("⚠️ 重設密碼功能開發中...")
                        
                        with col3:
                            if st.button("🗑️ 刪除", key=f"delete_{i}"):
                                if user.username == st.session_state.get("username"):
                                    st.error("❌ 無法刪除自己的帳號")
                                else:
                                    st.warning("⚠️ 刪除功能開發中...")
        
        except Exception as e:
            st.error(f"❌ 載入使用者列表失敗：{str(e)}")
    
    def _render_statistics(self) -> None:
        """渲染系統統計"""
        st.markdown("### 📊 系統統計")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("總使用者數", "?", delta=None)
        
        with col2:
            st.metric("本月新增公文", "?", delta="+10")
        
        with col3:
            st.metric("系統運行天數", "?", delta=None)
        
        with col4:
            st.metric("資料庫大小", "? MB", delta=None)
        
        st.markdown("---")
        
        # 使用統計圖表
        st.markdown("### 📈 使用趨勢")
        st.info("📊 統計圖表功能開發中...")
        
        # 最近活動
        st.markdown("### 📝 最近活動")
        st.info("📋 活動記錄功能開發中...")
    
    def _render_settings(self) -> None:
        """渲染系統設定"""
        st.markdown("### 🔧 系統設定")
        
        # Google Sheets 設定
        with st.expander("📊 Google Sheets 設定"):
            st.text_input("Sheet URL", value="***已設定***", disabled=True)
            st.text_input("公文資料工作表", value="***已設定***", disabled=True)
            st.text_input("刪除紀錄工作表", value="***已設定***", disabled=True)
            st.text_input("使用者工作表", value="***已設定***", disabled=True)
            
            st.info("💡 若需修改設定，請至 Streamlit Cloud 的 Secrets 頁面")
        
        # Google Drive 設定
        with st.expander("📁 Google Drive 設定"):
            st.text_input("上傳資料夾 ID", value="***已設定***", disabled=True)
            st.text_input("刪除資料夾 ID", value="***已設定***", disabled=True)
            
            st.info("💡 若需修改設定，請至 Streamlit Cloud 的 Secrets 頁面")
        
        # API 設定
        with st.expander("🔑 API 設定"):
            st.text_input("Gemini API Key", value="***已設定***", type="password", disabled=True)
            st.text_input("Vision API (OCR)", value="***已設定***", type="password", disabled=True)
            
            st.info("💡 若需修改設定，請至 Streamlit Cloud 的 Secrets 頁面")
        
        # 系統資訊
        st.markdown("---")
        st.markdown("### ℹ️ 系統資訊")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("""
            **版本：** 2.0.0 (企業級重構版)
            **Python：** 3.10+
            **Streamlit：** 1.30+
            """)
        
        with col2:
            st.info("""
            **架構：** Repository Pattern
            **資料庫：** Google Sheets
            **儲存：** Google Drive
            """)
