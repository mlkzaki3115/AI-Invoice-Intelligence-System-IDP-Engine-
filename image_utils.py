import io
from PIL import Image, ImageOps
import fitz  # PyMuPDF للتعامل مع ملفات الـ PDF

SUPPORTED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "tiff", "tif", "bmp", "pdf"}

def normalize_invoice_input(file_bytes: bytes, filename: str) -> Image.Image:
    """
    تحويل أي صيغة مرفوعة (PNG, JPEG, WEBP, TIFF, BMP, PDF)
    إلى كائن PIL Image موحد بصيغة RGB قياسية.
    """
    ext = filename.split(".")[-1].lower()
    
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"صيغة غير مدعومة: .{ext}. الصيغ المسموحة: {', '.join(SUPPORTED_EXTENSIONS)}")

    # 1. إذا كان الملف PDF: تحويل أول صفحة إلى صورة عالية الدقة
    if ext == "pdf":
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        if len(doc) == 0:
            raise ValueError("ملف الـ PDF فارغ.")
        page = doc[0]  # قراءة الصفحة الأولى
        # مضاعفة الدقة (DPI) لضمان وضوح الأرقام الصغيرة
        pix = page.get_pixmap(dpi=200)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
    else:
        # 2. إذا كان الملف صورة عادية
        img = Image.open(io.BytesIO(file_bytes))

    # 3. تصحيح تدوير الصورة التلقائي (EXIF Orientation) لصور الهواتف
    img = ImageOps.exif_transpose(img)

    # 4. تحويل أي وضع لوني (RGBA / Grayscale / CMYK) إلى RGB نقي
    if img.mode != "RGB":
        # إذا كانت الصورة شفافة، وضع خلفية بيضاء تحتها
        if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.convert("RGBA").split()[3])
            img = background
        else:
            img = img.convert("RGB")

    # 5. ضبط الحجم الأقصى لتفادي بطء الاستجابة واستهلاك الذاكرة
    max_dim = 2048
    if max(img.size) > max_dim:
        img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)

    return img