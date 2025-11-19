import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import timedelta

# ---------------------------------------------------------
# 1. إعداد الصفحة وتكوينها
# ---------------------------------------------------------
st.set_page_config(page_title="لوحة تحليل المبيعات الشاملة", layout="wide")

st.title("📊 لوحة القيادة لتحليل بيانات المبيعات (Sales Dashboard)")
st.markdown("""
تم تحديث الكود لضمان التشغيل الخالي من الأخطاء عبر الطلب اليدوي لأسماء الأعمدة.
""")

# ---------------------------------------------------------
# 2. دالة لتوليد بيانات تجريبية (للتأكد من عمل الكود)
# ---------------------------------------------------------
@st.cache_data
def generate_data():
    np.random.seed(42)
    dates = pd.date_range(start="2023-01-01", end="2023-12-31", freq="D")
    products = ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Headphones', 'Phone', 'Charger', 'Desk', 'Chair', 'Webcam']
    categories = {'Laptop': 'Electronics', 'Mouse': 'Accessories', 'Keyboard': 'Accessories', 
                  'Monitor': 'Electronics', 'Headphones': 'Audio', 'Phone': 'Electronics', 
                  'Charger': 'Accessories', 'Desk': 'Furniture', 'Chair': 'Furniture', 'Webcam': 'Accessories'}
    regions = ['North', 'South', 'East', 'West', 'Central']
    customers = ['Company A', 'Company B', 'Individual X', 'Store Y', 'Trader Z']
    
    data = []
    for _ in range(1000):
        date = np.random.choice(dates)
        prod = np.random.choice(products)
        cat = categories[prod]
        reg = np.random.choice(regions)
        cust = np.random.choice(customers)
        qty = np.random.randint(1, 20)
        price = np.random.randint(10, 2000)
        cost = price * 0.7 
        
        # نستخدم أسماء أعمدة عربية افتراضية في البيانات التجريبية لتجربة آلية التحديد اليدوي
        data.append([date, prod, cat, reg, cust, price, qty, cost])
        
    df = pd.DataFrame(data, columns=['التاريخ', 'المنتج', 'الفئة', 'المنطقة', 'العميل', 'السعر', 'الكمية', 'التكلفة'])
    return df

# ---------------------------------------------------------
# 3. تحميل البيانات (Sidebar)
# ---------------------------------------------------------
st.sidebar.header("📂 إعدادات البيانات")
upload_file = st.sidebar.file_uploader("ارفع ملف البيانات (CSV/Excel)", type=["csv", "xlsx"])

df = None
if upload_file:
    try:
        if upload_file.name.endswith('.csv'):
            df = pd.read_csv(upload_file, encoding='utf-8')
        else:
            df = pd.read_excel(upload_file)
    except Exception as e:
        st.error(f"حدث خطأ أثناء قراءة الملف. يرجى التأكد من التنسيق والترميز (عادةً UTF-8).")
        st.stop()
else:
    st.sidebar.info("يتم استخدام بيانات تجريبية غير حقيقية.")
    df = generate_data()

# ---------------------------------------------------------
# 4. معالجة البيانات وتحديد الأعمدة يدوياً (Manual Column Mapping)
# ---------------------------------------------------------

