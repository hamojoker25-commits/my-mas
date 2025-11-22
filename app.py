import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="نظام التحليل الشامل", layout="wide", initial_sidebar_state="expanded")

st.title("🎯 نظام التحليل الشامل للبيانات")
st.markdown("---")

ANALYSIS_GROUPS = {
    "المجموعة 1: تحليل المبيعات الأساسي": {
        "analyses": list(range(1, 11)),
        "names": [
            "إجمالي المبيعات", "إجمالي الأرباح", "أفضل 10 منتجات مبيعًا",
            "أقل 10 منتجات مبيعًا", "تحليل المبيعات حسب المنطقة",
            "تحليل المبيعات حسب الفئة", "تحليل المبيعات حسب العميل",
            "تحليل المبيعات حسب الشهر", "تحليل المبيعات حسب اليوم",
            "تحليل المبيعات حسب الربع المالي"
        ],
        "required_columns": ["التاريخ", "المنتج", "الفئة", "المنطقة", "العميل", "الكمية", "سعر_البيع", "التكلفة"]
    },
    "المجموعة 2: تحليل المبيعات المتقدم": {
        "analyses": list(range(11, 21)),
        "names": [
            "معدل الربح لكل منتج", "معدل الربح لكل فئة", "تحليل متوسط سعر البيع",
            "تحليل هامش الربح لكل منتج", "تحليل المبيعات حسب القناة",
            "تحليل المبيعات حسب المخزون", "تحليل المبيعات الموسمية",
            "تحليل المبيعات حسب الترويج", "تحليل المبيعات اليومية",
            "تحليل المبيعات الأسبوعية"
        ],
        "required_columns": ["التاريخ", "المنتج", "الفئة", "القناة", "الكمية", "سعر_البيع", "التكلفة", "الترويج", "المخزون"]
    },
    "المجموعة 3: تحليل المخزون الأساسي": {
        "analyses": list(range(21, 31)),
        "names": [
            "إجمالي المخزون", "المخزون حسب المنتج", "المخزون حسب الفئة",
            "المخزون حسب المستودع", "المنتجات منخفضة المخزون",
            "المنتجات عالية المخزون", "معدل دوران المخزون",
            "المخزون المتوقع", "المخزون الأمني", "تحليل المنتجات المتقادمة"
        ],
        "required_columns": ["المنتج", "الفئة", "المستودع", "الكمية_الحالية", "الحد_الأدنى", "الحد_الأقصى", "تاريخ_الإضافة", "المبيعات_الشهرية"]
    },
    "المجموعة 4: تحليل المخزون المتقدم": {
        "analyses": list(range(31, 41)),
        "names": [
            "تحليل المنتجات حسب العمر في المخزون", "تحليل المنتجات حسب المبيعات",
            "تحليل الطلب المستقبلي", "المخزون حسب المورد", "المخزون حسب المنطقة",
            "تحليل المخزون بناءً على الموسم", "المخزون حسب سعر البيع",
            "معدل استهلاك المخزون", "تحليل الطلب مقابل المخزون", "المخزون حسب الفئة العليا"
        ],
        "required_columns": ["المنتج", "الفئة", "المورد", "المنطقة", "الكمية_الحالية", "تاريخ_الإضافة", "سعر_البيع", "المبيعات_اليومية", "الموسم"]
    },
    "المجموعة 5: تحليل الموظفين الأساسي": {
        "analyses": list(range(41, 51)),
        "names": [
            "عدد الموظفين حسب القسم", "عدد الموظفين حسب الدور",
            "متوسط الراتب حسب القسم", "متوسط الراتب حسب الدور", "التوظيف الشهري",
            "معدل الاستقالات", "تحليل الغياب", "تحليل الحضور",
            "تحليل العمر الوظيفي", "تحليل الموظفين الجدد"
        ],
        "required_columns": ["الموظف", "القسم", "الدور", "الراتب", "تاريخ_التوظيف", "تاريخ_الاستقالة", "أيام_الغياب", "أيام_الحضور"]
    },
    "المجموعة 6: تحليل الموظفين المتقدم": {
        "analyses": list(range(51, 61)),
        "names": [
            "أعلى الرواتب", "أقل الرواتب", "توزيع الرواتب", "تقييم الأداء السنوي",
            "الأداء حسب القسم", "الأداء حسب الدور", "متوسط الغياب حسب القسم",
            "متوسط الغياب حسب الدور", "متوسط العمر الوظيفي",
            "تحليل الموظفين المستهدفين للترقية"
        ],
        "required_columns": ["الموظف", "القسم", "الدور", "الراتب", "تاريخ_التوظيف", "تقييم_الأداء", "أيام_الغياب", "مؤهل_للترقية"]
    },
    "المجموعة 7: تحليل العملاء الأساسي": {
        "analyses": list(range(61, 71)),
        "names": [
            "عدد العملاء الكلي", "العملاء الجدد", "العملاء النشطين",
            "العملاء غير النشطين", "أفضل العملاء حسب المبيعات",
            "أقل العملاء حسب المبيعات", "العملاء حسب المنطقة",
            "العملاء حسب الفئة", "العملاء حسب العمر", "العملاء حسب الجنس"
        ],
        "required_columns": ["العميل", "المنطقة", "الفئة", "العمر", "الجنس", "تاريخ_التسجيل", "آخر_عملية_شراء", "إجمالي_المشتريات"]
    },
    "المجموعة 8: تحليل العملاء المتقدم": {
        "analyses": list(range(71, 81)),
        "names": [
            "معدل الاحتفاظ بالعملاء", "معدل فقدان العملاء", "العملاء المحتملين",
            "معدل التحويل من Lead إلى عميل", "متوسط الإنفاق لكل عميل",
            "العملاء العائدين", "العملاء الذين لم يشتروا منذ فترة",
            "العملاء حسب التفاعل", "العملاء حسب القناة", "العملاء حسب المنتجات المشتركة"
        ],
        "required_columns": ["العميل", "تاريخ_التسجيل", "آخر_عملية_شراء", "عدد_المشتريات", "إجمالي_المشتريات", "القناة", "حالة_العميل", "التفاعل"]
    },
    "المجموعة 9: تحليل التسويق الأساسي": {
        "analyses": list(range(81, 91)),
        "names": [
            "عدد الزوار الكلي", "الزوار حسب المصدر", "الزوار حسب القناة",
            "معدل النقر CTR", "معدل التحويل", "معدل الارتداد",
            "المشتركين الجدد", "المشتركين النشطين", "المشتركين غير النشطين",
            "الحملات الإعلانية الأكثر فعالية"
        ],
        "required_columns": ["التاريخ", "المصدر", "القناة", "عدد_الزوار", "النقرات", "التحويلات", "معدل_الارتداد", "الحملة"]
    },
    "المجموعة 10: تحليل التسويق المتقدم": {
        "analyses": list(range(91, 101)),
        "names": [
            "تكلفة الاكتساب لكل عميل", "العائد على الاستثمار الإعلاني",
            "الإيرادات حسب القناة", "الإيرادات حسب الحملة", "الإيرادات حسب الفئة",
            "تحليل التفاعل حسب المحتوى", "تحليل التفاعل حسب الزمان",
            "تحليل التفاعل حسب القناة", "توقع الحملات الإعلانية القادمة",
            "تحليل المبيعات الناتجة عن الحملات"
        ],
        "required_columns": ["التاريخ", "القناة", "الحملة", "الفئة", "التكلفة", "الإيرادات", "التحويلات", "التفاعل", "المحتوى"]
    }
}

