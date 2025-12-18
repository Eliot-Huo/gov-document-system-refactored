"""政府公文追蹤系統 - 主程式

企業級架構重構版本。
"""
import streamlit as st

from src.config.settings import Settings
from src.config.constants import UIConstants
from src.data_access.google_sheets import (
    DocumentRepository,
    UserRepository,
    DeletedDocumentRepository
)
from src.data_access.google_drive import DriveRepository
from src.services.auth_service import AuthService
from src.services.document_service import DocumentService
from src.services.tracking_service import TrackingService
from src.ui.pages.home import HomePage
from src.ui.pages.add_document import AddDocumentPage
from src.ui.pages.search import SearchPage
from src.ui.pages.tracking import TrackingPage
from src.ui.pages.ocr import OCRPage
from src.ui.pages.admin import AdminPage
from src.ui.styles.theme import Theme

# 頁面設定
st.set_page_config(
    page_title="政府公文追蹤系統",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)


def initialize_repositories():
    """初始化所有 Repository
    
    Returns:
        tuple: (doc_repo, user_repo, deleted_repo, drive_repo)
    """
    # 載入設定
    sheets_config = Settings.load_google_sheets_config()
    drive_config = Settings.load_google_drive_config()
    credentials = Settings.load_gcp_credentials().credentials_dict
    
    # 初始化 Repositories
    doc_repo = DocumentRepository(sheets_config, credentials)
    user_repo = UserRepository(sheets_config, credentials)
    deleted_repo = DeletedDocumentRepository(sheets_config, credentials)
    drive_repo = DriveRepository(drive_config, credentials)
    
    return doc_repo, user_repo, deleted_repo, drive_repo


def render_sidebar(auth_service):
    """渲染側邊欄
    
    Args:
        auth_service: AuthService 實例
    """
    with st.sidebar:
        user = auth_service.get_current_user()
        
        if user:
            st.markdown(f"### 👤 {user['display_name']}")
            st.caption(f"角色: {user['role']}")
            
            if st.button("🚪 登出", use_container_width=True):
                auth_service.logout()
                st.rerun()
            
            st.markdown("---")
            st.markdown("### 📌 快速導航")
            
            # 首頁
            if st.button("🏠 首頁", key="nav_home", use_container_width=True):
                st.session_state[UIConstants.SESSION_CURRENT_PAGE] = UIConstants.PAGE_HOME
                st.rerun()
            
            # 新增公文
            if st.button("➕ 新增公文", key="nav_add", use_container_width=True):
                st.session_state[UIConstants.SESSION_CURRENT_PAGE] = UIConstants.PAGE_ADD_DOCUMENT
                st.rerun()
            
            # 查詢公文
            if st.button("🔍 查詢公文", key="nav_search", use_container_width=True):
                st.session_state[UIConstants.SESSION_CURRENT_PAGE] = UIConstants.PAGE_SEARCH
                st.rerun()
            
            # 追蹤回覆
            if st.button("⏰ 追蹤回覆", key="nav_tracking", use_container_width=True):
                st.session_state[UIConstants.SESSION_CURRENT_PAGE] = UIConstants.PAGE_TRACKING
                st.rerun()
            
            # OCR 處理
            if st.button("📝 處理辨識", key="nav_ocr", use_container_width=True):
                st.session_state[UIConstants.SESSION_CURRENT_PAGE] = UIConstants.PAGE_OCR
                st.rerun()
            
            # 系統管理 (僅管理員)
            if auth_service.is_admin():
                st.markdown("---")
                if st.button("📊 系統管理", key="nav_admin", use_container_width=True):
                    st.session_state[UIConstants.SESSION_CURRENT_PAGE] = UIConstants.PAGE_ADMIN
                    st.rerun()


def main():
    """主程式"""
    
    try:
        # 初始化 Repositories
        doc_repo, user_repo, deleted_repo, drive_repo = initialize_repositories()
        
        # 初始化 Auth Service
        auth_service = AuthService(user_repo)
        
        # 檢查是否已登入
        if not auth_service.is_authenticated():
            auth_service.render_login_page()
            return
        
        # 套用全域樣式
        st.markdown(Theme.get_global_css(), unsafe_allow_html=True)
        
        # 渲染側邊欄
        render_sidebar(auth_service)
        
        # Header
        st.markdown("# 📋 政府公文追蹤系統")
        st.caption("v2.0.0 - 企業級架構版本")
        st.markdown("---")
        
        # 路由 - 根據 current_page 顯示不同頁面
        current_page = st.session_state.get(
            UIConstants.SESSION_CURRENT_PAGE,
            UIConstants.PAGE_HOME
        )
        
        if current_page == UIConstants.PAGE_HOME:
            # 首頁
            document_service = DocumentService(doc_repo)
            tracking_service = TrackingService(doc_repo)
            HomePage(doc_repo, tracking_service).render()
        
        elif current_page == UIConstants.PAGE_ADD_DOCUMENT:
            # 新增公文
            document_service = DocumentService(doc_repo)
            AddDocumentPage(document_service).render()
        
        elif current_page == UIConstants.PAGE_SEARCH:
            # 查詢公文
            document_service = DocumentService(doc_repo)
            SearchPage(document_service).render()
        
        elif current_page == UIConstants.PAGE_TRACKING:
            # 追蹤回覆
            tracking_service = TrackingService(doc_repo)
            TrackingPage(tracking_service).render()
        
        elif current_page == UIConstants.PAGE_OCR:
            # OCR 處理
            OCRPage().render()
        
        elif current_page == UIConstants.PAGE_ADMIN:
            # 系統管理
            AdminPage(auth_service, user_repo).render()
    
    except Exception as e:
        st.error(f"❌ 系統錯誤: {str(e)}")
        st.exception(e)


if __name__ == "__main__":
    main()