if df is not None:
    st.subheader("🛠️ خطوة 1: تحديد الأعمدة المطلوبة من ملفك")
    st.info("يرجى إدخال اسم العمود في ملفك (مطابق تماماً) الذي يمثل القيمة المطلوبة. الأعمدة الموجودة هي: " + ", ".join(df.columns))

    required_fields = {
        'Date': 'عمود التاريخ (مثال: التاريخ)',
        'Product': 'عمود اسم المنتج (مثال: المنتج)',
        'Category': 'عمود فئة المنتج (مثال: الفئة)',
        'Region': 'عمود المنطقة/الفرع (مثال: المنطقة)',
        'Price': 'عمود سعر الوحدة (مثال: السعر)',
        'Quantity': 'عمود الكمية المباعة (مثال: الكمية)'
    }
    
    # استخدام حالة Streamlit لتخزين أسماء الأعمدة المختارة
    if 'column_mapping' not in st.session_state:
        st.session_state.column_mapping = {}

    col_mapping_cols = st.columns(3)
    
    # عرض مربعات الإدخال لتحديد الأعمدة المطلوبة
    for i, (internal_name, prompt) in enumerate(required_fields.items()):
        col = col_mapping_cols[i % 3]
        
        # استنتاج القيمة الافتراضية
        default_val = st.session_state.column_mapping.get(internal_name)
        if default_val is None:
            # محاولة استنتاج من الأعمدة التجريبية
            default_val = next((col_name for col_name in df.columns if col_name == prompt.split(': ')[-1].replace(')', '')), '')
        
        st.session_state.column_mapping[internal_name] = col.text_input(
            prompt, 
            value=default_val,
            key=f"map_{internal_name}"
        )

    # التحقق من إدخال جميع الأعمدة المطلوبة وصحتها
    is_ready = True
    renaming_dict = {}
    for internal_name, actual_name in st.session_state.column_mapping.items():
        if not actual_name or actual_name not in df.columns:
            is_ready = False
        else:
            renaming_dict[actual_name] = internal_name
            
    if not is_ready:
        st.warning("⚠️ يرجى التأكد من إدخال جميع أسماء الأعمدة المطلوبة بشكل **مطابق** (حساسة لحالة الأحرف والمسافات) وموجودة في ملفك.")
        st.stop()
        
    # إعادة تسمية الأعمدة الداخلية باستخدام الأسماء القياسية (Date, Product, ...)
    df.rename(columns=renaming_dict, inplace=True)
    
    # تحديد الأعمدة الاختيارية
    st.markdown("---")
    st.subheader("🛠️ خطوة 2: تحديد الأعمدة الاختيارية")
    
    # قائمة الأعمدة المتبقية بعد التسمية
    remaining_cols = [col for col in df.columns if col not in required_fields.keys() and col not in ['Cost', 'Customer']]
    
    col_opt1, col_opt2 = st.columns(2)
    
    # اختيار عمود التكلفة
    cost_col_name = col_opt1.selectbox("عمود التكلفة (اختياري - مطلوب لحساب الربح)", ['(لا يوجد)'] + remaining_cols)
    if cost_col_name != '(لا يوجد)':
        df.rename(columns={cost_col_name: 'Cost'}, inplace=True)
        remaining_cols.remove(cost_col_name) # إزالته من الخيارات المتبقية
        
    # اختيار عمود العميل
    customer_col_name = col_opt2.selectbox("عمود العميل/المشتري (اختياري)", ['(لا يوجد)'] + remaining_cols)
    if customer_col_name != '(لا يوجد)':
        df.rename(columns={customer_col_name: 'Customer'}, inplace=True)
        
    # تحويل التاريخ
    try:
        # استخدام coerce لإجبار التحويل مع وضع NaT إذا لم يكن صالحاً
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce') 
        df.dropna(subset=['Date'], inplace=True) # حذف الصفوف التي لم يتم تحويل تاريخها
    except Exception as e:
        st.error(f"❌ خطأ فادح: فشل تحويل عمود التاريخ. يرجى مراجعة بيانات التاريخ في ملفك.")
        st.stop()
        
    # حساب الأعمدة المشتقة
    df['Revenue'] = df['Price'] * df['Quantity']

    if 'Cost' not in df.columns:
        df['Cost'] = 0 

    df['Profit'] = df['Revenue'] - (df['Cost'] * df['Quantity'])
    df['Month'] = df['Date'].dt.to_period('M').astype(str)
    df['Day_Name'] = df['Date'].dt.day_name()

    # فلاتر جانبية (Sidebar Filters)
    st.sidebar.subheader("🔍 الفلاتر")
    selected_region = st.sidebar.multiselect("اختر المنطقة", df['Region'].unique(), default=df['Region'].unique())
    selected_category = st.sidebar.multiselect("اختر الفئة", df['Category'].unique(), default=df['Category'].unique())

    # تطبيق الفلاتر
    filtered_df = df[(df['Region'].isin(selected_region)) & (df['Category'].isin(selected_category))]

    if filtered_df.empty:
        st.warning("لا توجد بيانات بناءً على الفلاتر المختارة.")
        st.stop()
        
    # ---------------------------------------------------------
    # 5. الأقسام والتبويبات (Tabs) - تبدأ هنا
    # ---------------------------------------------------------
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 1. التحليل الإحصائي", 
        "🏆 2. تحليل الأداء", 
        "⏳ 3. تحليل الزمن", 
        "💰 4. تحليل الأسعار", 
        "📦 5. تحليل المنتجات"
    ])

    # =========================================================
    # TAB 1: التحليل الإحصائي الأساسي
    # =========================================================
    with tab1:
        st.header("🔹 التحليل الإحصائي الأساسي")
        
        # الحسابات
        total_revenue = filtered_df['Revenue'].sum()
        total_qty = filtered_df['Quantity'].sum()
        avg_price = filtered_df['Price'].mean()
        max_price = filtered_df['Price'].max()
        min_price = filtered_df['Price'].min()
        
        # التجميعات
        sales_by_region = filtered_df.groupby('Region')['Revenue'].sum()
        best_region = sales_by_region.idxmax()
        worst_region = sales_by_region.idxmin()
        
        sales_by_day = filtered_df.groupby('Date')['Revenue'].sum()
        avg_daily_revenue = sales_by_day.mean()
        best_day = sales_by_day.idxmax().strftime('%Y-%m-%d')
        worst_day = sales_by_day.idxmin().strftime('%Y-%m-%d')

        # عرض المقاييس (Metrics)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("عدد الصفوف (المعاملات)", filtered_df.shape[0])
        col1.metric("عدد المنتجات الفريدة", filtered_df['Product'].nunique())
        col1.metric("عدد الفئات", filtered_df['Category'].nunique())
        
        col2.metric("إجمالي الإيرادات", f"${total_revenue:,.2f}")
        col2.metric("مجموع الكميات", f"{total_qty:,}")
        col2.metric("متوسط السعر", f"${avg_price:.2f}")
        
        col3.metric("أعلى سعر منتج", f"${max_price:.2f}")
        col3.metric("أقل سعر منتج", f"${min_price:.2f}")
        col3.metric("متوسط الإيراد اليومي", f"${avg_daily_revenue:,.2f}")

        col4.metric("أكثر منطقة مبيعًا", best_region)
        col4.metric("أقل منطقة مبيعًا", worst_region)
        col4.metric("أفضل يوم مبيعات", best_day)
        
        st.info(f"📅 **أقل يوم مبيعات:** {worst_day}")

    # =========================================================
    # TAB 2: تحليل الأداء Performance
    # =========================================================
    with tab2:
        st.header("🔹 تحليل الأداء (Performance Analysis)")
        
        col_a, col_b = st.columns(2)
        
        # أفضل 10 منتجات وأسوأ 10 منتجات
        product_perf = filtered_df.groupby('Product')['Revenue'].sum().sort_values(ascending=False)
        
        with col_a:
            st.subheader("أفضل 10 منتجات (إيرادات)")
            fig_top_prod = px.bar(product_perf.head(10), orientation='h', title="Top 10 Products", color_discrete_sequence=['green'])
            st.plotly_chart(fig_top_prod, use_container_width=True)
            
        with col_b:
            st.subheader("أسوأ 10 منتجات (إيرادات)")
            fig_low_prod = px.bar(product_perf.tail(10), orientation='h', title="Bottom 10 Products", color_discrete_sequence=['red'])
            st.plotly_chart(fig_low_prod, use_container_width=True)

        col_c, col_d = st.columns(2)
        
        # أفضل 5 مناطق
        region_perf = filtered_df.groupby('Region')['Revenue'].sum().nlargest(5)
        with col_c:
            st.subheader("أفضل 5 مناطق")
            fig_region = px.pie(values=region_perf.values, names=region_perf.index, hole=0.4)
            st.plotly_chart(fig_region, use_container_width=True)

        # أعلى 5 عملاء (إذا وجد العمود)
        if 'Customer' in filtered_df.columns:
            cust_perf = filtered_df.groupby('Customer')['Revenue'].sum().nlargest(5)
            with col_d:
                st.subheader("أعلى 5 عملاء")
                fig_cust = px.bar(cust_perf, title="Top 5 Customers")
                st.plotly_chart(fig_cust, use_container_width=True)
        
        st.markdown("---")
        
        # نسبة المساهمة والكمية مقابل الإيراد
        col_e, col_f = st.columns(2)
        
        with col_e:
            st.subheader("نسبة مساهمة الفئات (Category Contribution)")
            cat_perf = filtered_df.groupby('Category')['Revenue'].sum()
            fig_cat = px.pie(values=cat_perf.values, names=cat_perf.index, title="Category Share")
            st.plotly_chart(fig_cat, use_container_width=True)
            
        with col_f:
            st.subheader("تحليل الكمية مقابل الإيراد لكل منتج")
            qty_rev = filtered_df.groupby('Product')[['Quantity', 'Revenue']].sum().reset_index()
            fig_scatter = px.scatter(qty_rev, x='Quantity', y='Revenue', hover_name='Product', size='Revenue', color='Revenue')
            st.plotly_chart(fig_scatter, use_container_width=True)

    # =========================================================
    # TAB 3: تحليل الزمن (Time Series)
    # =========================================================
    with tab3:
        st.header("🔹 تحليل الزمن (Time Series Analysis)")
        
        # تجميع البيانات
        daily_sales = filtered_df.groupby('Date')['Revenue'].sum()
        weekly_sales = filtered_df.set_index('Date').resample('W')['Revenue'].sum()
        monthly_sales = filtered_df.set_index('Date').resample('M')['Revenue'].sum()
        
        # اختيار نوع العرض
        time_frame = st.radio("اختر الفترة الزمنية:", ["يومي", "أسبوعي", "شهري"], horizontal=True)
        
        if time_frame == "يومي":
            data_ts = daily_sales
            title_ts = "المبيعات اليومية"
        elif time_frame == "أسبوعي":
            data_ts = weekly_sales
            title_ts = "المبيعات الأسبوعية"
        else:
            data_ts = monthly_sales
            title_ts = "المبيعات الشهرية"
        
        # رسم الخط الزمني
        fig_ts = px.line(data_ts, title=f"{title_ts} واتجاه المبيعات (Trend)")
        # إضافة Trendline (Moving Average)
        data_ts_df = data_ts.to_frame(name='Revenue')
        data_ts_df['MA'] = data_ts_df['Revenue'].rolling(window=3).mean()
        fig_ts.add_trace(go.Scatter(x=data_ts_df.index, y=data_ts_df['MA'], mode='lines', name='Trend (Moving Avg)', line=dict(dash='dash', color='orange')))
        st.plotly_chart(fig_ts, use_container_width=True)
        
        # معدل النمو
        st.subheader("معدل النمو (Growth Rate)")
        data_ts_df['Growth Rate %'] = data_ts_df['Revenue'].pct_change() * 100
        st.bar_chart(data_ts_df['Growth Rate %'])
        
        # التنبؤ البسيط (Forecast - Simple Linear Extrapolation visually)
        st.markdown("**ملاحظة:** خط الـ Trend أعلاه يمثل الاتجاه العام. للتنبؤ المتقدم يفضل استخدام خوارزميات ML.")

    # =========================================================
    # TAB 4: تحليل الأسعار
    # =========================================================
    with tab4:
        st.header("🔹 تحليل الأسعار (Price Analysis)")
        
        # متوسط سعر كل منتج
        avg_price_prod = filtered_df.groupby('Product')['Price'].mean().sort_values()
        global_avg = filtered_df['Price'].mean()
        
        col_p1, col_p2 = st.columns(2)
        
        with col_p1:
            st.subheader("توزيع أسعار المنتجات")
            fig_hist = px.histogram(filtered_df, x='Price', nbins=30, title="تكرار الأسعار")
            fig_hist.add_vline(x=global_avg, line_dash="dash", line_color="red", annotation_text="Avg Price")
            st.plotly_chart(fig_hist, use_container_width=True)
            
        with col_p2:
            st.subheader("السعر مقابل الكمية (المرونة)")
            fig_price_qty = px.scatter(filtered_df, x='Price', y='Quantity', color='Category', title="هل السعر يؤثر على الكمية؟")
            st.plotly_chart(fig_price_qty, use_container_width=True)
        
        # منتجات أعلى وأقل من المتوسط
        st.markdown("---")
        col_list1, col_list2 = st.columns(2)
        
        with col_list1:
            st.write(f"🔼 **منتجات سعرها أعلى من المتوسط العام ({global_avg:.1f}):**")
            above_avg = avg_price_prod[avg_price_prod > global_avg]
            st.dataframe(above_avg, height=200)
            
        with col_list2:
            st.write(f"🔽 **منتجات سعرها أقل من المتوسط العام:**")
            below_avg = avg_price_prod[avg_price_prod < global_avg]
            st.dataframe(below_avg, height=200)

    # =========================================================
    # TAB 5: تحليل المنتجات والربحية
    # =========================================================
    with tab5:
        st.header("🔹 تحليل المنتجات والربحية")
        
        # تجميع البيانات للمنتجات
        prod_analysis = filtered_df.groupby('Product').agg({
            'Quantity': 'sum',
            'Revenue': 'sum',
            'Profit': 'sum',
            'Price': 'mean'
        }).reset_index()
        
        # حساب هامش الربح
        prod_analysis['Profit Margin %'] = (prod_analysis['Profit'] / prod_analysis['Revenue']) * 100
        
        # الأكثر والأقل بيعًا (كمية)
        most_sold = prod_analysis.loc[prod_analysis['Quantity'].idxmax()]
        least_sold = prod_analysis.loc[prod_analysis['Quantity'].idxmin()]
        
        c1, c2, c3 = st.columns(3)
        c1.metric("المنتج الأكثر بيعًا (كمية)", most_sold['Product'], f"{most_sold['Quantity']} units")
        c2.metric("المنتج الأقل بيعًا (كمية)", least_sold['Product'], f"{least_sold['Quantity']} units")
        c3.metric("متوسط هامش الربح", f"{prod_analysis['Profit Margin %'].mean():.2f}%")
        
        st.markdown("---")
        
        # Scatter للربح
        st.subheader("أرباح كل منتج وهامش الربح")
        fig_profit = px.scatter(prod_analysis, x='Revenue', y='Profit', size='Profit Margin %', color='Product', 
                                title="الإيراد vs الربح (حجم النقطة = هامش الربح)")
        st.plotly_chart(fig_profit, use_container_width=True)
        
        # تصنيف ABC Analysis
        # A: تساهم بـ 80% من الإيراد
        # B: تساهم بالـ 15% التالية
        # C: الباقي 5%
        st.subheader("تصنيف المنتجات حسب الربحية (ABC Analysis)")
        
        abc_df = prod_analysis.sort_values('Revenue', ascending=False)
        abc_df['Cumulative Revenue'] = abc_df['Revenue'].cumsum()
        abc_df['Revenue Share'] = abc_df['Cumulative Revenue'] / abc_df['Revenue'].sum()
        
        def classify_abc(percentage):
            if percentage <= 0.80:
                return 'A'
            elif percentage <= 0.95:
                return 'B'
            else:
                return 'C'
                
        abc_df['Class'] = abc_df['Revenue Share'].apply(classify_abc)
        
        col_abc1, col_abc2 = st.columns([2, 1])
        
        with col_abc1:
            st.dataframe(abc_df[['Product', 'Revenue', 'Profit', 'Class']].style.applymap(
                lambda v: 'color: green; font-weight: bold;' if v == 'A' else ('color: orange;' if v == 'B' else 'color: red;'), subset=['Class']
            ))
            
        with col_abc2:
            fig_abc = px.pie(abc_df, names='Class', values='Revenue', title="توزيع الإيرادات حسب التصنيف", 
                             color='Class', color_discrete_map={'A':'green', 'B':'orange', 'C':'red'})
            st.plotly_chart(fig_abc, use_container_width=True)

    st.markdown("---")
    st.caption("تم تطوير لوحة البيانات باستخدام Python & Streamlit ✅")
