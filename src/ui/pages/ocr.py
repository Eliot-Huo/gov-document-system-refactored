"""OCR 處理頁面

此模組提供文字識別功能。
"""

import streamlit as st
from typing import Optional


class OCRPage:
    """OCR 處理頁面"""
    
    def render(self) -> None:
        """渲染頁面"""
        st.title("📷 OCR 文字識別")
        st.markdown("---")
        
        st.info("💡 上傳公文圖片，系統將自動識別文字內容")
        
        # 上傳檔案
        uploaded_file = st.file_uploader(
            "選擇圖片檔案",
            type=["jpg", "jpeg", "png", "pdf"],
            help="支援 JPG、PNG、PDF 格式"
        )
        
        if uploaded_file:
            # 顯示上傳的圖片
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("### 📄 原始圖片")
                if uploaded_file.type.startswith("image"):
                    st.image(uploaded_file, use_container_width=True)
                else:
                    st.info("📋 已上傳 PDF 檔案")
            
            with col2:
                st.markdown("### 📝 識別結果")
                
                # 處理按鈕
                if st.button("🔍 開始識別", use_container_width=True):
                    with st.spinner("正在識別文字..."):
                        # 這裡應該調用 OCR API
                        # 暫時顯示提示訊息
                        st.warning("⚠️ OCR 功能開發中...")
                        st.info("""
                        📌 **功能說明：**
                        
                        1. 上傳公文圖片或 PDF
                        2. 系統使用 Google Cloud Vision API 識別文字
                        3. 自動擷取關鍵資訊：
                           - 發文機關
                           - 發文字號
                           - 主旨
                           - 發文日期
                        4. 可直接編輯識別結果
                        5. 一鍵匯入至新增公文表單
                        
                        💡 **即將推出！**
                        """)
            
            # 如果有識別結果，顯示編輯區域
            if st.session_state.get("ocr_result"):
                st.markdown("---")
                st.markdown("### ✏️ 編輯識別結果")
                
                with st.form("edit_ocr_result"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        sender = st.text_input("發文機關", value="")
                        doc_number = st.text_input("發文字號", value="")
                    
                    with col2:
                        send_date = st.date_input("發文日期")
                        doc_type = st.selectbox("公文類型", ["來文", "發文", "內部簽呈"])
                    
                    subject = st.text_area("主旨", height=100)
                    
                    submitted = st.form_submit_button("✅ 匯入至新增公文")
                    
                    if submitted:
                        st.session_state["page"] = "ADD_DOCUMENT"
                        st.session_state["ocr_data"] = {
                            "sender": sender,
                            "document_number": doc_number,
                            "send_date": send_date,
                            "doc_type": doc_type,
                            "subject": subject
                        }
                        st.rerun()
        
        else:
            # 顯示使用說明
            st.markdown("""
            ### 📖 使用說明
            
            1. **點擊上方「瀏覽檔案」按鈕**
            2. **選擇公文圖片或 PDF**
            3. **點擊「開始識別」按鈕**
            4. **檢查並編輯識別結果**
            5. **點擊「匯入至新增公文」**
            
            ---
            
            ### ✨ 功能特色
            
            - 🎯 **高精準度** - 使用 Google Cloud Vision API
            - 🚀 **快速識別** - 幾秒內完成處理
            - ✏️ **可編輯** - 識別結果可手動修正
            - 📋 **一鍵匯入** - 直接帶入新增公文表單
            
            ---
            
            ### 💡 小技巧
            
            - 圖片清晰度越高，識別率越好
            - 建議使用 300 DPI 以上的掃描品質
            - 避免陰影、反光或傾斜的圖片
            """)
            
            # 顯示範例
            with st.expander("📸 查看範例"):
                st.info("📌 這裡可以顯示公文掃描的最佳範例")
