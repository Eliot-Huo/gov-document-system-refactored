"""浮水印工具模組"""
import fitz  # PyMuPDF
import io

def add_watermark(file_bytes: bytes, text: str) -> bytes:
    """
    為 PDF 加上文字浮水印
    Args:
        file_bytes: 原始 PDF 的 bytes
        text: 浮水印文字
    Returns:
        加上浮水印後的 PDF bytes
    """
    try:
        # 開啟 PDF
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        
        for page in doc:
            # 計算位置 (頁面中心)
            rect = page.rect
            p = fitz.Point(rect.width / 2, rect.height / 2)
            
            # 加入浮水印 (旋轉 45 度，灰色，透明度)
            page.insert_text(
                p,
                text,
                fontsize=40,
                fontname="helv",  # 內建字體
                rotate=45,
                color=(0.5, 0.5, 0.5), # 灰色
                fill_opacity=0.3, # 透明度
                align=1 # 置中
            )
            
        # 輸出結果
        output_stream = io.BytesIO()
        doc.save(output_stream)
        return output_stream.getvalue()
        
    except Exception as e:
        print(f"浮水印處理失敗: {str(e)}")
        # 如果失敗，回傳原檔，不要讓程式崩潰
        return file_bytes
