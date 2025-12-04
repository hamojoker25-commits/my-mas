"""
نظام إدارة محل ملابس متكامل
مميزات: تسجيل منتجات - باركود تلقائي - جوجل شيت - مبيعات
"""

import streamlit as st
import pandas as pd
import numpy as np
import random
import string
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import time

# --------------------------
# إعدادات الجلسة
# --------------------------
if 'products' not in st.session_state:
    st.session_state.products = []
if 'sales' not in st.session_state:
    st.session_state.sales = []
if 'barcodes' not in st.session_state:
    st.session_state.barcodes = set()

# --------------------------
# إعدادات جوجل شيت (يمكن استبدالها بملف محلي)
# --------------------------
def setup_google_sheets():
    """إعداد اتصال جوجل شيت"""
    try:
        # هنا تضيف بيانات الاعتماد الخاصة بك
        scope = ["https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive.file",
                "https://www.googleapis.com/auth/drive"]
        
        # طريقة بديلة باستخدام ملف محلي (CSV) إذا لم يكن جوجل شيت متاحاً
        st.info("جارٍ تحميل نظام التخزين المحلي...")
        
        # إنشاء ملفات CSV محلية للتخزين
        try:
            products_df = pd.read_csv('products.csv')
            st.session_state.products = products_df.to_dict('records')
        except:
            st.session_state.products = []
            
        try:
            sales_df = pd.read_csv('sales.csv')
            st.session_state.sales = sales_df.to_dict('records')
        except:
            st.session_state.sales = []
            
        return True
    except Exception as e:
        st.warning(f"سيتم استخدام التخزين المحلي بسبب: {e}")
        return False

# --------------------------
# دوال المساعدة
# --------------------------
def generate_barcode():
    """إنشاء باركود مكون من 6 أرقام عشوائية"""
    while True:
        barcode = ''.join(random.choices(string.digits, k=6))
        if barcode not in st.session_state.barcodes:
            st.session_state.barcodes.add(barcode)
            return barcode

def save_to_csv(data, filename):
    """حفظ البيانات في ملف CSV"""
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False, encoding='utf-8')

def load_from_csv(filename):
    """تحميل البيانات من ملف CSV"""
    try:
        df = pd.read_csv(filename)
        return df.to_dict('records')
    except:
        return []