with st.sidebar:
    st.header("⚙️ الإعدادات")
    selected_group = st.selectbox("اختر المجموعة:", options=list(ANALYSIS_GROUPS.keys()))
    st.subheader("📋 الأعمدة المطلوبة:")
    required_cols = ANALYSIS_GROUPS[selected_group]["required_columns"]
    for col in required_cols:
        st.write(f"• {col}")
    st.markdown("---")
    uploaded_file = st.file_uploader("📂 رفع ملف Excel أو CSV", type=['xlsx', 'xls', 'csv'])

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success("✅ تم تحميل الملف بنجاح!")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("عدد الصفوف", df.shape[0])
        with col2:
            st.metric("عدد الأعمدة", df.shape[1])
        with col3:
            st.metric("حجم البيانات", f"{df.memory_usage(deep=True).sum() / 1024:.2f} KB")
        
        with st.expander("👁️ عرض البيانات"):
            st.dataframe(df.head(10))
        
        st.markdown("---")
        st.subheader("📊 اختر التحليل المطلوب")
        
        analyses_names = ANALYSIS_GROUPS[selected_group]["names"]
        analyses_nums = ANALYSIS_GROUPS[selected_group]["analyses"]
        
        selected_analysis_name = st.selectbox("نوع التحليل:", options=analyses_names)
        selected_analysis_num = analyses_nums[analyses_names.index(selected_analysis_name)]
        
        if st.button("🚀 تنفيذ التحليل", type="primary"):
            st.markdown("---")
            st.subheader(f"📈 نتائج التحليل: {selected_analysis_name}")
            
            try:
                if 1 <= selected_analysis_num <= 10:
                    if selected_analysis_num == 1:
                        total = (df['الكمية'] * df['سعر_البيع']).sum()
                        st.metric("💰 إجمالي المبيعات", f"{total:,.2f} جنيه")
                    elif selected_analysis_num == 2:
                        profit = ((df['سعر_البيع'] - df['التكلفة']) * df['الكمية']).sum()
                        st.metric("💵 إجمالي الأرباح", f"{profit:,.2f} جنيه")
                    elif selected_analysis_num == 3:
                        top = df.groupby('المنتج').apply(lambda x: (x['الكمية'] * x['سعر_البيع']).sum()).nlargest(10)
                        fig = px.bar(x=top.values, y=top.index, orientation='h', title="أفضل 10 منتجات مبيعًا")
                        st.plotly_chart(fig, use_container_width=True)
                    elif selected_analysis_num == 4:
                        bottom = df.groupby('المنتج').apply(lambda x: (x['الكمية'] * x['سعر_البيع']).sum()).nsmallest(10)
                        fig = px.bar(x=bottom.values, y=bottom.index, orientation='h', title="أقل 10 منتجات مبيعًا")
                        st.plotly_chart(fig, use_container_width=True)
                    elif selected_analysis_num == 5:
                        by_region = df.groupby('المنطقة').apply(lambda x: (x['الكمية'] * x['سعر_البيع']).sum())
                        fig = px.pie(values=by_region.values, names=by_region.index, title="المبيعات حسب المنطقة")
                        st.plotly_chart(fig, use_container_width=True)
                    elif selected_analysis_num == 6:
                        by_cat = df.groupby('الفئة').apply(lambda x: (x['الكمية'] * x['سعر_البيع']).sum())
                        fig = px.bar(x=by_cat.index, y=by_cat.values, title="المبيعات حسب الفئة")
                        st.plotly_chart(fig, use_container_width=True)
                    elif selected_analysis_num == 7:
                        by_customer = df.groupby('العميل').apply(lambda x: (x['الكمية'] * x['سعر_البيع']).sum()).nlargest(15)
                        fig = px.bar(x=by_customer.index, y=by_customer.values, title="المبيعات حسب العميل")
                        st.plotly_chart(fig, use_container_width=True)
                    elif selected_analysis_num == 8:
                        df['الشهر'] = pd.to_datetime(df['التاريخ']).dt.to_period('M').astype(str)
                        by_month = df.groupby('الشهر').apply(lambda x: (x['الكمية'] * x['سعر_البيع']).sum())
                        fig = px.line(x=by_month.index, y=by_month.values, title="المبيعات حسب الشهر")
                        st.plotly_chart(fig, use_container_width=True)
                    elif selected_analysis_num == 9:
                        df['اليوم'] = pd.to_datetime(df['التاريخ']).dt.date
                        by_day = df.groupby('اليوم').apply(lambda x: (x['الكمية'] * x['سعر_البيع']).sum())
                        fig = px.line(x=by_day.index, y=by_day.values, title="المبيعات حسب اليوم")
                        st.plotly_chart(fig, use_container_width=True)
                    elif selected_analysis_num == 10:
                        df['الربع'] = pd.to_datetime(df['التاريخ']).dt.to_period('Q').astype(str)
                        by_quarter = df.groupby('الربع').apply(lambda x: (x['الكمية'] * x['سعر_البيع']).sum())
                        fig = px.bar(x=by_quarter.index, y=by_quarter.values, title="المبيعات حسب الربع المالي")
                        st.plotly_chart(fig, use_container_width=True)
                
                elif 11 <= selected_analysis_num <= 20:
                    if selected_analysis_num == 11:
                        df['الربح'] = (df['سعر_البيع'] - df['التكلفة']) * df['الكمية']
                        df['المبيعات'] = df['الكمية'] * df['سعر_البيع']
                        profit_rate = df.groupby('المنتج').apply(lambda x: (x['الربح'].sum() / x['المبيعات'].sum() * 100) if x['المبيعات'].sum() > 0 else 0)
                        fig = px.bar(x=profit_rate.index, y=profit_rate.values, title="معدل الربح لكل منتج")
                        st.plotly_chart(fig, use_container_width=True)
                    elif selected_analysis_num == 12:
                        df['الربح'] = (df['سعر_البيع'] - df['التكلفة']) * df['الكمية']
                        df['المبيعات'] = df['الكمية'] * df['سعر_البيع']
                        profit_rate = df.groupby('الفئة').apply(lambda x: (x['الربح'].sum() / x['المبيعات'].sum() * 100) if x['المبيعات'].sum() > 0 else 0)
                        fig = px.bar(x=profit_rate.index, y=profit_rate.values, title="معدل الربح لكل فئة")
                        st.plotly_chart(fig, use_container_width=True)
                    elif selected_analysis_num == 13:
                        avg_price = df.groupby('المنتج')['سعر_البيع'].mean()
                        fig = px.bar(x=avg_price.index, y=avg_price.values, title="متوسط سعر البيع")
                        st.plotly_chart(fig, use_container_width=True)
                    elif selected_analysis_num == 14:
                        df['هامش_الربح'] = ((df['سعر_البيع'] - df['التكلفة']) / df['سعر_البيع'] * 100)
                        margin = df.groupby('المنتج')['هامش_الربح'].mean()
                        fig = px.bar(x=margin.index, y=margin.values, title="هامش الربح لكل منتج")
                        st.plotly_chart(fig, use_container_width=True)
                    elif selected_analysis_num == 15:
                        by_channel = df.groupby('القناة').apply(lambda x: (x['الكمية'] * x['سعر_البيع']).sum())
                        fig = px.pie(values=by_channel.values, names=by_channel.index, title="المبيعات حسب القناة")
                        st.plotly_chart(fig, use_container_width=True)
                    elif selected_analysis_num == 16:
                        sales_inv = df.groupby('المنتج').agg({'الكمية': 'sum', 'المخزون': 'mean'}).reset_index()
                        fig = px.scatter(sales_inv, x='المخزون', y='الكمية', text='المنتج', title="المبيعات مقابل المخزون")
                        st.plotly_chart(fig, use_container_width=True)
                    elif selected_analysis_num == 17:
                        df['الشهر'] = pd.to_datetime(df['التاريخ']).dt.month
                        seasonal = df.groupby('الشهر').apply(lambda x: (x['الكمية'] * x['سعر_البيع']).sum())
                        fig = px.line(x=seasonal.index, y=seasonal.values, title="المبيعات الموسمية")
                        st.plotly_chart(fig, use_container_width=True)
                    elif selected_analysis_num == 18:
                        by_promo = df.groupby('الترويج').apply(lambda x: (x['الكمية'] * x['سعر_البيع']).sum())
                        fig = px.bar(x=by_promo.index, y=by_promo.values, title="المبيعات حسب الترويج")
                        st.plotly_chart(fig, use_container_width=True)
                    elif selected_analysis_num == 19:
                        df['اليوم'] = pd.to_datetime(df['التاريخ']).dt.date
                        daily = df.groupby('اليوم').apply(lambda x: (x['الكمية'] * x['سعر_البيع']).sum())
                        fig = px.line(x=daily.index, y=daily.values, title="المبيعات اليومية")
                        st.plotly_chart(fig, use_container_width=True)
                    elif selected_analysis_num == 20:
                        df['الأسبوع'] = pd.to_datetime(df['التاريخ']).dt.to_period('W').astype(str)
                        weekly = df.groupby('الأسبوع').apply(lambda x: (x['الكمية'] * x['سعر_البيع']).sum())
                        fig = px.line(x=weekly.index, y=weekly.values, title="المبيعات الأسبوعية")
                        st.plotly_chart(fig, use_container_width=True)
                
                elif 21 <= selected_analysis_num <= 30:
                    if selected_analysis_num == 21:
                        total = df['الكمية_الحالية'].sum()
                        st.metric("📦 إجمالي المخزون", f"{total:,.0f} وحدة")
                    elif selected_analysis_num == 22:
                        by_product = df.groupby('المنتج')['الكمية_الحالية'].sum()
                        fig = px.bar(x=by_product.index, y=by_product.values, title="المخزون حسب المنتج")
                        st.plotly_chart(fig, use_container_width=True)
                    elif selected_analysis_num == 23:
                        by_cat = df.groupby('الفئة')['الكمية_الحالية'].sum()
                        fig = px.pie(values=by_cat.values, names=by_cat.index, title="المخزون حسب الفئة")
                        st.plotly_chart(fig, use_container_width=True)
                    elif selected_analysis_num == 24:
                        by_warehouse = df.groupby('المستودع')['الكمية_الحالية'].sum()
                        fig = px.bar(x=by_warehouse.index, y=by_warehouse.values, title="المخزون حسب المستودع")
                        st.plotly_chart(fig, use_container_width=True)
                    elif selected_analysis_num == 25:
                        low = df[df['الكمية_الحالية'] < df['الحد_الأدنى']]
                        st.write(f"⚠️ عدد المنتجات منخفضة المخزون: {len(low)}")
                        if len(low) > 0:
                            st.dataframe(low[['المنتج', 'الكمية_الحالية', 'الحد_الأدنى']])
                    elif selected_analysis_num == 26:
                        high = df[df['الكمية_الحالية'] > df['الحد_الأقصى']]
                        st.write(f"📈 عدد المنتجات عالية المخزون: {len(high)}")
                        if len(high) > 0:
                            st.dataframe(high[['المنتج', 'الكمية_الحالية', 'الحد_الأقصى']])
                    elif selected_analysis_num == 27:
                        df_copy = df.copy()
                        df_copy['معدل_الدوران'] = df_copy.apply(lambda x: x['المبيعات_الشهرية'] / x['الكمية_الحالية'] if x['الكمية_الحالية'] > 0 else 0, axis=1)
                        turnover = df_copy.groupby('المنتج')['معدل_الدوران'].mean()
                        fig = px.bar(x=turnover.index, y=turnover.values, title="معدل دوران المخزون")
                        st.plotly_chart(fig, use_container_width=True)
                    elif selected_analysis_num == 28:
                        df_copy = df.copy()
                        df_copy['المخزون_المتوقع'] = df_copy['الكمية_الحالية'] - (df_copy['المبيعات_الشهرية'] / 30 * 7)
                        expected = df_copy.groupby('المنتج')['المخزون_المتوقع'].mean()
                        fig = px.bar(x=expected.index, y=expected.values, title="المخزون المتوقع بعد 7 أيام")
                        st.plotly_chart(fig, use_container_width=True)
                    elif selected_analysis_num == 29:
                        safety = df.groupby('المنتج')['الحد_الأدنى'].mean()
                        fig = px.bar(x=safety.index, y=safety.values, title="المخزون الأمني")
                        st.plotly_chart(fig, use_container_width=True)
                    elif selected_analysis_num == 30:
                        df_copy = df.copy()
                        df_copy['العمر'] = (pd.Timestamp.now() - pd.to_datetime(df_copy['تاريخ_الإضافة'])).dt.days
                        obsolete = df_copy[df_copy['العمر'] > 180]
                        st.write(f"⏰ عدد المنتجات المتقادمة (أكثر من 180 يوم): {len(obsolete)}")
                        if len(obsolete) > 0:
                            st.dataframe(obsolete[['المنتج', 'الكمية_الحالية', 'العمر']])
                
                else:
                    st.warning("⚠️ هذا التحليل قيد التطوير. اختر تحليل آخر من المجموعات 1-3")
                
            except Exception as e:
                st.error(f"❌ حدث خطأ أثناء التحليل: {str(e)}")
                st.info("💡 تأكد من أن الملف يحتوي على جميع الأعمدة المطلوبة")
    
    except Exception as e:
        st.error(f"❌ خطأ في قراءة الملف: {str(e)}")

else:
    st.info("👆 ارفع ملف Excel أو CSV من القائمة الجانبية للبدء")
