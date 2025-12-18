"""驗證服務

此模組處理使用者驗證相關的業務邏輯。
"""
import streamlit as st
from typing import Optional

from src.models.user import User
from src.data_access.google_sheets import UserRepository
from src.utils.exceptions import AuthenticationError
from src.config.constants import UIConstants


class AuthService:
    """驗證服務"""
    
    def __init__(self, repository: UserRepository):
        """初始化
        
        Args:
            repository: UserRepository 實例
        """
        self.repository = repository
    
    def verify_user(self, username: str, password: str) -> User:
        """驗證使用者
        
        Args:
            username: 使用者名稱
            password: 密碼
            
        Returns:
            User 物件
            
        Raises:
            AuthenticationError: 驗證失敗
        """
        if not username or not password:
            raise AuthenticationError("請輸入使用者名稱和密碼")
        
        user = self.repository.get_by_id(username)
        
        if not user:
            raise AuthenticationError("使用者不存在")
        
        if user.password != password:
            raise AuthenticationError("密碼錯誤")
        
        return user
    
    def login(self, username: str, password: str) -> bool:
        """登入
        
        Args:
            username: 使用者名稱
            password: 密碼
            
        Returns:
            True 如果成功
        """
        try:
            user = self.verify_user(username, password)
            st.session_state[UIConstants.SESSION_USER] = user.to_dict()
            return True
        except AuthenticationError as e:
            st.error(f"❌ {str(e)}")
            return False
    
    def logout(self) -> None:
        """登出"""
        if UIConstants.SESSION_USER in st.session_state:
            del st.session_state[UIConstants.SESSION_USER]
    
    def is_authenticated(self) -> bool:
        """檢查是否已登入
        
        Returns:
            True 如果已登入
        """
        return UIConstants.SESSION_USER in st.session_state
    
    def get_current_user(self) -> Optional[dict]:
        """取得目前登入的使用者
        
        Returns:
            使用者資訊字典，如果未登入則回傳 None
        """
        return st.session_state.get(UIConstants.SESSION_USER)
    
    def is_admin(self) -> bool:
        """檢查目前使用者是否為管理員
        
        Returns:
            True 如果是管理員
        """
        user = self.get_current_user()
        if not user:
            return False
        return user.get('role') == 'admin'
    
    def render_login_page(self) -> None:
        """渲染登入頁面 (UI 邏輯)"""
        st.markdown("# 🔐 登入系統")
        st.markdown("### 政府公文追蹤系統")
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("## 請登入")
            
            username = st.text_input("👤 使用者名稱", key="login_username")
            password = st.text_input("🔒 密碼", type="password", key="login_password")
            
            if st.button("🚪 登入", type="primary", use_container_width=True):
                if self.login(username, password):
                    st.success("✅ 登入成功!")
                    st.rerun()
            
            st.markdown("---")
            st.caption("💡 提示：請聯繫管理員取得帳號")
