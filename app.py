import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import IsolationForest
import plotly.express as px
import warnings

# تجاهل التحذيرات
warnings.filterwarnings('ignore')

# ==========================================
# إعداد الصفحة
# ==========================================
st.set_page_config(page_title="نظام تحليل المبيعات الذكي AI", layout="wide", page_icon="🤖")

# ==========================================
# الكلاسات (Logic Core)
# ==========================================

class AnalyticsEngine:
    def __init__(self, df):
        self.df = df
        # التعامل مع عمود الحالة إذا وجد، وإلا اعتبار الكل "Won"
        if 'Status' in df.columns:
            self.df_won = df[df['Status'] == 'Won']
        else:
            self.df_won = df

    def get_kpis(self):
        revenue = self.df_won['Sales'].sum()
        profit = self.df_won['Profit'].sum() if 'Profit' in self.df_won.columns else 0
        avg_deal = self.df_won['Sales'].mean()
        return revenue, profit, avg_deal

    def get_top_products(self):
        return self.df_won.groupby('Product')['Sales'].sum().sort_values(ascending=False).head(5)

    def get_rfm_segments(self):
        last_date = self.df_won['Date'].max()
        rfm = self.df_won.groupby('Customer').agg({
            'Date': lambda x: (last_date - x.max()).days,
            'Sales': 'sum'
        }).rename(columns={'Date': 'Days_Since_Last_Buy', 'Sales': 'Total_Spend'})
        return rfm.sort_values('Total_Spend', ascending=False).head(5)

class AIEngine:
    def __init__(self, df):
        self.df = df

    def detect_anomalies(self):
        # التأكد من خلو البيانات من القيم الفارغة قبل الذكاء الاصطناعي
        features = self.df[['Sales']].fillna(0)
        if 'Profit' in self.df.columns:
            features = self.df[['Sales', 'Profit']].fillna(0)
            
        model = IsolationForest(contamination=0.01, random_state=42)
        self.df['Anomaly'] = model.fit_predict(features)
        return self.df[self.df['Anomaly'] == -1]

    def predict_churn_risk(self):
        last_date = self.df['Date'].max()
        customers = self.df.groupby('Customer')['Date'].max().reset_index()
        customers['Days_Inactive'] = (last_date - customers['Date']).dt.days
        # العميل خطر لو بقاله اكتر من 90 يوم ما اشترى
        return customers[customers['Days_Inactive'] > 90].sort_values('Days_Inactive', ascending=False).head(10)

# ==========================================
# واجهة التطبيق والمنطق الرئيسي
# ==========================================

st.title("🤖 نظام تحليل المبيعات الذكي المتكامل")
st.markdown("---")

# 1. التحميل
st.sidebar.header("📂 البيانات")
uploaded_file = st.sidebar.file_uploader("ارفع ملف المبيعات (Excel/CSV)", type=['xlsx', 'csv'])

df = None

# دالة لإنشاء بيانات تجريبية لو مفيش ملف
def load_demo_data():
    np.random.seed(42)
    dates = [datetime(2024, 1, 1) + timedelta(days=x) for x in range(365)]
    data = {
        'Date': np.random.choice(dates, 1000),
        'Customer': np.random.choice(['Client A', 'Client B', 'Client C', 'Client D'], 1000),
        'Product': np.random.choice(['Product X', 'Product Y', 'Product Z'], 1000),
        'Sales': np.random.randint(100, 5000, 1000),
        'Profit': np.random.randint(10, 1000, 1000),
        'Status': np.random.choice(['Won', 'Won', 'Lost'], 1000)
    }
    return pd.DataFrame(data)

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            raw_df = pd.read_csv(uploaded_file)
        else:
            raw_df = pd.read_excel(uploaded_file)
        
        st.sidebar.success("تم رفع الملف! يرجى تحديد الأعمدة 👇")
        
        # 2. تعيين الأعمدة (Mapping) - هذا هو الجزء الذي يحل المشكلة
        st.sidebar.markdown("### 🔗 ربط الأعمدة")
        st.sidebar.info("اختر العمود المناسب من ملفك لكل خانة:")
        
        cols = raw_df.columns.tolist()
        
        col_date = st.sidebar.selectbox("عمود التاريخ (Date)", cols, index=0)
        col_customer = st.sidebar.selectbox("عمود العميل (Customer)", cols, index=min(1, len(cols)-1))
        col_product = st.sidebar.selectbox("عمود المنتج (Product)", cols, index=min(2, len(cols)-1))
        col_sales = st.sidebar.selectbox("عمود المبيعات/المبلغ (Sales)", cols, index=min(3, len(cols)-1))
        
        # أعمدة اختيارية
        has_profit = st.sidebar.checkbox("لدي عمود للأرباح")
        col_profit = None
        if has_profit:
            col_profit = st.sidebar.selectbox("عمود الأرباح (Profit)", cols)
            
        has_status = st.sidebar.checkbox("لدي عمود لحالة الصفقة (Won/Lost)")
        col_status = None
        if has_status:
            col_status = st.sidebar.selectbox("عمود الحالة (Status)", cols)

        # زر التطبيق
        if st.sidebar.button("تحليل البيانات"):
            # إعادة تسمية الأعمدة لأسماء قياسية يفهمها الكود
            df = raw_df.copy()
            rename_map = {
                col_date: 'Date',
                col_customer: 'Customer',
                col_product: 'Product',
                col_sales: 'Sales'
            }
            if has_profit and col_profit:
                rename_map[col_profit] = 'Profit'
            if has_status and col_status:
                rename_map[col_status] = 'Status'
            
            df.rename(columns=rename_map, inplace=True)
            
            # تنظيف وتجهيز البيانات
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            df['Sales'] = pd.to_numeric(df['Sales'], errors='coerce')
            
            if 'Profit' not in df.columns:
                df['Profit'] = df['Sales'] * 0.20 # افتراض ربح 20% لو مش موجود
            else:
                df['Profit'] = pd.to_numeric(df['Profit'], errors='coerce')

            df.dropna(subset=['Date', 'Sales'], inplace=True)
            
    except Exception as e:
        st.error(f"حدث خطأ في قراءة الملف: {e}")

