"""UI 樣式主題

此模組定義所有 UI 樣式和 CSS。
"""


class Theme:
    """樣式主題類別"""
    
    # 配色定義
    COLORS = {
        'background': '#F5F1E8',
        'primary': '#8B7355',
        'card_bg': '#FFFFFF',
        'card_border': '#E8DCC8',
        'text_primary': '#2C3E50',
        'text_secondary': '#666666',
        'success': '#10B981',
        'warning': '#F59E0B',
        'danger': '#EF4444',
        'info': '#3B82F6'
    }
    
    # 尺寸定義
    SIZES = {
        'border_radius': '12px',
        'tile_border_radius': '16px',
        'tile_min_height': '180px'
    }
    
    @classmethod
    def get_global_css(cls) -> str:
        """取得全域 CSS
        
        Returns:
            CSS 字串
        """
        return f"""
        <style>
        /* 全域樣式 */
        .stApp {{
            background-color: {cls.COLORS['background']};
            color: {cls.COLORS['text_primary']};
        }}
        
        /* 強制所有文字深色 */
        .stMarkdown, .stText, p, span, div, h1, h2, h3, h4, h5, h6 {{
            color: {cls.COLORS['text_primary']} !important;
        }}
        
        /* 標題深色 */
        h1, h2, h3 {{
            color: {cls.COLORS['text_primary']} !important;
            font-weight: 600;
        }}
        
        /* 卡片樣式 */
        .custom-card {{
            background-color: {cls.COLORS['card_bg']};
            border: 1px solid {cls.COLORS['card_border']};
            border-radius: {cls.SIZES['border_radius']};
            padding: 20px;
            margin-bottom: 16px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        
        /* 功能磚塊樣式 */
        .function-tile {{
            background: linear-gradient(135deg, {cls.COLORS['background']} 0%, {cls.COLORS['card_border']} 100%);
            border-radius: {cls.SIZES['tile_border_radius']};
            padding: 40px;
            text-align: center;
            margin-bottom: 20px;
            min-height: {cls.SIZES['tile_min_height']};
            display: flex;
            flex-direction: column;
            justify-content: center;
            transition: all 0.3s ease;
        }}
        
        .function-tile:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        }}
        
        /* 警示卡片 */
        .alert-card-urgent {{
            background-color: #FFF3F3;
            border: 2px solid {cls.COLORS['danger']};
            border-radius: {cls.SIZES['border_radius']};
            padding: 20px;
            margin-bottom: 16px;
        }}
        
        .alert-card-warning {{
            background-color: #FFFBEB;
            border: 2px solid {cls.COLORS['warning']};
            border-radius: {cls.SIZES['border_radius']};
            padding: 20px;
            margin-bottom: 16px;
        }}
        
        .alert-card-success {{
            background-color: #F0FDF4;
            border: 2px solid {cls.COLORS['success']};
            border-radius: {cls.SIZES['border_radius']};
            padding: 20px;
            margin-bottom: 16px;
        }}
        
        /* 指標卡片 */
        .metric-card {{
            background-color: {cls.COLORS['card_bg']};
            border: 1px solid {cls.COLORS['card_border']};
            border-radius: {cls.SIZES['border_radius']};
            padding: 20px;
            text-align: center;
        }}
        
        /* 按鈕樣式 */
        .stButton > button {{
            background-color: {cls.COLORS['primary']};
            color: white;
            border-radius: 8px;
            padding: 10px 24px;
            border: none;
            transition: all 0.3s ease;
        }}
        
        .stButton > button:hover {{
            background-color: #6F5B45;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }}
        </style>
        """
