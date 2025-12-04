"""
نظام إدارة محل ملابس متكامل مع Google Sheets
إصدار شامل مع كل المميزات المطلوبة
"""

import streamlit as st
import pandas as pd
import numpy as np
import random
import string
from datetime import datetime, timedelta
import time
import json
import re
from io import BytesIO

# مكتبات Google Sheets
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# --------------------------
# إعدادات الصفحة
# --------------------------
st.set_page_config(
    page_title="👕 نظام إدارة محل ملابس متكامل",
    page_icon="👕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------
# التهيئة الأولية للجلسة
# --------------------------
def init_session_state():
    """تهيئة جميع متغيرات الجلسة"""
    defaults = {
        'products': [],
        'sales': [],
        'barcodes': set(),
        'gsheet_initialized': False,
        'gsheet_client': None,
        'current_sale_items': [],
        'sale_total': 0.0,
        'sale_discount': 0.0,
        'search_results': [],
        'last_scanned': None,
        'scanner_mode': 'manual'  # 'manual', 'automatic', 'file'
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# --------------------------
# إعداد Google Sheets
# --------------------------
@st.cache_resource
def setup_google_sheets():
    """إعداد اتصال Google Sheets مع معالجة الأخطاء"""
    try:
        # تأكد من وجود ملف الاعتماد
        CREDENTIALS_FILE = 'clothing-store-credentials.json'
        
        # يمكنك تحميل الملف يدوياً عبر واجهة Streamlit
        if 'google_creds' not in st.session_state:
            st.warning("""
            ⚠️ **يرجى رفع ملف اعتماد Google Sheets API (.json)**
            
            **خطوات الحصول على الملف:**
            1. اذهب إلى Google Cloud Console
            2. أنشئ Service Account
            3. حمّل ملف JSON
            4. ارفعه هنا
            """)
            
            uploaded_file = st.file_uploader("رفع ملف credentials.json", type=['json'])
            if uploaded_file is not None:
                creds_data = json.load(uploaded_file)
                with open(CREDENTIALS_FILE, 'w') as f:
                    json.dump(creds_data, f)
                st.session_state.google_creds = creds_data
                st.success("✅ تم رفع ملف الاعتماد بنجاح!")
                st.rerun()
            else:
                return None
        
        # تعريف النطاقات المطلوبة
        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive"
        ]
        
        # إنشاء الاعتماد
        creds = Credentials.from_service_account_file(
            CREDENTIALS_FILE, 
            scopes=scope
        )
        
        # إنشاء عميل Google Sheets
        client = gspread.authorize(creds)
        
        # فتح الورقة
        SPREADSHEET_ID = "1YOUR_SPREADSHEET_ID_HERE"  # استبدل بمعرف ورقتك
        
        try:
            spreadsheet = client.open_by_key(SPREADSHEET_ID)
        except:
            # إنشاء ورقة جديدة إذا لم تكن موجودة
            st.info("📝 جاري إنشاء ورقة Google Sheets جديدة...")
            spreadsheet = client.create("Clothing_Store_System")
            
            # مشاركة الورقة
            spreadsheet.share('', perm_type='anyone', role='writer')
            
            # إنشاء الأوراق المطلوبة
            worksheet_list = spreadsheet.worksheets()
            if len(worksheet_list) < 3:
                spreadsheet.add_worksheet(title="products", rows=1000, cols=20)
                spreadsheet.add_worksheet(title="sales", rows=1000, cols=15)
                spreadsheet.add_worksheet(title="inventory_log", rows=1000, cols=10)
            
            SPREADSHEET_ID = spreadsheet.id
            st.success(f"✅ تم إنشاء ورقة جديدة. معرف الورقة: {SPREADSHEET_ID}")
        
        st.session_state.gsheet_initialized = True
        return spreadsheet
    
    except Exception as e:
        st.error(f"❌ خطأ في إعداد Google Sheets: {str(e)}")
        st.info("💡 يمكنك استخدام النظام بالتخزين المحلي لحين حل المشكلة")
        return None

# --------------------------
# دوال إدارة Google Sheets
# --------------------------
def load_products_from_sheets():
    """تحميل المنتجات من Google Sheets"""
    try:
        if st.session_state.gsheet_client:
            worksheet = st.session_state.gsheet_client.worksheet("products")
            data = worksheet.get_all_records()
            
            # تحويل البيانات
            products = []
            for row in data:
                if row.get('barcode'):  # تجاهل الصفوف الفارغة
                    products.append(row)
            
            st.session_state.products = products
            
            # تحديث مجموعة الباركودات
            barcodes = {str(p['barcode']) for p in products if p.get('barcode')}
            st.session_state.barcodes = barcodes
            
            return products
    except Exception as e:
        st.warning(f"⚠️ تعذر تحميل المنتجات من Google Sheets: {e}")
    
    return []

def save_product_to_sheets(product):
    """حفظ منتج جديد في Google Sheets"""
    try:
        if st.session_state.gsheet_client:
            worksheet = st.session_state.gsheet_client.worksheet("products")
            
            # تحويل المنتج إلى قائمة
            headers = [
                'barcode', 'product_name', 'category', 'sub_category', 
                'brand', 'size', 'color', 'material', 'season', 'gender',
                'quantity', 'min_stock', 'max_stock', 
                'purchase_price', 'selling_price', 'wholesale_price',
                'supplier', 'supplier_code', 'supplier_contact',
                'date_added', 'last_updated', 'expiry_date',
                'description', 'notes', 'image_url', 'is_active'
            ]
            
            row = [product.get(header, '') for header in headers]
            
            # إضافة الصف الجديد
            worksheet.append_row(row)
            
            st.success(f"✅ تم حفظ المنتج في Google Sheets")
            return True
    except Exception as e:
        st.error(f"❌ خطأ في حفظ المنتج: {e}")
    
    return False

def update_product_in_sheets(barcode, updates):
    """تحديث بيانات منتج في Google Sheets"""
    try:
        if st.session_state.gsheet_client:
            worksheet = st.session_state.gsheet_client.worksheet("products")
            
            # البحث عن الصف باستخدام الباركود
            cell = worksheet.find(str(barcode))
            if cell:
                row_num = cell.row
                
                # تحديث الحقول المطلوبة
                headers = worksheet.row_values(1)
                current_row = worksheet.row_values(row_num)
                
                # تحديث الحقول
                for key, value in updates.items():
                    if key in headers:
                        col_idx = headers.index(key) + 1
                        worksheet.update_cell(row_num, col_idx, value)
                
                return True
    except Exception as e:
        st.error(f"❌ خطأ في تحديث المنتج: {e}")
    
    return False

def save_sale_to_sheets(sale_data):
    """حفظ عملية بيع في Google Sheets"""
    try:
        if st.session_state.gsheet_client:
            worksheet = st.session_state.gsheet_client.worksheet("sales")
            
            row = [
                sale_data['sale_id'],
                sale_data['date_time'],
                sale_data['customer_name'] if 'customer_name' in sale_data else 'مشترٍ عام',
                sale_data['customer_phone'] if 'customer_phone' in sale_data else '',
                sale_data['payment_method'] if 'payment_method' in sale_data else 'نقدي',
                sale_data['items_count'],
                sale_data['total_quantity'],
                sale_data['subtotal'],
                sale_data['discount'],
                sale_data['tax'] if 'tax' in sale_data else 0.0,
                sale_data['total_amount'],
                sale_data['cash_received'],
                sale_data['change_amount'],
                sale_data['seller_name'] if 'seller_name' in sale_data else 'نظام',
                sale_data['notes'] if 'notes' in sale_data else ''
            ]
            
            worksheet.append_row(row)
            
            # حفظ تفاصيل المنتجات المباعة
            for item in sale_data.get('items', []):
                detail_worksheet = st.session_state.gsheet_client.worksheet("sales")
                detail_row = [
                    sale_data['sale_id'],
                    item['barcode'],
                    item['product_name'],
                    item['size'],
                    item['color'],
                    item['quantity'],
                    item['unit_price'],
                    item['total_price'],
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ]
                # يمكن إضافة ورقة منفصلة للتفاصيل
                # نستخدم نفس الورقة مع عمود إضافي
                
            return True
    except Exception as e:
        st.error(f"❌ خطأ في حفظ عملية البيع: {e}")
    
    return False

# --------------------------
# دوال المساعدة
# --------------------------
def generate_barcode():
    """إنشاء باركود فريد مكون من 12 رقم"""
    while True:
        # EAN-13 style (12 رقم + checksum)
        barcode = ''.join(random.choices(string.digits, k=12))
        
        # حساب checksum (مبسط)
        digits = [int(d) for d in barcode]
        odd_sum = sum(digits[::2])
        even_sum = sum(digits[1::2])
        checksum = (10 - ((odd_sum * 3 + even_sum) % 10)) % 10
        
        full_barcode = barcode + str(checksum)
        
        # التحقق من التكرار
        if full_barcode not in st.session_state.barcodes:
            st.session_state.barcodes.add(full_barcode)
            return full_barcode

def validate_barcode(barcode):
    """التحقق من صحة الباركود"""
    if not barcode or not str(barcode).strip():
        return False, "الباركود لا يمكن أن يكون فارغاً"
    
    barcode_str = str(barcode).strip()
    
    # التحقق من الطول (يمكن أن يكون 6-13 رقم)
    if len(barcode_str) < 6 or len(barcode_str) > 13:
        return False, "الباركود يجب أن يكون بين 6 و 13 رقم"
    
    # التحقق من أن كل المحارف أرقام
    if not barcode_str.isdigit():
        return False, "الباركود يجب أن يحتوي على أرقام فقط"
    
    return True, "الباركود صالح"

def format_currency(amount):
    """تنسيق المبالغ المالية"""
    return f"£{amount:,.2f}"

# --------------------------
# صفحة تسجيل المنتجات الموسعة
# --------------------------
def product_registration_page():
    st.title("📦 تسجيل المنتجات الجديدة (نسخة موسعة)")
    
    # تحميل المنتجات الحالية
    if not st.session_state.products:
        load_products_from_sheets()
    
    with st.form("product_form_expanded", clear_on_submit=True):
        # قسم الباركود - مع خيارات متعددة
        st.subheader("🔖 نظام الباركود المتقدم")
        
        col1, col2 = st.columns(2)
        
        with col1:
            barcode_method = st.radio(
                "اختر طريقة إدخال الباركود:",
                ["📱 قراءة تلقائية من الجهاز", "⌨️ إدخال يدوي", "🔢 توليد تلقائي"],
                index=2
            )
            
            if barcode_method == "📱 قراءة تلقائية من الجهاز":
                st.info("تأكد من توصيل قارئ الباركود")
                # محاكاة القراءة التلقائية
                if st.button("🔍 محاكاة قراءة باركود"):
                    # في التطبيق الحقيقي، هنا يتم قراءة الباركود من الجهاز
                    scanned_barcode = generate_barcode()
                    st.session_state.scanned_barcode = scanned_barcode
                    st.success(f"تم قراءة الباركود: {scanned_barcode}")
                
                barcode = st.text_input(
                    "الباركود المقروء",
                    value=st.session_state.get('scanned_barcode', ''),
                    disabled=True
                )
                
            elif barcode_method == "⌨️ إدخال يدوي":
                barcode = st.text_input(
                    "أدخل الباركود يدوياً",
                    placeholder="أدخل 6-13 رقم",
                    max_chars=13,
                    help="يمكن إدخال باركود جاهز للمنتج"
                )
                
                if barcode:
                    is_valid, message = validate_barcode(barcode)
                    if not is_valid:
                        st.error(message)
                    else:
                        st.success("✅ الباركود صالح")
                
            else:  # توليد تلقائي
                barcode = generate_barcode()
                st.info(f"الباركود التلقائي المولد: **{barcode}**")
                st.write("يمكنك نسخه للاستخدام: ", barcode)
        
        with col2:
            # التحقق من تكرار الباركود
            if barcode and barcode in st.session_state.barcodes:
                st.error("⚠️ هذا الباركود مسجل مسبقاً!")
                st.write("المنتج الحالي بهذا الباركود:")
                existing_product = next(
                    (p for p in st.session_state.products 
                     if str(p.get('barcode')) == str(barcode)), 
                    None
                )
                if existing_product:
                    st.write(f"**الاسم:** {existing_product.get('product_name', 'غير معروف')}")
                    st.write(f"**الفئة:** {existing_product.get('category', 'غير معروف')}")
        
        st.markdown("---")
        
        # بيانات المنتج الأساسية
        st.subheader("📋 المعلومات الأساسية")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            product_name = st.text_input("اسم المنتج *", placeholder="مثال: تيشيرت قطني أبيض")
            category = st.selectbox(
                "الفئة الرئيسية *",
                ["تيشيرتات", "بلوزات", "كنزات", "جاكيتات", "معاطف",
                 "بناطيل", "جينز", "شورتات", "فساتين", "تنانير",
                 "ملابس داخلية", "ملابس نوم", "ملابس رياضية",
                 "أحذية", "حقائب", "إكسسوارات", "أخرى"]
            )
            sub_category = st.text_input("الفئة الفرعية", placeholder="مثال: تيشيرتات قصيرة الأكمام")
            brand = st.text_input("الماركة/العلامة التجارية", placeholder="مثال: Nike, Zara")
        
        with col2:
            size = st.multiselect(
                "المقاسات المتاحة *",
                ["XS", "S", "M", "L", "XL", "XXL", "XXXL", "مقاس واحد"],
                default=["M", "L"]
            )
            color = st.multiselect(
                "الألوان المتاحة *",
                ["أبيض", "أسود", "أحمر", "أزرق", "أخضر", "أصفر", 
                 "وردي", "رمادي", "بني", "بيج", "أرجواني", "برتقالي",
                 "متعدد الألوان", "أخرى"],
                default=["أبيض", "أسود"]
            )
            material = st.text_input("المادة الخام", placeholder="مثال: 100% قطن، بوليستر")
            season = st.selectbox(
                "الموسم",
                ["جميع المواسم", "صيف", "شتاء", "ربيع", "خريف", "رمضان"]
            )
        
        with col3:
            gender = st.selectbox(
                "النوع",
                ["رجالي", "حريمي", "أطفال", "بناتي", "جميع الأفراد"]
            )
            expiry_date = st.date_input(
                "تاريخ الصلاحية (إن وجد)",
                value=None,
                min_value=datetime.now().date(),
                help="للمنتجات القابلة للتلف"
            )
            is_active = st.checkbox("المنتج متاح للبيع", value=True)
        
        st.markdown("---")
        
        # معلومات المخزون والأسعار
        st.subheader("💰 الأسعار والمخزون")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            quantity = st.number_input("الكمية المتاحة *", min_value=0, value=10, step=1)
            min_stock = st.number_input("الحد الأدنى للمخزون", min_value=0, value=5, step=1)
            max_stock = st.number_input("الحد الأقصى للمخزون", min_value=0, value=100, step=1)
        
        with col2:
            purchase_price = st.number_input("سعر الشراء *", min_value=0.0, value=50.0, step=1.0)
            selling_price = st.number_input("سعر البيع *", min_value=0.0, value=80.0, step=1.0)
            wholesale_price = st.number_input("سعر الجملة", min_value=0.0, value=65.0, step=1.0)
        
        with col3:
            discount_price = st.number_input("سعر التخفيض", min_value=0.0, value=0.0, step=1.0)
            if discount_price > 0:
                discount_percent = ((selling_price - discount_price) / selling_price) * 100
                st.metric("نسبة التخفيض", f"{discount_percent:.1f}%")
        
        st.markdown("---")
        
        # معلومات المورد
        st.subheader("🏢 معلومات المورد")
        
        col1, col2 = st.columns(2)
        
        with col1:
            supplier = st.text_input("اسم المورد *", placeholder="مثال: شركة النسيج المتحد")
            supplier_code = st.text_input("كود المورد", placeholder="كود التعريف بالمورد")
        
        with col2:
            supplier_contact = st.text_input("جهة اتصال المورد", placeholder="رقم الهاتف أو البريد")
            supplier_rating = st.slider("تقييم المورد", 1, 5, 3)
        
        st.markdown("---")
        
        # معلومات إضافية
        st.subheader("📝 معلومات إضافية")
        
        description = st.text_area(
            "وصف تفصيلي للمنتج",
            height=100,
            placeholder="وصف كامل للمنتج، الجودة، المميزات..."
        )
        
        notes = st.text_area(
            "ملاحظات خاصة",
            height=80,
            placeholder="ملاحظات خاصة للمنتج، نصائح للعرض..."
        )
        
        # رفع صورة المنتج
        uploaded_image = st.file_uploader(
            "رفع صورة للمنتج (اختياري)",
            type=['jpg', 'jpeg', 'png', 'gif'],
            help="حجم الصورة المفضل: 800x800 بكسل"
        )
        
        image_url = ""
        if uploaded_image:
            st.image(uploaded_image, caption="صورة المنتج", width=200)
            # في التطبيق الحقيقي، هنا يتم رفع الصورة لسيرفر أو تخزينها
            image_url = f"uploaded/{uploaded_image.name}"
        
        st.markdown("---")
        
        # أزرار التحكم
        col1, col2, col3 = st.columns(3)
        
        with col2:
            submitted = st.form_submit_button(
                "💾 حفظ المنتج في Google Sheets",
                type="primary",
                use_container_width=True
            )
        
        if submitted:
            # التحقق من البيانات المطلوبة
            required_fields = {
                'اسم المنتج': product_name,
                'الفئة': category,
                'المقاسات': size,
                'الألوان': color,
                'الكمية': quantity > 0,
                'سعر الشراء': purchase_price > 0,
                'سعر البيع': selling_price > 0,
                'المورد': supplier
            }
            
            missing_fields = [field for field, value in required_fields.items() if not value]
            
            if missing_fields:
                st.error(f"❌ الرجاء ملء الحقول المطلوبة: {', '.join(missing_fields)}")
            else:
                # إنشاء كائن المنتج
                product = {
                    'barcode': barcode,
                    'product_name': product_name,
                    'category': category,
                    'sub_category': sub_category if sub_category else '',
                    'brand': brand if brand else '',
                    'size': ','.join(size) if size else '',
                    'color': ','.join(color) if color else '',
                    'material': material if material else '',
                    'season': season,
                    'gender': gender,
                    'quantity': int(quantity),
                    'min_stock': int(min_stock),
                    'max_stock': int(max_stock),
                    'purchase_price': float(purchase_price),
                    'selling_price': float(selling_price),
                    'wholesale_price': float(wholesale_price) if wholesale_price else 0.0,
                    'discount_price': float(discount_price) if discount_price else 0.0,
                    'supplier': supplier,
                    'supplier_code': supplier_code if supplier_code else '',
                    'supplier_contact': supplier_contact if supplier_contact else '',
                    'supplier_rating': int(supplier_rating),
                    'date_added': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'expiry_date': expiry_date.strftime("%Y-%m-%d") if expiry_date else '',
                    'description': description if description else '',
                    'notes': notes if notes else '',
                    'image_url': image_url,
                    'is_active': is_active
                }
                
                # حفظ المنتج
                save_success = save_product_to_sheets(product)
                
                if save_success:
                    st.success(f"✅ تم حفظ المنتج '{product_name}' بنجاح في Google Sheets!")
                    st.balloons()
                    
                    # تحديث البيانات المحلية
                    st.session_state.products.append(product)
                    st.session_state.barcodes.add(barcode)
                    
                    # عرض ملخص
                    with st.expander("📄 عرض ملخص المنتج المسجل", expanded=True):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**المعلومات الأساسية:**")
                            st.write(f"- **الباركود:** {barcode}")
                            st.write(f"- **الاسم:** {product_name}")
                            st.write(f"- **الفئة:** {category}")
                            st.write(f"- **المقاسات:** {', '.join(size)}")
                            st.write(f"- **الألوان:** {', '.join(color)}")
                            st.write(f"- **المورد:** {supplier}")
                        
                        with col2:
                            st.write("**المعلومات المالية:**")
                            st.write(f"- **الكمية:** {quantity}")
                            st.write(f"- **سعر الشراء:** {format_currency(purchase_price)}")
                            st.write(f"- **سعر البيع:** {format_currency(selling_price)}")
                            if discount_price > 0:
                                st.write(f"- **سعر التخفيض:** {format_currency(discount_price)}")
                            st.write(f"- **القيمة الإجمالية:** {format_currency(quantity * selling_price)}")
                else:
                    st.error("❌ حدث خطأ أثناء حفظ المنتج. يرجى المحاولة مرة أخرى.")

# --------------------------
# صفحة المبيعات المتقدمة
# --------------------------
def advanced_sales_page():
    st.title("💰 شاشة المبيعات المتقدمة")
    
    # تحميل المنتجات إذا لم تكن محملة
    if not st.session_state.products:
        load_products_from_sheets()
    
    # شريط التحكم العلوي
    st.subheader("🔍 البحث والمسح")
    
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        # خيارات إدخال الباركود
        input_method = st.radio(
            "طريقة الإدخال:",
            ["⌨️ إدخال يدوي", "📱 مسح ضوئي تلقائي", "📁 ملف دفعة"],
            horizontal=True,
            key="input_method"
        )
        
        if input_method == "⌨️ إدخال يدوي":
            barcode_input = st.text_input(
                "أدخل باركود المنتج",
                placeholder="أدخل 6-13 رقم أو استخدم الماسح الضوئي",
                key="barcode_manual",
                help="اضغط Enter بعد إدخال الباركود"
            )
            
        elif input_method == "📱 مسح ضوئي تلقائي":
            # محاكاة الماسح الضوئي
            if st.button("🔍 بدء المسح الضوئي", type="primary"):
                # في التطبيق الحقيقي، هنا يتم انتظار إشارة من الماسح
                st.info("جاهز لقراءة الباركود... ضع المنتج أمام الماسح")
                
                # محاكاة قراءة باركود عشوائي
                time.sleep(2)  # محاكاة وقت المسح
                
                if st.session_state.products:
                    random_product = random.choice(st.session_state.products)
                    barcode_input = random_product['barcode']
                    st.session_state.scanned_barcode = barcode_input
                    st.success(f"تم قراءة الباركود: {barcode_input}")
                    st.rerun()
            
            barcode_input = st.text_input(
                "الباركود المقروء",
                value=st.session_state.get('scanned_barcode', ''),
                disabled=True
            )
            
        else:  # ملف دفعة
            uploaded_file = st.file_uploader(
                "رفع ملف CSV يحتوي على باركودات",
                type=['csv', 'txt'],
                help="يجب أن يحتوي الملف على عمود باسم 'barcode'"
            )
            
            if uploaded_file is not None:
                try:
                    df = pd.read_csv(uploaded_file)
                    if 'barcode' in df.columns:
                        barcodes = df['barcode'].astype(str).tolist()
                        st.success(f"تم تحميل {len(barcodes)} باركود")
                        
                        # معالجة الباركودات
                        for barcode in barcodes:
                            add_product_to_sale(barcode)
                        
                        st.rerun()
                except Exception as e:
                    st.error(f"خطأ في قراءة الملف: {e}")
    
    with col2:
        st.write("")
        st.write("")
        if st.button("🔄 تحديث القائمة", type="secondary"):
            load_products_from_sheets()
            st.rerun()
    
    with col3:
        st.write("")
        st.write("")
        if st.button("📊 عرض المخزون", type="secondary"):
            st.session_state.show_inventory = True
    
    # البحث عن المنتج عند إدخال باركود
    if 'barcode_input' in locals() and barcode_input:
        product_found = None
        
        for product in st.session_state.products:
            if str(product.get('barcode', '')).strip() == str(barcode_input).strip():
                product_found = product
                break
        
        if product_found:
            add_product_to_sale(product_found, barcode_input)
        else:
            st.error(f"❌ الباركود '{barcode_input}' غير موجود في قاعدة البيانات!")
            
            # خيار البحث اليدوي
            if st.button("🔎 البحث اليدوي عن المنتج"):
                st.session_state.show_manual_search = True
    
    # البحث اليدوي
    if st.session_state.get('show_manual_search', False):
        st.subheader("🔍 البحث اليدوي عن المنتجات")
        
        search_col1, search_col2 = st.columns([3, 1])
        
        with search_col1:
            search_term = st.text_input(
                "ابحث باسم المنتج، الفئة، الماركة، اللون...",
                placeholder="مثال: تيشيرت قطني أبيض"
            )
        
        with search_col2:
            st.write("")
            if st.button("بحث", type="primary"):
                if search_term:
                    search_results = []
                    for product in st.session_state.products:
                        search_fields = [
                            str(product.get('product_name', '')),
                            str(product.get('category', '')),
                            str(product.get('brand', '')),
                            str(product.get('color', '')),
                            str(product.get('description', ''))
                        ]
                        
                        if any(search_term.lower() in field.lower() for field in search_fields):
                            search_results.append(product)
                    
                    st.session_state.search_results = search_results
        
        # عرض نتائج البحث
        if st.session_state.get('search_results'):
            st.write(f"**تم العثور على {len(st.session_state.search_results)} منتج:**")
            
            for idx, product in enumerate(st.session_state.search_results[:10]):  # عرض أول 10 نتائج
                with st.expander(f"{product.get('product_name')} - باركود: {product.get('barcode')}"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**الفئة:** {product.get('category', 'غير معروف')}")
                        st.write(f"**المقاس:** {product.get('size', 'غير معروف')}")
                        st.write(f"**اللون:** {product.get('color', 'غير معروف')}")
                        st.write(f"**المخزون:** {product.get('quantity', 0)}")
                        st.write(f"**سعر البيع:** {format_currency(product.get('selling_price', 0))}")
                    
                    with col2:
                        if product.get('quantity', 0) > 0:
                            qty_to_sell = st.number_input(
                                "الكمية",
                                min_value=1,
                                max_value=product.get('quantity', 1),
                                value=1,
                                key=f"qty_{idx}"
                            )
                            
                            if st.button(f"إضافة للبيع", key=f"add_{idx}"):
                                add_product_to_sale(product, product.get('barcode'), qty_to_sell)
                                st.success(f"تمت الإضافة!")
                                time.sleep(1)
                                st.rerun()
                        else:
                            st.warning("⛔ غير متوفر")
    
    # عرض عناصر البيع الحالية
    st.markdown("---")
    st.subheader("🛒 عربة التسوق")
    
    if not st.session_state.current_sale_items:
        st.info("لا توجد عناصر في عربة التسوق. أضف منتجات باستخدام الباركود.")
    else:
        # جدول العناصر
        sale_df = pd.DataFrame(st.session_state.current_sale_items)
        
        # عرض الجدول مع إمكانية التعديل
        edited_df = st.data_editor(
            sale_df,
            column_config={
                "product_name": st.column_config.TextColumn("المنتج"),
                "barcode": st.column_config.TextColumn("الباركود"),
                "quantity": st.column_config.NumberColumn(
                    "الكمية",
                    min_value=1,
                    max_value=1000,
                    step=1
                ),
                "unit_price": st.column_config.NumberColumn("سعر الوحدة", format="%.2f"),
                "total_price": st.column_config.NumberColumn("الإجمالي", format="%.2f"),
                "remove": st.column_config.CheckboxColumn("إزالة")
            },
            hide_index=True,
            use_container_width=True
        )
        
        # تحديث العناصر بناءً على التعديلات
        for idx, item in enumerate(st.session_state.current_sale_items):
            if idx < len(edited_df):
                new_qty = edited_df.iloc[idx]['quantity']
                if new_qty != item['quantity']:
                    item['quantity'] = new_qty
                    item['total_price'] = new_qty * item['unit_price']
                
                if edited_df.iloc[idx]['remove']:
                    st.session_state.current_sale_items.pop(idx)
                    st.rerun()
        
        # حساب الإجماليات
        subtotal = sum(item['total_price'] for item in st.session_state.current_sale_items)
        total_quantity = sum(item['quantity'] for item in st.session_state.current_sale_items)
        
        # قسم الخصم والدفع
        st.markdown("---")
        st.subheader("💳 الدفع والخروج")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            discount_type = st.radio(
                "نوع الخصم",
                ["بدون خصم", "نسبة مئوية %", "مبلغ ثابت"],
                horizontal=True
            )
            
            if discount_type == "نسبة مئوية %":
                discount_percent = st.slider("نسبة الخصم %", 0, 100, 0)
                discount_amount = subtotal * (discount_percent / 100)
            elif discount_type == "مبلغ ثابت":
                discount_amount = st.number_input("مبلغ الخصم", min_value=0.0, max_value=subtotal, value=0.0)
            else:
                discount_amount = 0.0
            
            tax_rate = st.number_input("ضريبة القيمة المضافة %", min_value=0.0, value=14.0)
            tax_amount = (subtotal - discount_amount) * (tax_rate / 100)
            
            total_amount = subtotal - discount_amount + tax_amount
        
        with col2:
            st.metric("الإجمالي الجزئي", format_currency(subtotal))
            st.metric("الخصم", format_currency(discount_amount))
            st.metric("الضريبة", format_currency(tax_amount))
            st.metric("**المبلغ الإجمالي**", format_currency(total_amount), delta_color="off")
        
        with col3:
            payment_method = st.selectbox(
                "طريقة الدفع",
                ["نقدي", "بطاقة ائتمان", "بطاقة مدى", "تحويل بنكي", "أخرى"]
            )
            
            if payment_method == "نقدي":
                cash_received = st.number_input(
                    "المبلغ المستلم",
                    min_value=0.0,
                    value=float(total_amount),
                    step=50.0
                )
                
                change_amount = cash_received - total_amount
                if change_amount > 0:
                    st.success(f"الباقي: {format_currency(change_amount)}")
                elif change_amount < 0:
                    st.error(f"المبلغ غير كافي: {format_currency(abs(change_amount))}")
            else:
                cash_received = total_amount
                change_amount = 0.0
            
            customer_name = st.text_input("اسم العميل (اختياري)", placeholder="أدخل اسم العميل")
            customer_phone = st.text_input("هاتف العميل (اختياري)", placeholder="رقم الهاتف")
        
        # زر إتمام البيع
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("✅ إتمام عملية البيع", type="primary", use_container_width=True):
                if total_amount <= 0:
                    st.error("لا يمكن إتمام بيع بقيمة صفر!")
                else:
                    # إنشاء سجل البيع
                    sale_id = f"SALE{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    
                    sale_data = {
                        'sale_id': sale_id,
                        'date_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'customer_name': customer_name,
                        'customer_phone': customer_phone,
                        'payment_method': payment_method,
                        'items_count': len(st.session_state.current_sale_items),
                        'total_quantity': total_quantity,
                        'subtotal': subtotal,
                        'discount': discount_amount,
                        'tax': tax_amount,
                        'total_amount': total_amount,
                        'cash_received': cash_received,
                        'change_amount': change_amount,
                        'seller_name': 'نظام',
                        'items': st.session_state.current_sale_items.copy(),
                        'notes': ''
                    }
                    
                    # حفظ في Google Sheets
                    save_success = save_sale_to_sheets(sale_data)
                    
                    if save_success:
                        # تحديث المخزون
                        for item in st.session_state.current_sale_items:
                            for product in st.session_state.products:
                                if str(product.get('barcode')) == str(item.get('barcode')):
                                    new_qty = product.get('quantity', 0) - item.get('quantity', 0)
                                    update_product_in_sheets(
                                        item.get('barcode'),
                                        {'quantity': new_qty, 'last_updated': sale_data['date_time']}
                                    )
                                    product['quantity'] = new_qty
                        
                        st.success(f"✅ تم إتمام عملية البيع رقم: {sale_id}")
                        st.balloons()
                        
                        # عرض الفاتورة
                        with st.expander("📄 عرض فاتورة البيع", expanded=True):
                            display_invoice(sale_data)
                        
                        # إعادة تعيين عربة التسوق
                        st.session_state.current_sale_items = []
                        st.session_state.sale_total = 0.0
                        st.session_state.sale_discount = 0.0
                        
                        # خيار طباعة الفاتورة
                        if st.button("🖨️ طباعة الفاتورة"):
                            generate_invoice_pdf(sale_data)
                    else:
                        st.error("❌ حدث خطأ أثناء حفظ عملية البيع!")

def add_product_to_sale(product, barcode=None, quantity=1):
    """إضافة منتج إلى عربة التسوق"""
    if not product:
        return
    
    # استخدام الباركود الممرر أو باركود المنتج
    actual_barcode = barcode if barcode else product.get('barcode')
    
    # التحقق من توفر الكمية
    available_qty = product.get('quantity', 0)
    
    if available_qty <= 0:
        st.error(f"⛔ المنتج '{product.get('product_name')}' غير متوفر في المخزون!")
        return
    
    if quantity > available_qty:
        st.warning(f"⚠️ الكمية المطلوبة ({quantity}) أكبر من المخزون المتاح ({available_qty})")
        quantity = available_qty
    
    # البحث إذا كان المنتج مضافاً مسبقاً
    for item in st.session_state.current_sale_items:
        if item.get('barcode') == actual_barcode:
            new_total_qty = item['quantity'] + quantity
            
            if new_total_qty <= available_qty:
                item['quantity'] = new_total_qty
                item['total_price'] = new_total_qty * item['unit_price']
                st.success(f"تم تحديث كمية '{product.get('product_name')}' إلى {new_total_qty}")
            else:
                st.warning(f"الكمية الإجمالية ({new_total_qty}) تتجاوز المخزون ({available_qty})")
            return
    
    # إضافة منتج جديد
    sale_price = product.get('discount_price', 0) or product.get('selling_price', 0)
    
    new_item = {
        'barcode': actual_barcode,
        'product_name': product.get('product_name', 'غير معروف'),
        'category': product.get('category', ''),
        'size': product.get('size', ''),
        'color': product.get('color', ''),
        'quantity': quantity,
        'unit_price': float(sale_price),
        'total_price': float(sale_price) * quantity,
        'remove': False
    }
    
    st.session_state.current_sale_items.append(new_item)
    st.success(f"تمت إضافة '{product.get('product_name')}' إلى عربة التسوق")

def display_invoice(sale_data):
    """عرض فاتورة البيع"""
    st.write(f"**رقم الفاتورة:** {sale_data['sale_id']}")
    st.write(f"**التاريخ والوقت:** {sale_data['date_time']}")
    
    if sale_data.get('customer_name'):
        st.write(f"**اسم العميل:** {sale_data['customer_name']}")
    if sale_data.get('customer_phone'):
        st.write(f"**هاتف العميل:** {sale_data['customer_phone']}")
    
    st.write("---")
    
    # جدول العناصر
    items_df = pd.DataFrame(sale_data['items'])
    st.dataframe(
        items_df[['product_name', 'quantity', 'unit_price', 'total_price']],
        column_config={
            'product_name': 'المنتج',
            'quantity': 'الكمية',
            'unit_price': st.column_config.NumberColumn('سعر الوحدة', format="%.2f"),
            'total_price': st.column_config.NumberColumn('الإجمالي', format="%.2f")
        },
        hide_index=True
    )
    
    st.write("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**الإجمالي الجزئي:** {format_currency(sale_data['subtotal'])}")
        st.write(f"**الخصم:** {format_currency(sale_data['discount'])}")
        st.write(f"**الضريبة ({sale_data.get('tax_rate', 14)}%):** {format_currency(sale_data['tax'])}")
        st.write(f"**طريقة الدفع:** {sale_data['payment_method']}")
    
    with col2:
        st.write(f"**المبلغ المستلم:** {format_currency(sale_data['cash_received'])}")
        if sale_data.get('change_amount', 0) > 0:
            st.write(f"**الباقي:** {format_currency(sale_data['change_amount'])}")
        
        st.markdown(f"### **المبلغ الإجمالي: {format_currency(sale_data['total_amount'])}**")
    
    st.write("---")
    st.write("**شكراً لشرائك! نرجو زيارتنا مجدداً**")

def generate_invoice_pdf(sale_data):
    """إنشاء فاتورة PDF (مبسط)"""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import mm
        
        # إنشاء PDF في الذاكرة
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # إضافة المحتوى
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, "فاتورة بيع - محل الملابس")
        
        c.setFont("Helvetica", 10)
        c.drawString(50, height - 80, f"رقم الفاتورة: {sale_data['sale_id']}")
        c.drawString(50, height - 100, f"التاريخ: {sale_data['date_time']}")
        
        # حفظ PDF
        c.save()
        
        buffer.seek(0)
        
        # زر التحميل
        st.download_button(
            label="📥 تحميل الفاتورة PDF",
            data=buffer,
            file_name=f"invoice_{sale_data['sale_id']}.pdf",
            mime="application/pdf"
        )
        
    except ImportError:
        st.warning("لإنشاء فواتير PDF، قم بتثبيت: `pip install reportlab`")

# --------------------------
# الصفحات الأخرى (مختصرة)
# --------------------------
def inventory_reports_page():
    st.title("📊 تقارير المخزون والمبيعات")
    st.write("تحميل البيانات من Google Sheets...")
    
    if st.session_state.gsheet_client:
        products = load_products_from_sheets()
        
        if products:
            df = pd.DataFrame(products)
            
            # عرض التقارير
            st.subheader("إحصائيات المخزون")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("إجمالي المنتجات", len(df))
            with col2:
                st.metric("إجمالي القطع", int(df['quantity'].sum()))
            with col3:
                st.metric("القيمة الإجمالية", format_currency((df['quantity'] * df['selling_price']).sum()))
            with col4:
                low_stock = df[df['quantity'] <= df['min_stock']]
                st.metric("منتجات منخفضة المخزون", len(low_stock), delta=f"-{len(low_stock)}")
            
            # المزيد من التقارير...
        else:
            st.warning("لا توجد بيانات في Google Sheets")
    else:
        st.warning("Google Sheets غير متصل")

def settings_page():
    st.title("⚙️ إعدادات النظام")
    
    st.subheader("إعدادات Google Sheets")
    
    if st.button("🔗 اختبار اتصال Google Sheets"):
        client = setup_google_sheets()
        if client:
            st.success("✅ الاتصال بـ Google Sheets يعمل بنجاح!")
        else:
            st.error("❌ فشل الاتصال بـ Google Sheets")
    
    st.subheader("إدارة البيانات")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 مزامنة البيانات من Google Sheets"):
            load_products_from_sheets()
            st.success("تمت المزامنة!")
    
    with col2:
        if st.button("🧹 مسح الذاكرة المؤقتة"):
            st.session_state.current_sale_items = []
            st.session_state.search_results = []
            st.success("تم مسح الذاكرة المؤقتة!")

# --------------------------
# القائمة الرئيسية
# --------------------------
def main():
    # الشريط الجانبي
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3082/3082383.png", width=80)
        st.title("👕 متجر الملابس")
        st.markdown("---")
        
        # حالة الاتصال
        if st.session_state.gsheet_initialized:
            st.success("✅ متصل بـ Google Sheets")
        else:
            st.warning("⚠️ غير متصل بـ Google Sheets")
        
        st.markdown("---")
        
        # القائمة
        menu_options = [
            "📦 تسجيل المنتجات الموسع",
            "💰 شاشة المبيعات المتقدمة", 
            "📊 تقارير المخزون",
            "⚙️ الإعدادات"
        ]
        
        selected_page = st.radio(
            "القائمة الرئيسية",
            menu_options,
            index=0
        )
        
        st.markdown("---")
        
        # إحصائيات سريعة
        st.write("**الإحصائيات:**")
        st.write(f"• المنتجات: {len(st.session_state.products)}")
        
        if st.session_state.current_sale_items:
            st.write(f"• عناصر البيع: {len(st.session_state.current_sale_items)}")
        
        st.markdown("---")
        
        # معلومات النظام
        st.caption(f"الإصدار 2.0 | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        if st.button("🔄 تحديث الصفحة"):
            st.rerun()
    
    # تحميل Google Sheets عند التشغيل
    if not st.session_state.gsheet_initialized:
        with st.spinner("جارٍ الاتصال بـ Google Sheets..."):
            client = setup_google_sheets()
            if client:
                st.session_state.gsheet_client = client
                load_products_from_sheets()
            else:
                st.warning("يعمل النظام بالتخزين المحلي فقط")
    
    # تحميل الصفحة المحددة
    if "تسجيل المنتجات" in selected_page:
        product_registration_page()
    elif "شاشة المبيعات" in selected_page:
        advanced_sales_page()
    elif "تقارير المخزون" in selected_page:
        inventory_reports_page()
    elif "الإعدادات" in selected_page:
        settings_page()

# --------------------------
# تشغيل التطبيق
# --------------------------
if __name__ == "__main__":
    main()