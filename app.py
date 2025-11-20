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
    # تنظيف أسماء الأعمدة فقط من المسافات الزائدة في البداية والنهاية
    df.columns = df.columns.astype(str).str.strip()
    
    df.dropna(axis=1, how='all', inplace=True)
    df.dropna(axis=0, how='all', inplace=True)
    df.replace(["-", "--", "N/A", "NA", "null"], np.nan, inplace=True)
    
    # محاولة تحويل الأرقام
    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col], errors="ignore")
        except:
            pass
    return df

# ============================================================
# 📌 التحليل الكامل
# ============================================================
def full_analysis(df, col_product, col_sales, col_profit, col_date, col_customer, col_region):
    report = {}

    # التأكد من نوع البيانات للأرقام
    df[col_sales] = pd.to_numeric(df[col_sales], errors='coerce').fillna(0)
    df[col_profit] = pd.to_numeric(df[col_profit], errors='coerce').fillna(0)

    # --- الأساسيات ---
    report["total_sales"] = df[col_sales].sum()
    report["total_profit"] = df[col_profit].sum()
    
    report["avg_selling_price"] = df[col_sales].mean()
    report["avg_profit_per_product"] = df[col_profit].mean()
    
    if report["total_sales"] > 0:
        report["profit_margin"] = (report["total_profit"] / report["total_sales"]) * 100
    else:
        report["profit_margin"] = 0

    # --- تحليلات المنتجات ---
    report["top_products"] = df.groupby(col_product)[col_sales].sum().sort_values(ascending=False).head(5)
    report["worst_products"] = df.groupby(col_product)[col_sales].sum().sort_values().head(5)
    report["top_profit_products"] = df.groupby(col_product)[col_profit].sum().sort_values(ascending=False).head(5)

    # --- تحليلات العملاء والمناطق ---
    # ملاحظة: نستخدم "لا يوجد" كخيار افتراضي في القائمة المنسدلة
    if col_customer and col_customer != "لا يوجد":
        report["top_customers"] = df.groupby(col_customer)[col_sales].sum().sort_values(ascending=False).head(5)
    else:
        report["top_customers"] = "لم يتم تحديد عمود العملاء"

    if col_region and col_region != "لا يوجد":
        report["top_regions"] = df.groupby(col_region)[col_sales].sum().sort_values(ascending=False).head(5)
    else:
        report["top_regions"] = "لم يتم تحديد عمود المنطقة"

    # --- معالجة التواريخ ---
    df_date = df.copy()
    df_date[col_date] = pd.to_datetime(df_date[col_date], errors="coerce")
    
    # حذف الصفوف التي لم يتم تحويل التاريخ فيها بنجاح
    df_date = df_date.dropna(subset=[col_date])
    
    df_date["month"] = df_date[col_date].dt.to_period("M").astype(str)
    df_date["day_name"] = df_date[col_date].dt.day_name()

    monthly_sales = df_date.groupby("month")[col_sales].sum()
    report["monthly_sales"] = monthly_sales
    
    monthly_change = monthly_sales.pct_change() * 100
    report["best_growth_month"] = monthly_change.idxmax() if not monthly_change.dropna().empty else "N/A"
    report["worst_drop_month"] = monthly_change.idxmin() if not monthly_change.dropna().empty else "N/A"

    daily_sales = df_date.groupby("day_name")[col_sales].sum().sort_values(ascending=False)
    report["best_day"] = daily_sales.index[0] if not daily_sales.empty else "N/A"
    report["worst_day"] = daily_sales.index[-1] if not daily_sales.empty else "N/A"

    # Forecast
    if len(monthly_sales) > 1:
        y = monthly_sales.values
        x = np.arange(len(y))
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        next_month_sales = p(len(y))
        report["forecast_next_month"] = next_month_sales
        report["trend_direction"] = "تصاعدي 📈" if z[0] > 0 else "تنازلي 📉"
    else:
        report["forecast_next_month"] = 0
        report["trend_direction"] = "غير كافٍ للتحليل"

    return report

# ============================================================
# 📌 تقارير AI
# ============================================================
def ai_full_report(report):
    return f"""
===============================
📊 AI FULL SMART REPORT
===============================
📌 الأداء المالي:
- إجمالي المبيعات: {report['total_sales']:,}
- إجمالي الأرباح: {report['total_profit']:,}
- نسبة هامش الربح: {report['profit_margin']:.2f}%

🌍 العملاء والمناطق:
- أهم المناطق: {report['top_regions'] if isinstance(report['top_regions'], str) else 'انظر الجدول'}
- أهم العملاء: {report['top_customers'] if isinstance(report['top_customers'], str) else 'انظر الجدول'}

📅 الزمن:
- أفضل يوم: {report['best_day']}
- الاتجاه: {report['trend_direction']}
- توقع الشهر القادم: {report['forecast_next_month']:,.2f}
"""

