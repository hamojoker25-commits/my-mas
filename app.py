# ============================================================
# 📊 Streamlit Sales Analyzer + AI + Logging + Full Analysis
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import re
import warnings
import os
from datetime import datetime
warnings.filterwarnings("ignore")

# ============================================================
# 📌 إنشاء مجلد لحفظ العمليات
# ============================================================
if not os.path.exists("operations_logs"):
    os.makedirs("operations_logs")

def save_operation(text, name):
    """حفظ أي عملية تحليل أو تقرير"""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"operations_logs/{name}_{timestamp}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)

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
    save_operation("تم تنفيذ عملية تنظيف البيانات", "cleaning")
    return df

# ============================================================
# 📌 التحليل الكامل لكل عناصر البيانات
# ============================================================
def full_analysis(df, col_product, col_sales, col_profit, col_date, col_customer="", col_region=""):
    report = {}

    # -----------------------------------
    # التحليل الأساسي
    # -----------------------------------
    report["total_sales"] = df[col_sales].sum()
    report["total_profit"] = df[col_profit].sum()
    report["profit_ratio"] = (df[col_profit].sum() / df[col_sales].sum()) * 100

    report["top_products"] = df.groupby(col_product)[col_sales].sum().sort_values(ascending=False).head(5)
    report["worst_products"] = df.groupby(col_product)[col_sales].sum().sort_values().head(5)
    report["top_profit_products"] = df.groupby(col_product)[col_profit].sum().sort_values(ascending=False).head(5)

    # -----------------------------------
    # إضافات التحليل
    # -----------------------------------
    if col_customer:
        report["top_customers"] = df.groupby(col_customer)[col_sales].sum().sort_values(ascending=False).head(5)
    else:
        report["top_customers"] = pd.Series([], dtype="float64")

    if col_region:
        report["top_regions"] = df.groupby(col_region)[col_sales].sum().sort_values(ascending=False).head(5)
    else:
        report["top_regions"] = pd.Series([], dtype="float64")

    report["avg_sale"] = df[col_sales].mean()
    report["avg_profit"] = df[col_profit].mean()

    # -----------------------------------
    # التحليل الزمني
    # -----------------------------------
    df_date = df.copy()
    df_date[col_date] = pd.to_datetime(df_date[col_date], errors="coerce")
    df_date["month"] = df_date[col_date].dt.to_period("M").astype(str)
    df_date["day"] = df_date[col_date].dt.to_period("D").astype(str)

    report["monthly_sales"] = df_date.groupby("month")[col_sales].sum()
    report["best_month"] = report["monthly_sales"].idxmax()
    report["worst_month"] = report["monthly_sales"].idxmin()

    report["daily_sales"] = df_date.groupby("day")[col_sales].sum()
    report["best_day"] = report["daily_sales"].idxmax()
    report["worst_day"] = report["daily_sales"].idxmin()

    save_operation(str(report), "analysis_full")
    return report

# ============================================================
# 📌 تقارير AI
# ============================================================
def ai_full_report(report):
    text = f"""
===============================
📊 AI FULL SMART REPORT
===============================

إجمالي المبيعات: {report['total_sales']:,}
إجمالي الأرباح: {report['total_profit']:,}
نسبة الربح: {report['profit_ratio']:.2f}%

🔥 أفضل المنتجات:
{report['top_products']}

⚠ أسوأ المنتجات:
{report['worst_products']}

💰 أعلى المنتجات ربحًا:
{report['top_profit_products']}

👥 أفضل العملاء:
{report['top_customers']}

🌍 أفضل المناطق:
{report['top_regions']}

📅 أفضل الشهور: {report['best_month']}
📅 أسوأ الشهور: {report['worst_month']}

📆 أفضل يوم: {report['best_day']}
📆 أسوأ يوم: {report['worst_day']}

🎯 توصيات:
- دعم المنتجات الأعلى مبيعًا
- إعادة تسعير المنتجات الضعيفة
- تحسين المخزون
- استهداف أفضل العملاء
"""
    save_operation(text, "AI_FULL")
    return text