else:
    # تشغيل Demo Mode
    if st.sidebar.checkbox("استخدام بيانات تجريبية", value=True):
        df = load_demo_data()
        st.sidebar.info("يعمل الآن على بيانات تجريبية.")

# 3. المحركات والواجهة (فقط لو الداتا جاهزة)
if df is not None:
    analytics = AnalyticsEngine(df)
    ai = AIEngine(df)

    # --------------------------------------------
    # لوحة المعلومات (Dashboard)
    # --------------------------------------------
    st.subheader("📊 نظرة عامة (KPIs)")
    rev, prof, avg = analytics.get_kpis()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("إجمالي الإيرادات", f"${rev:,.0f}")
    c2.metric("إجمالي الأرباح", f"${prof:,.0f}")
    c3.metric("متوسط الصفقة", f"${avg:,.0f}")

    # --------------------------------------------
    # الذكاء الاصطناعي (AI Insights)
    # --------------------------------------------
    st.markdown("---")
    st.subheader("🧠 تحليلات الذكاء الاصطناعي")
    
    tab1, tab2, tab3 = st.tabs(["🚨 كشف الأخطاء (Anomalies)", "⚠️ خطر الانسحاب (Churn)", "🏆 أفضل العملاء"])
    
    with tab1:
        st.write("يقوم الذكاء الاصطناعي بالبحث عن عمليات بيع غير منطقية:")
        anomalies = ai.detect_anomalies()
        if not anomalies.empty:
            st.error(f"تم اكتشاف {len(anomalies)} عملية مشبوهة!")
            st.dataframe(anomalies)
        else:
            st.success("البيانات سليمة، لم يتم اكتشاف شواذ.")

    with tab2:
        st.write("عملاء لم يشتروا منذ أكثر من 90 يوماً:")
        risk = ai.predict_churn_risk()
        if not risk.empty:
            st.dataframe(risk)
        else:
            st.info("لا يوجد عملاء في دائرة الخطر.")

    with tab3:
        st.write("أفضل العملاء (VIP) بناءً على إجمالي الإنفاق:")
        st.dataframe(analytics.get_rfm_segments())

    # --------------------------------------------
    # الشات بوت (Chatbot Interaction)
    # --------------------------------------------
    st.markdown("---")
    st.subheader("💬 المساعد الذكي (AI Assistant)")
    
    user_query = st.text_input("اسأل النظام عن البيانات (مثلاً: أفضل منتج، هل هناك مشاكل، تقرير):")
    
    if user_query:
        q = user_query.lower()
        if "مبيعات" in q or "ايراد" in q:
            st.info(f"💰 إجمالي الإيرادات هو: ${rev:,.2f}")
        elif "منتج" in q:
            st.bar_chart(analytics.get_top_products())
        elif "عميل" in q:
            st.write("أهم العملاء:")
            st.table(analytics.get_rfm_segments())
        elif "خطر" in q or "مشكلة" in q or "خطأ" in q:
            anoms = len(ai.detect_anomalies())
            risk_count = len(ai.predict_churn_risk())
            st.warning(f"تم اكتشاف {anoms} عمليات شاذة، و {risk_count} عملاء معرضين للخطر.")
        elif "تقرير" in q:
            st.success(f"تقرير سريع:\n- المبيعات: {rev:,.0f}\n- الأرباح: {prof:,.0f}\n- متوسط الصفقة: {avg:,.0f}")
        else:
            st.write("🤖 أنا مساعد لتحليل البيانات، اسألني عن المبيعات أو العملاء.")

else:
    st.info("👈 يرجى رفع ملف وتحديد الأعمدة من القائمة الجانبية، أو تفعيل البيانات التجريبية.")
