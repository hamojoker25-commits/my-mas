import streamlit as st
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

# ============================================================
# 📌 تنظيف البيانات
# ============================================================
def clean_data(df):
    df = df.copy()
    df.dropna(axis=1, how='all', inplace=True)
    df.dropna(axis=0, how='all', inplace=True)
    df.columns = [col.strip().replace(" ", "_") for col in df.columns]
    df.replace(["-", "--", "N/A", "NA", "null"], np.nan, inplace=True)
    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col], errors="ignore")
        except:
            pass
    return df

# ============================================================
# 📌 التحليل الكامل (تم التحديث)
# ============================================================
def full_analysis(df, col_product, col_sales, col_profit, col_date, col_customer=None, col_region=None):
    report = {}

    # --- الأساسيات ---
    report["total_sales"] = df[col_sales].sum()
    report["total_profit"] = df[col_profit].sum()
    
    # --- التحليلات الجديدة (المتوسطات والنسب) ---
    report["avg_selling_price"] = df[col_sales].mean()  # متوسط سعر البيع
    report["avg_profit_per_product"] = df[col_profit].mean() # متوسط الربح لكل منتج
    
    if report["total_sales"] > 0:
        report["profit_margin"] = (report["total_profit"] / report["total_sales"]) * 100 # نسبة الربح
    else:
        report["profit_margin"] = 0

    # --- تحليلات المنتجات ---
    report["top_products"] = df.groupby(col_product)[col_sales].sum().sort_values(ascending=False).head(5)
    report["worst_products"] = df.groupby(col_product)[col_sales].sum().sort_values().head(5)
    report["top_profit_products"] = df.groupby(col_product)[col_profit].sum().sort_values(ascending=False).head(5)

    # --- تحليلات العملاء والمناطق (جديد) ---
    if col_customer:
        report["top_customers"] = df.groupby(col_customer)[col_sales].sum().sort_values(ascending=False).head(5)
    else:
        report["top_customers"] = "لم يتم تحديد عمود العملاء"

    if col_region:
        report["top_regions"] = df.groupby(col_region)[col_sales].sum().sort_values(ascending=False).head(5)
    else:
        report["top_regions"] = "لم يتم تحديد عمود المنطقة"

    # --- معالجة التواريخ ---
    df_date = df.copy()
    df_date[col_date] = pd.to_datetime(df_date[col_date], errors="coerce")
    df_date["month"] = df_date[col_date].dt.to_period("M").astype(str)
    df_date["day_name"] = df_date[col_date].dt.day_name() # اسم اليوم

    # --- المبيعات الشهرية والنمو ---
    monthly_sales = df_date.groupby("month")[col_sales].sum()
    report["monthly_sales"] = monthly_sales
    
    # حساب أكثر الشهور نموًا وهبوطًا (Change %)
    monthly_change = monthly_sales.pct_change() * 100
    report["best_growth_month"] = monthly_change.idxmax() if not monthly_change.dropna().empty else "N/A"
    report["worst_drop_month"] = monthly_change.idxmin() if not monthly_change.dropna().empty else "N/A"

    # --- تحليل الأيام (Best/Worst Day) ---
    daily_sales = df_date.groupby("day_name")[col_sales].sum().sort_values(ascending=False)
    report["best_day"] = daily_sales.index[0] if not daily_sales.empty else "N/A"
    report["worst_day"] = daily_sales.index[-1] if not daily_sales.empty else "N/A"

    # --- تحليل التنبؤ البسيط (Forecast Trend) ---
    # نستخدم Linear Regression بسيط بناءً على أرقام الشهور
    if len(monthly_sales) > 1:
        y = monthly_sales.values
        x = np.arange(len(y))
        z = np.polyfit(x, y, 1) # الميل
        p = np.poly1d(z)
        next_month_sales = p(len(y)) # التنبؤ للشهر القادم
        report["forecast_next_month"] = next_month_sales
        report["trend_direction"] = "تصاعدي 📈" if z[0] > 0 else "تنازلي 📉"
    else:
        report["forecast_next_month"] = 0
        report["trend_direction"] = "غير كافٍ للتحليل"

    return report

# ============================================================
# 📌 تقرير AI كامل (محدث)
# ============================================================
def ai_full_report(report):
    return f"""
===============================
📊 AI FULL SMART REPORT
===============================

📌 الأداء المالي العام:
- إجمالي المبيعات: {report['total_sales']:,}
- إجمالي الأرباح: {report['total_profit']:,}
- نسبة هامش الربح: {report['profit_margin']:.2f}%
- متوسط سعر البيع (ASP): {report['avg_selling_price']:.2f}
- متوسط ربح المنتج: {report['avg_profit_per_product']:.2f}

-------------------------------
🌍 التحليل الجغرافي والعملاء:
- أفضل المناطق: 
{report['top_regions'] if isinstance(report['top_regions'], pd.Series) else report['top_regions']}

- أهم العملاء (VIP):
{report['top_customers'] if isinstance(report['top_customers'], pd.Series) else report['top_customers']}

-------------------------------
🔥 أفضل المنتجات:
{report['top_products']}

-------------------------------
⚠️ أسوأ المنتجات:
{report['worst_products']}

-------------------------------
📅 تحليل الزمن والاتجاهات:
- أفضل يوم للبيع: {report['best_day']}
- أسوأ يوم للبيع: {report['worst_day']}
- شهر النمو القياسي: {report['best_growth_month']}
- أكبر شهر هبوط: {report['worst_drop_month']}

🔮 التنبؤ المستقبلي (Forecast):
- الاتجاه العام: {report['trend_direction']}
- المتوقع للشهر القادم: {report['forecast_next_month']:,.2f}

===============================
🎯 تحليل الذكاء الاصطناعي:
===============================
✔ هامش الربح الحالي {report['profit_margin']:.1f}% يحتاج لمراقبة مستمرة.
✔ ركّز تسويقك في يوم {report['best_day']} لأنه الأنشط.
✔ المناطق الأعلى مبيعًا تحتاج دعم لوجيستي لضمان استمرار النمو.
✔ التنبؤ يشير لاتجاه {report['trend_direction']}، استعد لذلك بالمخزون المناسب.
"""