def ai_short_report(report):
    return f"""
===============================
📄 EXECUTIVE SUMMARY
===============================
✔ المبيعات: {report['total_sales']:,}
✔ الربح: {report['total_profit']:,}
✔ أفضل يوم: {report['best_day']}
✔ الاتجاه المستقبلي: {report['trend_direction']}
"""

# ============================================================
# 🚀 STREAMLIT APP
# ============================================================
st.set_page_config(page_title="Sales Analysis AI Pro", layout="wide")

st.title("📊 نظام تحليل بيانات المبيعات (بدون أخطاء)")
st.write("🔹 اختر الأعمدة من القوائم المنسدلة لتجنب الأخطاء.")

uploaded = st.file_uploader("📂 ارفع ملف CSV أو Excel", type=["csv", "xlsx", "xls"])

if uploaded:
    try:
        if uploaded.name.endswith(".csv"):
            df = pd.read_csv(uploaded)
        else:
            df = pd.read_excel(uploaded)
        
        df = clean_data(df)
        
        st.success("✅ تم تحميل الملف. الآن اختر الأعمدة المناسبة:")
        st.dataframe(df.head(3))
        
        # الحصول على قائمة الأعمدة
        columns_list = df.columns.tolist()

        # ---------------------------------------------------------
        # 🔥 التغيير الجذري هنا: استخدام القوائم المنسدلة بدلاً من الكتابة
        # ---------------------------------------------------------
        st.subheader("⚙️ إعداد الأعمدة (Mapping)")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            col_product = st.selectbox("📦 اختر عمود 'اسم المنتج'", options=columns_list, index=0)
        with c2:
            col_sales = st.selectbox("💰 اختر عمود 'المبيعات/الإيرادات'", options=columns_list, index=1 if len(columns_list) > 1 else 0)
        with c3:
            col_profit = st.selectbox("💵 اختر عمود 'الربح'", options=columns_list, index=2 if len(columns_list) > 2 else 0)

        c4, c5, c6 = st.columns(3)
        with c4:
            col_date = st.selectbox("📅 اختر عمود 'التاريخ'", options=columns_list, index=3 if len(columns_list) > 3 else 0)
        with c5:
            # نضيف خيار "لا يوجد" في حالة عدم توفر العمود
            col_customer = st.selectbox("bust اختر عمود 'العميل' (اختياري)", options=["لا يوجد"] + columns_list)
        with c6:
            col_region = st.selectbox("🌍 اختر عمود 'المنطقة' (اختياري)", options=["لا يوجد"] + columns_list)

        if st.button("🚀 بدء التحليل"):
            # التحقق من أن المستخدم لم يختر نفس العمود للحقول الأساسية (اختياري)
            with st.spinner('جاري تحليل البيانات...'):
                try:
                    report = full_analysis(
                        df, 
                        col_product, 
                        col_sales, 
                        col_profit, 
                        col_date, 
                        None if col_customer == "لا يوجد" else col_customer, 
                        None if col_region == "لا يوجد" else col_region
                    )

                    # --- عرض النتائج ---
                    st.success("✅ تم التحليل بنجاح!")
                    
                    # KPIs
                    k1, k2, k3, k4 = st.columns(4)
                    k1.metric("إجمالي المبيعات", f"{report['total_sales']:,.0f}")
                    k2.metric("إجمالي الأرباح", f"{report['total_profit']:,.0f}")
                    k3.metric("هامش الربح", f"{report['profit_margin']:.1f}%")
                    k4.metric("التنبؤ القادم", f"{report['forecast_next_month']:,.0f}")

                    # الجداول
                    row1_1, row1_2 = st.columns(2)
                    with row1_1:
                        st.write("##### 🥇 أفضل المنتجات")
                        st.dataframe(report["top_products"])
                    with row1_2:
                        st.write("##### 📉 المنتجات الأقل مبيعاً")
                        st.dataframe(report["worst_products"])

                    st.write("---")
                    st.subheader("🤖 تقرير الذكاء الاصطناعي")
                    st.text(ai_full_report(report))
                
                except Exception as e:
                    st.error(f"حدث خطأ أثناء التحليل: {e}")
                    st.warning("تأكد أن أعمدة المبيعات والربح تحتوي على أرقام، وعمود التاريخ يحتوي على تواريخ صحيحة.")

    except Exception as e:
        st.error(f"خطأ في قراءة الملف: {e}")
