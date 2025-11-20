# ============================================================
# 🔥 نظام تحليل بيانات المبيعات + AI كامل ومختصر عبر Streamlit
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import re
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
# 📌 التحليل الكامل
# ============================================================
def full_analysis(df, col_product, col_sales, col_profit, col_date):

    report = {}

    report["total_sales"] = df[col_sales].sum()
    report["total_profit"] = df[col_profit].sum()

    report["top_products"] = (
        df.groupby(col_product)[col_sales].sum().sort_values(ascending=False).head(5)
    )

    report["worst_products"] = (
        df.groupby(col_product)[col_sales].sum().sort_values().head(5)
    )

    report["top_profit_products"] = (
        df.groupby(col_product)[col_profit].sum().sort_values(ascending=False).head(5)
    )

    df_date = df.copy()
    df_date[col_date] = pd.to_datetime(df_date[col_date], errors="coerce")
    df_date["month"] = df_date[col_date].dt.to_period("M").astype(str)

    report["monthly_sales"] = (
        df_date.groupby("month")[col_sales].sum()
    )

    return report

# ============================================================
# 📌 تقرير AI كامل
# ============================================================
def ai_full_report(report):
    return f"""
===============================
📊 AI FULL SMART REPORT
===============================

📌 إجمالي المبيعات: {report['total_sales']:,}
📌 إجمالي الأرباح: {report['total_profit']:,}

-------------------------------
🔥 أفضل المنتجات:
{report['top_products']}

-------------------------------
⚠️ أسوأ المنتجات:
{report['worst_products']}

-------------------------------
💰 أكثر المنتجات ربحية:
{report['top_profit_products']}

-------------------------------
📅 المبيعات الشهرية:
{report['monthly_sales']}

===============================
🎯 تحليل الذكاء الاصطناعي:
===============================

✔ ركّز على المنتجات الأعلى مبيعًا.  
✔ المنتجات الضعيفة تحتاج تخفيضات أو إعادة تسعير.  
✔ ارتفاع المبيعات لا يعني ارتفاع الأرباح — راقب هوامش الربح.  
✔ لو في تذبذب شهري → موسمية السوق تؤثر على المبيعات.  
✔ قلل المخزون الزائد لزيادة الربحية.

===============================
🚀 توصيات لتحسين الأداء:
===============================

1️⃣ دعم المنتجات الأعلى طلبًا.  
2️⃣ عروض على المنتجات الراكدة.  
3️⃣ رفع هامش الربح للمنتجات المطلوبة.  
4️⃣ تحسين سلسلة التوريد.  
5️⃣ مراقبة الاتجاهات الشهرية.
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
✔ إجمالي الأرباح: {report['total_profit']:,}

🔥 أهم الفرص:
- دعم أفضل المنتجات.
- إعادة تسعير المنتجات الضعيفة.
- تحسين هامش الربح.

⚠ المشاكل:
- منتجات بطيئة.
- أرباح منخفضة لبعض المنتجات.
- تذبذب شهري.

🚀 الحلول:
- عروض.
- تحسين المخزون.
- رفع التسويق.
"""

# ============================================================
# 🚀 STREAMLIT APP
# ============================================================
st.set_page_config(page_title="Sales Analysis AI", layout="wide")

st.title("📊 نظام تحليل بيانات المبيعات + تقارير AI")
st.write("🔹 يدعم عربي + إنجليزي — يعمل على Streamlit — جاهز لأي ملف")

# ====================================================================
# تحميل الملف
# ====================================================================
uploaded = st.file_uploader("📂 ارفع ملف CSV أو Excel", type=["csv", "xlsx", "xls"])

if uploaded:
    # قراءة الملف
    if uploaded.name.endswith(".csv"):
        df = pd.read_csv(uploaded)
    else:
        df = pd.read_excel(uploaded)

    st.success("✅ تم تحميل الملف بنجاح")

    # عرض أول 10 صفوف
    st.subheader("📄 عرض البيانات")
    st.dataframe(df.head(10))

    # تنظيف
    df = clean_data(df)

    # إدخال أسماء الأعمدة
    st.subheader("📝 أدخل أسماء الأعمدة (عربي/إنجليزي)")

    col1, col2 = st.columns(2)
    with col1:
        col_product = st.text_input("عمود المنتج:")
        col_sales = st.text_input("عمود المبيعات:")
        col_profit = st.text_input("عمود الربح:")

    with col2:
        col_date = st.text_input("عمود التاريخ:")
        col_customer = st.text_input("عمود العميل (اختياري):")
        col_region = st.text_input("عمود المنطقة (اختياري):")

    if st.button("🚀 بدء التحليل"):
        if col_product and col_sales and col_profit and col_date:

            report = full_analysis(df, col_product, col_sales, col_profit, col_date)

            st.success("✅ تم تنفيذ التحليل بنجاح")

            # عرض النتائج
            st.subheader("📊 نتائج التحليل")
            st.write("### 🔥 إجمالي المبيعات:", report["total_sales"])
            st.write("### 💰 إجمالي الأرباح:", report["total_profit"])

            st.write("### 🥇 أفضل المنتجات")
            st.dataframe(report["top_products"])

            st.write("### 🐌 أسوأ المنتجات")
            st.dataframe(report["worst_products"])

            st.write("### 💵 المنتجات الأعلى ربحًا")
            st.dataframe(report["top_profit_products"])

            st.write("### 📅 المبيعات الشهرية")
            st.dataframe(report["monthly_sales"])

            st.subheader("🤖 تقرير AI")

            # اختيار نوع التقرير
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
            st.error("❌ يجب إدخال جميع أسماء الأعمدة الأساسية أولاً")