def ai_short_report(report):
    text = f"""
===============================
📄 EXECUTIVE SUMMARY
===============================

إجمالي المبيعات: {report['total_sales']:,}
إجمالي الأرباح: {report['total_profit']:,}

أهم الفرص:
- المنتجات الأعلى مبيعًا
- تحسين هامش الربح
- استهداف العملاء المتكررين

المشاكل:
- المنتجات الراكدة
- تذبذب شهري
- انخفاض أرباح بعض المنتجات
"""
    save_operation(text, "AI_SHORT")
    return text

def ai_custom(report, choices):
    lines = []
    if "مبيعات" in choices:
        lines.append(f"إجمالي المبيعات: {report['total_sales']:,}")
        lines.append(f"أفضل الشهور: {report['best_month']}")
    if "أرباح" in choices:
        lines.append(f"إجمالي الأرباح: {report['total_profit']:,}")
        lines.append(f"نسبة الربح: {report['profit_ratio']:.2f}%")
    if "منتجات" in choices:
        lines.append("أفضل المنتجات:\n" + str(report['top_products']))
        lines.append("أسوأ المنتجات:\n" + str(report['worst_products']))

    text = "===============================\n📄 CUSTOM REPORT\n===============================\n\n"
    text += "\n".join(lines)
    save_operation(text, "AI_CUSTOM")
    return text

# ============================================================
# 🚀 واجهة Streamlit
# ============================================================
st.set_page_config(page_title="Sales Analyzer AI", layout="wide")
st.title("📊 Sales Analyzer + AI + Logging + Full Analysis")

if "report_mode" not in st.session_state:
    st.session_state.report_mode = None

uploaded = st.file_uploader("📂 ارفع ملف CSV أو Excel", type=["csv", "xlsx", "xls"])

if uploaded:
    if uploaded.name.endswith(".csv"):
        df = pd.read_csv(uploaded)
    else:
        df = pd.read_excel(uploaded)

    st.subheader("البيانات")
    st.dataframe(df.head())

    df = clean_data(df)

    st.subheader("📝 أدخل أسماء الأعمدة")

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
        report = full_analysis(df, col_product, col_sales, col_profit, col_date, col_customer, col_region)
        st.session_state.report = report
        st.success("تم التحليل بنجاح")

    if "report" in st.session_state:
        report = st.session_state.report

        st.subheader("📊 عرض النتائج المنسقة")

        st.metric("إجمالي المبيعات", f"{report['total_sales']:,}")
        st.metric("إجمالي الأرباح", f"{report['total_profit']:,}")

        st.dataframe(report['top_products'].reset_index(), use_container_width=True)
        st.dataframe(report['worst_products'].reset_index(), use_container_width=True)
        st.dataframe(report['top_profit_products'].reset_index(), use_container_width=True)
        if not report['top_customers'].empty:
            st.dataframe(report['top_customers'].reset_index(), use_container_width=True)
        if not report['top_regions'].empty:
            st.dataframe(report['top_regions'].reset_index(), use_container_width=True)

        st.line_chart(report['monthly_sales'])
        st.line_chart(report['daily_sales'])

        st.subheader("🤖 اختر نوع التقرير")
        choice = st.radio("نوع التقرير", ["تقرير كامل", "تقرير مختصر", "تقرير قابل للتخصيص"])

        if choice == "تقرير كامل":
            st.text(ai_full_report(report))
        elif choice == "تقرير مختصر":
            st.text(ai_short_report(report))
        else:
            options = st.multiselect("اختر نوع التحليل:", ["مبيعات", "أرباح", "منتجات"])
            if options:
                st.text(ai_custom(report, options))
            else:
                st.warning("اختر نوع واحد على الأقل")