# ============================================================
# 📌 تقرير AI مختصر
# ============================================================
def ai_short_report(report):
    return f"""
===============================
📄 EXECUTIVE SUMMARY
===============================

✔ إجمالي المبيعات: {report['total_sales']:,}  
✔ صافي الربح: {report['total_profit']:,} ({report['profit_margin']:.1f}%)
✔ التنبؤ القادم: {report['trend_direction']}

🔥 الفرص الذهبية:
- التركيز على عملاء الـ VIP.
- تعزيز المبيعات في يوم {report['best_day']}.
- التوسع في المناطق الأعلى طلبًا.

⚠ المخاطر:
- منتجات راكدة.
- تذبذب النمو في شهر {report['worst_drop_month']}.
"""

# ============================================================
# 🚀 STREAMLIT APP
# ============================================================
st.set_page_config(page_title="Sales Analysis AI Pro", layout="wide")

st.title("📊 نظام تحليل بيانات المبيعات + تقارير AI (نسخة احترافية)")
st.write("🔹 يدعم: التنبؤ، تحليل العملاء، المناطق، هوامش الربح، والمزيد.")

# ====================================================================
# تحميل الملف
# ====================================================================
uploaded = st.file_uploader("📂 ارفع ملف CSV أو Excel", type=["csv", "xlsx", "xls"])

if uploaded:
    if uploaded.name.endswith(".csv"):
        df = pd.read_csv(uploaded)
    else:
        df = pd.read_excel(uploaded)

    st.success("✅ تم تحميل الملف بنجاح")

    st.subheader("📄 عرض البيانات")
    st.dataframe(df.head(10))

    df = clean_data(df)

    st.subheader("📝 أدخل أسماء الأعمدة (عربي/إنجليزي)")

    col1, col2 = st.columns(2)
    with col1:
        col_product = st.text_input("عمود المنتج (مطلوب):")
        col_sales = st.text_input("عمود المبيعات (مطلوب):")
        col_profit = st.text_input("عمود الربح (مطلوب):")

    with col2:
        col_date = st.text_input("عمود التاريخ (مطلوب):")
        col_customer = st.text_input("عمود العميل (اختياري - للتحليل):")
        col_region = st.text_input("عمود المنطقة (اختياري - للتحليل):")

    if st.button("🚀 بدء التحليل المتقدم"):
        if col_product and col_sales and col_profit and col_date:
            
            # استدعاء دالة التحليل المحدثة
            report = full_analysis(df, col_product, col_sales, col_profit, col_date, col_customer, col_region)

            st.success("✅ تم تنفيذ التحليل بنجاح")

            # --- عرض النتائج بالأرقام الكبيرة (KPIs) ---
            st.markdown("---")
            st.subheader("📌 المؤشرات الرئيسية (KPIs)")
            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            kpi1.metric("إجمالي المبيعات", f"{report['total_sales']:,.0f}")
            kpi2.metric("إجمالي الأرباح", f"{report['total_profit']:,.0f}")
            kpi3.metric("نسبة الربح (Margin)", f"{report['profit_margin']:.2f}%")
            kpi4.metric("متوسط قيمة الطلب", f"{report['avg_selling_price']:.2f}")

            # --- عرض الجداول والتحليلات ---
            c1, c2 = st.columns(2)
            
            with c1:
                st.write("### 🥇 أفضل المنتجات")
                st.dataframe(report["top_products"])
                
                st.write("### 💵 المنتجات الأعلى ربحًا")
                st.dataframe(report["top_profit_products"])
                
                if col_customer:
                    st.write("### 👥 أعلى العملاء شراءً")
                    st.dataframe(report["top_customers"])

            with c2:
                st.write("### 🐌 أسوأ المنتجات")
                st.dataframe(report["worst_products"])
                
                st.write("### 📅 المبيعات الشهرية")
                st.dataframe(report["monthly_sales"])

                if col_region:
                    st.write("### 🌍 المناطق الأعلى مبيعًا")
                    st.dataframe(report["top_regions"])

            # --- قسم التحليل الزمني والتنبؤ ---
            st.markdown("---")
            st.subheader("⏳ التحليل الزمني والتنبؤ (Time Series & AI Forecast)")
            
            t1, t2, t3 = st.columns(3)
            t1.info(f"📅 أفضل يوم في الأسبوع: **{report['best_day']}**")
            t2.warning(f"📉 أسوأ يوم في الأسبوع: **{report['worst_day']}**")
            t3.success(f"🚀 اتجاه التنبؤ (Trend): **{report['trend_direction']}**")

            st.write(f"📊 **توقع المبيعات للشهر القادم:** {report['forecast_next_month']:,.2f}")
            
            st.write("---")
            st.subheader("🤖 تقرير AI المطور")

            report_type = st.radio(
                "اختر نوع التقرير:",
                ["تقرير كامل", "تقرير مختصر", "الاثنين معًا"]
            )

            if report_type == "تقرير كامل":
                st.text(ai_full_report(report))
            elif report_type == "تقرير مختصر":
                st.text(ai_short_report(report))
            else:
                st.text(ai_full_report(report))
                st.text(ai_short_report(report))

        else:
            st.error("❌ يجب إدخال جميع أسماء الأعمدة الأساسية (المنتج، المبيعات، الربح، التاريخ) أولاً")
