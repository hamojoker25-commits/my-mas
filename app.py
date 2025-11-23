import streamlit as st
import pandas as pd

# 1. إعداد الصفحة والواجهة الرأسية
st.set_page_config(page_title="نظام تحليل المبيعات الشامل", layout="wide")

# دالة مساعدة للنصوص حسب اللغة
def get_text(ar_text, en_text, lang):
    return ar_text if lang == 'العربية' else en_text

# الشريط الجانبي للإعدادات
with st.sidebar:
    st.header("الإعدادات / Settings")
    language = st.radio("اللغة / Language", ('العربية', 'English'))
    
    st.divider()
    
    # 2. دالة تحميل الملف
    upload_label = get_text("قم برفع ملف البيانات (CSV او Excel)", "Upload Data File (CSV or Excel)", language)
    uploaded_file = st.file_uploader(upload_label, type=['csv', 'xlsx'])

# 3. الواجهة الرأسية
title = get_text("برنامج تحليل المبيعات المتقدم", "Advanced Sales Analysis Program", language)
st.title(f"📊 {title}")

if uploaded_file is not None:
    # قراءة الملف
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success(get_text("تم تحميل الملف بنجاح!", "File Uploaded Successfully!", language))
        with st.expander(get_text("عرض البيانات الخام", "Show Raw Data", language)):
            st.dataframe(df.head())
            
    except Exception as e:
        st.error(f"Error: {e}")
        st.stop()

    # قائمة الأعمدة لتسهيل الاختيار بدلاً من الكتابة اليدوية
    columns = df.columns.tolist()

    # اختيار المجموعة المراد تشغيلها
    st.header(get_text("اختر نوع التحليل", "Choose Analysis Type", language))
    analysis_options = [
        "1. اساسيات تحليل المبيعات / Basic Sales Analysis",
        "2. تحليل المبيعات والمنتجات / Product & Sales Analysis",
        "3. تحليل المناطق والفروع / Regional Analysis",
        "4. تحليل الوقت والتاريخ / Time & Date Analysis",
        "5. تحليل الارباح والتكلفة / Profit & Cost Analysis"
    ]
    choice = st.selectbox("", analysis_options)

    st.markdown("---")

    # --- الدوال (تم تعديل المدخلات والمخرجات لتناسب Streamlit مع الحفاظ على المعادلات) ---

    if choice == analysis_options[0]:
        # The_first_group
        st.subheader(get_text("اساسيات تحليل المبيعات", "Basic Sales Analysis", language))
        
        col1, col2 = st.columns(2)
        with col1:
            First_column = st.selectbox(get_text("اختر عمود المبيعات", "Select Sales Column", language), columns, index=0)
            Second_column = st.selectbox(get_text("اختر عمود المنتج", "Select Product Column", language), columns, index=1 if len(columns)>1 else 0)
        with col2:
            Third_column = st.selectbox(get_text("اختر عمود المنطقة", "Select Region Column", language), columns, index=2 if len(columns)>2 else 0)
            # التعامل مع عمود الكمية (Quantity) لأنه كان ثابت في الكود الأصلي
            Quantity_col = st.selectbox(get_text("اختر عمود الكمية", "Select Quantity Column", language), columns)

        if st.button(get_text("تشغيل التحليل", "Run Analysis", language)):
            st.write(get_text("اجمالي المبيعات", "Total Sales", language))
            st.info(df[First_column].sum())

            st.write(get_text("متوسط قيمة البيع", "Average Sales Value", language))
            st.info(df[First_column].mean())

            st.write(get_text("اعلي قيمه مبيعا", "Max Sales Value", language))
            st.info(df[First_column].max())

            st.write(get_text("اقل قيمه مبيعا", "Min Sales Value", language))
            st.info(df[First_column].min())

            st.write(get_text("عدد عمليات البيع", "Number of Sales Transactions", language))
            st.info(df.shape[0])

            st.write(get_text("وصف المبيعات احصائيا", "Statistical Description", language))
            st.write(df[First_column].describe())

            st.write(get_text("عدد المنتجات المختلفة المباعة", "Number of Unique Products", language))
            st.info(df[Second_column].nunique())

            st.write(get_text("عدد المناطق التي تمت فيها المبيعات", "Number of Regions", language))
            st.info(df[Third_column].nunique()) # تم تصحيح المتغير بناء على المدخلات

            st.write(get_text("اجمالي الكمية المباعة", "Total Quantity Sold", language))
            st.info(df[Quantity_col].sum()) # استخدام المتغير المختار

            st.write(get_text("اعلي منطقة تحقيقا للمبيعات", "Top Region by Sales", language))
            st.write(df.groupby(Third_column)[First_column].sum().sort_values(ascending=False))

    elif choice == analysis_options[1]:
        # The_second_group
        st.subheader(get_text("تحليل المبيعات داخل المبيعات", "Sales & Product Analysis", language))
        
        c1, c2, c3 = st.columns(3)
        First_column = c1.selectbox(get_text("ادخل اسم المنتج", "Product Column", language), columns)
        Second_column = c2.selectbox(get_text("ادخل اسم المبيعات", "Sales Column", language), columns)
        Third_column = c3.selectbox(get_text("ادخل اسم الكمية", "Quantity Column", language), columns)
        
        c4, c5, c6 = st.columns(3)
        Fourth_column = c4.selectbox(get_text("ادخل عمود الربح", "Profit Column", language), columns)
        Fifth_column = c5.selectbox(get_text("ادخل عمود التاريخ", "Date Column", language), columns)
        Sixth_column = c6.selectbox(get_text("ادخل عمود الفئة", "Category Column", language), columns)

        if st.button(get_text("تشغيل التحليل", "Run Analysis", language)):
            # تحويل التاريخ لضمان عمل الكود
            try:
                df[Fifth_column] = pd.to_datetime(df[Fifth_column])
            except:
                st.warning("تأكد أن عمود التاريخ بالتنسيق الصحيح")

            st.write("اعلي منتجات مبيعا")
            st.dataframe(df.groupby(First_column)[Second_column].sum().sort_values(ascending=False))

            st.write("اقل منتج مبيعا")
            st.dataframe(df.groupby(First_column)[Second_column].sum().sort_values().head(10))

            st.write("اكثر منتج مبيعا من حيث الكمية")
            st.dataframe(df.groupby(First_column)[Third_column].sum().sort_values(ascending=False))

            st.write("اقل منتج مبيعا من حيث الكمية")
            st.dataframe(df.groupby(First_column)[Third_column].sum().sort_values().head(10))

            st.write("اعلي منتجات ربحا")
            st.dataframe(df.groupby(First_column)[Fourth_column].sum().sort_values(ascending=False))

            st.write("اقل منتج ربحا")
            st.dataframe(df.groupby(First_column)[Fourth_column].sum().sort_values().head(10))

            st.write("المنتجات الاعلي في هامش الربح")
            st.dataframe(df.groupby(First_column)[Fourth_column].sum() / df.groupby(First_column)[Second_column].sum())

            st.write("تحليل المنتجات من حيث الفئة")
            st.dataframe(df.groupby(Sixth_column)[Second_column].sum().sort_values(ascending=False))

            st.write("افضل 10 منتجات في كل فئة")
            st.dataframe(df.groupby([Sixth_column,First_column])[Second_column].sum().sort_values(ascending=False).groupby(level=0).head(10))

            st.write("المنتجات الموسمية حسب الشهر")
            if pd.api.types.is_datetime64_any_dtype(df[Fifth_column]):
                st.dataframe(df.groupby(df[Fifth_column].dt.month)[First_column].value_counts())
            else:
                st.error("يرجى التأكد من تحويل عمود التاريخ لصيغة Date")

    elif choice == analysis_options[2]:
        # The_third_group
        st.subheader(get_text("تحليل المناطق والفروع", "Regional Analysis", language))
        
        First_column = st.selectbox(get_text("ادخل عمود المنطقة", "Region Column", language), columns)
        Second_column = st.selectbox(get_text("ادخل عمود المبيعات", "Sales Column", language), columns)
        Third_column = st.selectbox(get_text("ادخل عمود الربح", "Profit Column", language), columns)
        Fourth_column = st.selectbox(get_text("ادخل عمود الكمية", "Quantity Column", language), columns)
        # Fifth_column ignored in code logic below but requested in input, map to Country if exists
        Fifth_column = st.selectbox(get_text("ادخل اسم الدولة/المحافظة (للتحليل حسب الدولة)", "Country Column", language), columns) 
        Sixth_column = st.selectbox(get_text("ادخل اسم المنتج", "Product Column", language), columns)
        Column_VII = st.selectbox(get_text("ادخل عمود السعر", "Price Column", language), columns)

        if st.button(get_text("تشغيل التحليل", "Run Analysis", language)):
            st.write("تحليل المبيعات حسب المنطقة")
            st.dataframe(df.groupby(First_column)[Second_column].sum().sort_values(ascending=False))

            st.write("تحليل الارباح حسب المنطقة")
            st.dataframe(df.groupby(First_column)[Third_column].sum().sort_values(ascending=False))
            
            st.write("اجمالي الكمية المباعة حسب المنطقة")
            st.dataframe(df.groupby(First_column)[Fourth_column].sum().sort_values(ascending=False))
            
            st.write("متوسط قيمة البيع في كل منطقة")
            st.dataframe(df.groupby(First_column)[Second_column].mean().sort_values(ascending=False))
            
            st.write("عدد العمليات في كل منطقة")
            st.write(df[First_column].value_counts())
            
            st.write("اعلي منطقة نمو في المبيعات (مقارنة تسلسلية)")
            st.dataframe(df.groupby(First_column)[Second_column].sum().diff())
            
            st.write("اسوأ منطقة من حيث المبيعات")
            st.dataframe(df.groupby(First_column)[Second_column].sum().sort_values().head(1))
            
            st.write("تحليل المبيعات حسب الدولة")
            st.dataframe(df.groupby(Fifth_column)[Second_column].sum().sort_values(ascending=False))
            
            st.write("تحليل اختلاف الاسعار حسب المنطقة")
            st.dataframe(df.groupby(First_column)[Column_VII].mean())
            
            st.write("تحليل المنتجات الاكثر مبيعا داخل كل منطقة")
            st.dataframe(df.groupby([First_column,Sixth_column])[Second_column].sum().sort_values(ascending=False))

    elif choice == analysis_options[3]:
        # Fourth_group
        st.subheader(get_text("تحليل الوقت والتاريخ", "Time Analysis", language))
        
        First_column = st.selectbox("ادخل عمود التاريخ / Date Column", columns)
        Second_column = st.selectbox("ادخل عمود المبيعات / Sales Column", columns)
        # Inputs for frequency
        Third_column = st.selectbox("التكرار الزمني (M للشهري)", ['M', 'Q', 'Y'], index=0)
        # Fourth column was meant for Year column in pivot, let's ask for a categorical column to pivot against
        Fourth_column = st.selectbox("عمود للمقارنة (مثل الفئة أو المنطقة) / Pivot Column", columns)

        if st.button(get_text("تشغيل التحليل", "Run Analysis", language)):
            st.write("تحويل التاريخ لصيغة Datetime")
            df[First_column] = pd.to_datetime(df[First_column])
            st.success("تم التحويل / Converted")

            st.write("تحليل المبيعات حسب اليوم")
            st.line_chart(df.groupby(df[First_column].dt.date)[Second_column].sum())

            st.write("تحليل المبيعات حسب الفترة المختارة")
            st.write(df.groupby(df[First_column].dt.to_period(Third_column))[Second_column].sum())

            st.write("تحليل المبيعات حسب السنة")
            st.bar_chart(df.groupby(df[First_column].dt.year)[Second_column].sum())

            st.write("تحديد اشهر الذروة")
            st.write(df.groupby(df[First_column].dt.month)[Second_column].sum().sort_values(ascending=False).head(3))

            st.write("تحديد اضعف الشهور مبيعات")
            st.write(df.groupby(df[First_column].dt.month)[Second_column].sum().sort_values().head(3))

            st.write("تحليل المبيعات حسب اليوم داخل الاسبوع")
            st.bar_chart(df.groupby(df[First_column].dt.day_name())[Second_column].sum())

            st.write("المبيعات اليومية المتراكمة")
            st.area_chart(df.groupby(df[First_column].dt.date)[Second_column].sum().cumsum())

            st.write("المتوسط اليومي للمبيعات")
            st.write(df.groupby(df[First_column].dt.date)[Second_column].mean())

            st.write("مقارنة المبيعات (Pivot Table)")
            try:
                pivot = df.pivot_table(values=Second_column, index=df[First_column].dt.month, columns=Fourth_column, aggfunc='sum')
                st.dataframe(pivot)
            except Exception as e:
                st.error(f"لا يمكن إنشاء الجدول المحوري: {e}")

    elif choice == analysis_options[4]:
        # Fifth_group
        st.subheader(get_text("تحليل الارباح والتكلفة", "Profit & Cost Analysis", language))
        
        First_column = st.selectbox("ادخل عمود الربح", columns)
        Second_column = st.selectbox("ادخل عمود التكلفة", columns)
        Third_column = st.selectbox("ادخل عمود المبيعات", columns)
        Fourth_column = st.selectbox("ادخل عمود المنتج", columns)
        Fifth_column = st.selectbox("ادخل عمود المنطقة", columns)

        if st.button(get_text("تشغيل التحليل", "Run Analysis", language)):
            st.metric("اجمالي الارباح", f"{df[First_column].sum():,.2f}")
            st.metric("متوسط الربح لكل عملية", f"{df[First_column].mean():,.2f}")
            st.metric("اعلي ربح في عملية واحده", f"{df[First_column].max():,.2f}")
            st.metric("اقل ربح في عملية واحدة", f"{df[First_column].min():,.2f}")
            st.metric("اجمالي التكلفة", f"{df[Second_column].sum():,.2f}")

            st.write("هامش الربح (تمت إضافته للجدول)")
            df['Profit_Margin'] = df[First_column] / df[Third_column]
            st.dataframe(df[['Profit_Margin']].head())

            st.write("تحليل الربح حسب المنتج")
            st.bar_chart(df.groupby(Fourth_column)[First_column].sum().sort_values(ascending=False).head(10))

            st.write("تحليل الربح حسب المنطقة")
            st.bar_chart(df.groupby(Fifth_column)[First_column].sum().sort_values(ascending=False))

            st.write("حساب نسبة الربح المئوية لكل منتج")
            profit_pct = (df.groupby(Fourth_column)[First_column].sum() / df.groupby(Fourth_column)[Third_column].sum()) * 100
            st.dataframe(profit_pct.sort_values(ascending=False))

            st.write("تحديد المنتجات الخاسرة")
            st.dataframe(df[df[First_column] < 0])

else:
    st.info(get_text("يرجى رفع ملف بيانات للبدء", "Please upload a data file to start", language))