# --------------------------
# صفحة تسجيل المنتجات
# --------------------------
def product_registration_page():
    st.title("📦 تسجيل المنتجات الجديدة")
    
    with st.form("product_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            # بيانات المنتج الأساسية
            product_name = st.text_input("اسم المنتج", placeholder="مثال: تيشيرت قطني")
            category = st.selectbox(
                "الفئة",
                ["تيشيرتات", "بناطيل", "جاكيتات", "فساتين", "أحذية", "إكسسوارات", "أخرى"]
            )
            size = st.selectbox("المقاس", ["S", "M", "L", "XL", "XXL", "مقاس واحد"])
            color = st.text_input("اللون", placeholder="أبيض، أسود، أزرق...")
            
        with col2:
            # بيانات السعر والكمية
            quantity = st.number_input("الكمية المتاحة", min_value=1, value=1)
            purchase_price = st.number_input("سعر الشراء", min_value=0.0, value=0.0)
            selling_price = st.number_input("سعر البيع", min_value=0.0, value=0.0)
            min_stock = st.number_input("الحد الأدنى للمخزون", min_value=0, value=5)
            
        # قسم الباركود
        st.subheader("🔖 نظام الباركود")
        barcode_option = st.radio("طريقة إدخال الباركود:", 
                                 ["توليد تلقائي (6 أرقام)", "إدخال يدوي"])
        
        if barcode_option == "توليد تلقائي (6 أرقام)":
            barcode = generate_barcode()
            st.info(f"الباركود التلقائي: **{barcode}**")
        else:
            barcode = st.text_input("أدخل الباركود يدوياً (6 أرقام)", 
                                   max_chars=6, 
                                   placeholder="123456")
            if barcode and (len(barcode) != 6 or not barcode.isdigit()):
                st.error("الباركود يجب أن يكون 6 أرقام فقط!")
        
        # معلومات إضافية
        description = st.text_area("وصف المنتج (اختياري)", 
                                  placeholder="وصف تفصيلي للمنتج...")
        
        supplier = st.text_input("المورد (اختياري)", placeholder="اسم المورد")
        
        # زر الحفظ
        submitted = st.form_submit_button("💾 حفظ المنتج")
        
        if submitted:
            if not product_name or not category:
                st.error("الرجاء إدخال اسم المنتج والفئة!")
            elif barcode_option == "إدخال يدوي" and (not barcode or len(barcode) != 6):
                st.error("الباركود غير صالح!")
            else:
                # إنشاء كائن المنتج
                product = {
                    'barcode': barcode if barcode_option == "إدخال يدوي" else barcode,
                    'product_name': product_name,
                    'category': category,
                    'size': size,
                    'color': color,
                    'quantity': int(quantity),
                    'purchase_price': float(purchase_price),
                    'selling_price': float(selling_price),
                    'min_stock': int(min_stock),
                    'description': description,
                    'supplier': supplier,
                    'date_added': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # إضافة المنتج للقائمة
                st.session_state.products.append(product)
                
                # حفظ في CSV
                save_to_csv(st.session_state.products, 'products.csv')
                
                st.success(f"✅ تم حفظ المنتج {product_name} بنجاح!")
                st.balloons()
                
                # عرض تفاصيل المنتج المسجل
                with st.expander("عرض تفاصيل المنتج المسجل"):
                    st.json(product)

# --------------------------
# صفحة المبيعات
# --------------------------
def sales_page():
    st.title("💰 شاشة المبيعات")
    
    # قسم إدخال الباركود
    col1, col2 = st.columns([2, 1])
    
    with col1:
        barcode_input = st.text_input(
            "🔍 أدخل باركود المنتج",
            placeholder="أدخل 6 أرقام أو استخدم الماسح الضوئي",
            key="barcode_input"
        )
    
    with col2:
        st.write("")
        st.write("")
        if st.button("📷 محاكاة الماسح الضوئي", type="secondary"):
            # توليد باركود عشوائي للمحاكاة
            random_barcode = generate_barcode()
            st.session_state.barcode_input = random_barcode
            st.rerun()
    
    # البحث عن المنتج
    product_found = None
    if barcode_input:
        for product in st.session_state.products:
            if str(product['barcode']) == str(barcode_input):
                product_found = product
                break
        
        if product_found:
            st.success(f"✅ تم العثور على المنتج: {product_found['product_name']}")
            
            # عرض تفاصيل المنتج
            with st.container():
                st.subheader("📋 تفاصيل المنتج")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("اسم المنتج", product_found['product_name'])
                    st.metric("الفئة", product_found['category'])
                    st.metric("المقاس", product_found['size'])
                    
                with col2:
                    st.metric("اللون", product_found['color'])
                    st.metric("المخزون المتاح", product_found['quantity'])
                    st.metric("سعر البيع", f"${product_found['selling_price']:.2f}")
                    
                with col3:
                    # إدخال كمية البيع
                    max_qty = product_found['quantity']
                    sale_qty = st.number_input(
                        "الكمية المطلوبة", 
                        min_value=1, 
                        max_value=max_qty,
                        value=1,
                        key="sale_qty"
                    )
                    
                    # حساب السعر الإجمالي
                    total_price = sale_qty * product_found['selling_price']
                    st.metric("المبلغ الإجمالي", f"${total_price:.2f}")
                    
                    # زر تأكيد البيع
                    if st.button("✅ تأكيد عملية البيع", type="primary"):
                        if sale_qty <= product_found['quantity']:
                            # تحديث المخزون
                            product_found['quantity'] -= sale_qty
                            product_found['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            
                            # تسجيل عملية البيع
                            sale_record = {
                                'sale_id': f"SALE{int(time.time())}",
                                'date_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                'barcode': product_found['barcode'],
                                'product_name': product_found['product_name'],
                                'quantity': sale_qty,
                                'unit_price': product_found['selling_price'],
                                'total_price': total_price,
                                'remaining_stock': product_found['quantity']
                            }
                            
                            st.session_state.sales.append(sale_record)
                            
                            # حفظ التحديثات
                            save_to_csv(st.session_state.products, 'products.csv')
                            save_to_csv(st.session_state.sales, 'sales.csv')
                            
                            st.success(f"✅ تم بيع {sale_qty} قطعة بنجاح!")
                            st.balloons()
                            
                            # عرض الفاتورة
                            with st.expander("عرض فاتورة البيع"):
                                st.write("**فاتورة البيع**")
                                st.write(f"رقم العملية: {sale_record['sale_id']}")
                                st.write(f"التاريخ: {sale_record['date_time']}")
                                st.write(f"المنتج: {sale_record['product_name']}")
                                st.write(f"الكمية: {sale_record['quantity']}")
                                st.write(f"سعر الوحدة: ${sale_record['unit_price']:.2f}")
                                st.write(f"**الإجمالي: ${sale_record['total_price']:.2f}**")
                        else:
                            st.error("❌ الكمية المطلوبة غير متوفرة في المخزون!")
        else:
            st.error("❌ الباركود غير موجود في قاعدة البيانات!")
            if st.button("🔄 البحث يدوياً عن المنتج"):
                st.session_state.show_search = True
    
    # قسم البحث اليدوي
    if st.session_state.get('show_search', False):
        st.subheader("🔎 البحث اليدوي عن المنتجات")
        search_term = st.text_input("ابحث باسم المنتج أو الفئة")
        
        if search_term:
            search_results = [
                p for p in st.session_state.products 
                if search_term.lower() in p['product_name'].lower() 
                or search_term.lower() in p['category'].lower()
            ]
            
            if search_results:
                st.write(f"تم العثور على {len(search_results)} منتج:")
                for product in search_results:
                    with st.expander(f"{product['product_name']} - باركود: {product['barcode']}"):
                        st.write(f"**الفئة:** {product['category']}")
                        st.write(f"**المقاس:** {product['size']}")
                        st.write(f"**اللون:** {product['color']}")
                        st.write(f"**المخزون:** {product['quantity']}")
                        st.write(f"**سعر البيع:** ${product['selling_price']:.2f}")
                        
                        # زر اختيار هذا المنتج للبيع
                        if st.button(f"اختر للبيع", key=f"select_{product['barcode']}"):
                            st.session_state.barcode_input = product['barcode']
                            st.session_state.show_search = False
                            st.rerun()
            else:
                st.warning("لم يتم العثور على منتجات تطابق بحثك")

# --------------------------
# صفحة تقارير المخزون
# --------------------------
def inventory_page():
    st.title("📊 تقارير المخزون والمبيعات")
    
    if not st.session_state.products:
        st.warning("لا توجد منتجات مسجلة بعد!")
        return
    
    # تحويل البيانات إلى DataFrame
    df_products = pd.DataFrame(st.session_state.products)
    df_sales = pd.DataFrame(st.session_state.sales) if st.session_state.sales else pd.DataFrame()
    
    # أقسام التبويب
    tab1, tab2, tab3, tab4 = st.tabs(["📦 المخزون الحالي", "💰 المبيعات", "⚠️ تنبيهات", "📈 إحصائيات"])
    
    with tab1:
        st.subheader("قائمة المنتجات الكاملة")
        
        # فلترة البيانات
        col1, col2 = st.columns(2)
        with col1:
            selected_category = st.multiselect(
                "فلترة حسب الفئة",
                options=df_products['category'].unique() if not df_products.empty else [],
                default=[]
            )
        
        with col2:
            min_stock = st.slider("الحد الأدنى للمخزون", 0, 100, 0)
        
        # تطبيق الفلتر
        filtered_df = df_products.copy()
        if selected_category:
            filtered_df = filtered_df[filtered_df['category'].isin(selected_category)]
        filtered_df = filtered_df[filtered_df['quantity'] >= min_stock]
        
        # عرض الجدول
        st.dataframe(
            filtered_df[['barcode', 'product_name', 'category', 'quantity', 
                        'selling_price', 'last_updated']],
            use_container_width=True
        )
        
        # أزرار التصدير
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📥 تصدير إلى CSV"):
                csv = filtered_df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="تحميل ملف CSV",
                    data=csv,
                    file_name="inventory_report.csv",
                    mime="text/csv"
                )
        
        with col2:
            st.metric("إجمالي المنتجات", len(filtered_df))
            st.metric("إجمالي القيمة", f"${(filtered_df['quantity'] * filtered_df['selling_price']).sum():.2f}")
    
    with tab2:
        if df_sales.empty:
            st.info("لا توجد عمليات بيع مسجلة بعد!")
        else:
            st.subheader("سجل المبيعات")
            
            # تحويل تاريخ البيع
            df_sales['date'] = pd.to_datetime(df_sales['date_time']).dt.date
            
            # إحصائيات المبيعات
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("إجمالي المبيعات", len(df_sales))
            with col2:
                st.metric("إجمالي الكمية المباعة", int(df_sales['quantity'].sum()))
            with col3:
                st.metric("إجمالي الإيرادات", f"${df_sales['total_price'].sum():.2f}")
            
            # عرض سجل المبيعات
            st.dataframe(
                df_sales[['sale_id', 'date_time', 'product_name', 'quantity', 
                         'total_price', 'remaining_stock']],
                use_container_width=True
            )
            
            # رسم بياني للمبيعات
            if len(df_sales) > 1:
                st.subheader("مخطط المبيعات اليومية")
                daily_sales = df_sales.groupby('date')['total_price'].sum().reset_index()
                st.line_chart(daily_sales.set_index('date'))
    
    with tab3:
        st.subheader("منتجات تحتاج إعادة طلب")
        
        # البحث عن منتجات أقل من الحد الأدنى
        low_stock = df_products[df_products['quantity'] <= df_products['min_stock']]
        
        if low_stock.empty:
            st.success("✅ جميع المنتجات في مستوى مخزون جيد!")
        else:
            st.warning(f"⚠️ يوجد {len(low_stock)} منتج تحتاج إعادة طلب")
            
            for _, product in low_stock.iterrows():
                with st.expander(f"{product['product_name']} - المخزون: {product['quantity']}"):
                    st.write(f"**الحد الأدنى:** {product['min_stock']}")
                    st.write(f"**الباقي:** {product['quantity'] - product['min_stock']} تحت الحد")
                    
                    # زر إضافة كمية
                    add_qty = st.number_input(f"إضافة كمية لـ {product['product_name']}", 
                                             min_value=1, value=10, key=f"add_{product['barcode']}")
                    
                    if st.button(f"تحديث المخزون", key=f"update_{product['barcode']}"):
                        # البحث عن المنتج وتحديثه
                        for p in st.session_state.products:
                            if p['barcode'] == product['barcode']:
                                p['quantity'] += add_qty
                                p['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                break
                        
                        save_to_csv(st.session_state.products, 'products.csv')
                        st.success(f"تم تحديث المخزون! إضافة {add_qty} وحدة")
                        st.rerun()
    
    with tab4:
        st.subheader("إحصائيات عامة")
        
        if not df_products.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # توزيع المنتجات حسب الفئة
                st.write("**توزيع المنتجات حسب الفئة**")
                category_dist = df_products['category'].value_counts()
                st.bar_chart(category_dist)
            
            with col2:
                # أعلى المنتجات قيمة
                st.write("**أعلى المنتجات قيمة (المخزون × السعر)**")
                df_products['total_value'] = df_products['quantity'] * df_products['selling_price']
                top_products = df_products.nlargest(5, 'total_value')[['product_name', 'total_value']]
                st.dataframe(top_products, use_container_width=True)
            
            # ملخص المخزون
            st.write("**ملخص المخزون**")
            summary_cols = st.columns(4)
            with summary_cols[0]:
                st.metric("إجمالي المنتجات", len(df_products))
            with summary_cols[1]:
                st.metric("إجمالي الوحدات", int(df_products['quantity'].sum()))
            with summary_cols[2]:
                st.metric("متوسط السعر", f"${df_products['selling_price'].mean():.2f}")
            with summary_cols[3]:
                st.metric("القيمة الإجمالية", f"${df_products['total_value'].sum():.2f}")

# --------------------------
# صفحة الإعدادات
# --------------------------
def settings_page():
    st.title("⚙️ إعدادات النظام")
    
    st.subheader("إدارة البيانات")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 تحميل البيانات من ملفات CSV"):
            try:
                st.session_state.products = load_from_csv('products.csv')
                st.session_state.sales = load_from_csv('sales.csv')
                st.success("تم تحميل البيانات بنجاح!")
            except Exception as e:
                st.error(f"خطأ في تحميل البيانات: {e}")
    
    with col2:
        if st.button("💾 حفظ البيانات الحالية"):
            try:
                save_to_csv(st.session_state.products, 'products.csv')
                save_to_csv(st.session_state.sales, 'sales.csv')
                st.success("تم حفظ البيانات بنجاح!")
            except Exception as e:
                st.error(f"خطأ في حفظ البيانات: {e}")
    
    st.subheader("نسخ احتياطي للبيانات")
    
    if st.button("📥 إنشاء نسخة احتياطية"):
        # إنشاء ملف نسخ احتياطي
        backup_data = {
            'products': st.session_state.products,
            'sales': st.session_state.sales,
            'backup_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        import json
        backup_json = json.dumps(backup_data, ensure_ascii=False, indent=2)
        
        st.download_button(
            label="تحميل النسخة الاحتياطية",
            data=backup_json,
            file_name=f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    st.subheader("معلومات النظام")
    
    st.info(f"""
    **إحصائيات النظام:**
    - عدد المنتجات: {len(st.session_state.products)}
    - عدد عمليات البيع: {len(st.session_state.sales)}
    - تاريخ التحديث الأخير: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    """)

# --------------------------
# الواجهة الرئيسية
# --------------------------
def main():
    # إعداد الصفحة
    st.set_page_config(
        page_title="نظام إدارة محل ملابس",
        page_icon="👕",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # الشريط الجانبي
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3082/3082383.png", width=100)
        st.title("👕 إدارة محل ملابس")
        st.markdown("---")
        
        # القائمة الرئيسية
        page = st.radio(
            "القائمة الرئيسية",
            ["📦 تسجيل المنتجات", "💰 شاشة المبيعات", "📊 تقارير المخزون", "⚙️ الإعدادات"],
            index=0
        )
        
        st.markdown("---")
        
        # معلومات سريعة
        st.write("**إحصائيات سريعة:**")
        if st.session_state.products:
            total_products = len(st.session_state.products)
            total_qty = sum(p['quantity'] for p in st.session_state.products)
            st.write(f"• المنتجات: {total_products}")
            st.write(f"• القطع: {total_qty}")
        else:
            st.write("لا توجد بيانات")
        
        st.markdown("---")
        st.caption(f"الإصدار 1.0 | {datetime.now().strftime('%Y-%m-%d')}")
    
    # تحميل البيانات
    if not st.session_state.products:
        setup_google_sheets()
    
    # تحميل الصفحة المختارة
    if "تسجيل المنتجات" in page:
        product_registration_page()
    elif "شاشة المبيعات" in page:
        sales_page()
    elif "تقارير المخزون" in page:
        inventory_page()
    elif "الإعدادات" in page:
        settings_page()

# --------------------------
# تشغيل التطبيق
# --------------------------
if __name__ == "__main__":
    main()