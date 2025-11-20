import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
from sklearn.ensemble import IsolationForest
import warnings

# تجاهل التحذيرات
warnings.filterwarnings('ignore')

# ==========================================
# إعداد الصفحة
# ==========================================
st.set_page_config(page_title="نظام تحليل المبيعات الذكي AI", layout="wide", page_icon="🤖")

# ==============================================================================
# 1. إعدادات النظام (Configuration)
# ==============================================================================
COLUMN_MAPPING = {
    'Date': 'Date',
    'Customer': 'Customer',
    'Product': 'Product',
    'Sales': 'Total_Sales',
    'Status': 'Status',
    'Profit': 'Profit'
}

# ==============================================================================
# 2. الكلاسات (Logic Core) - نفس منطقك القوي
# ==============================================================================
class DataProcessor:
    def __init__(self, uploaded_file=None):
        self.uploaded_file = uploaded_file
        self.df = None

    def create_demo_data(self):
        """إنشاء بيانات وهمية"""
        np.random.seed(42)
        num_records = 1000
        dates = [datetime(2024, 1, 1) + timedelta(days=x) for x in range(365)]
        
        data = {
            'Date': np.random.choice(dates, num_records),
            'Customer': np.random.choice(['شركة ألفا', 'مؤسسة النور', 'سوبر ماركت الخير', 'Tech Solutions', 'Global Corp'], num_records),
            'Product': np.random.choice(['Laptop HP', 'Server Dell', 'Software License', 'Maintenance', 'Mouse'], num_records),
            'Total_Sales': np.random.randint(100, 5000, num_records),
            'Status': np.random.choice(['Won', 'Lost'], num_records, p=[0.8, 0.2])
        }
        df = pd.DataFrame(data)
        # إضافة قيم شاذة
        df.loc[990] = [datetime(2024, 6, 1), 'Client X', 'Laptop HP', 150000, 'Won'] 
        return df

    def load_data(self):
        if self.uploaded_file is None:
            self.df = self.create_demo_data()
            return self.df, "demo"
        else:
            try:
                if self.uploaded_file.name.endswith('.csv'):
                    self.df = pd.read_csv(self.uploaded_file)
                else:
                    self.df = pd.read_excel(self.uploaded_file)
                
                inv_map = {v: k for k, v in COLUMN_MAPPING.items() if v in self.df.columns}
                self.df.rename(columns=inv_map, inplace=True)
                
                self.df['Date'] = pd.to_datetime(self.df['Date'])
                
                if 'Profit' not in self.df.columns and 'Sales' in self.df.columns:
                    self.df['Profit'] = self.df['Sales'] * 0.20
                
                return self.df, "uploaded"
            except Exception as e:
                st.error(f"خطأ في قراءة الملف: {e}")
                return None, "error"

class AnalyticsEngine:
    def __init__(self, df):
        self.df = df
        self.df_won = df[df['Status'] == 'Won'] if 'Status' in df.columns else df

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
        return rfm.sort_values('Total_Spend', ascending=False).head(3)

class AIEngine:
    def __init__(self, df):
        self.df = df

    def detect_anomalies(self):
        if 'Sales' not in self.df.columns: return pd.DataFrame()
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
        return customers[customers['Days_Inactive'] > 90].sort_values('Days_Inactive', ascending=False).head(5)

# ==============================================================================
# 3. واجهة التطبيق (Streamlit Interface)
# ==============================================================================

st.title("🤖 نظام تحليل المبيعات الذكي المتكامل")
st.markdown("---")

# الشريط الجانبي للتحميل
st.sidebar.header("📂 البيانات")
uploaded_file = st.sidebar.file_uploader("ارفع ملف المبيعات (Excel/CSV)", type=['xlsx', 'csv'])

# زر لاستخدام بيانات تجريبية
use_demo = st.sidebar.checkbox("استخدام بيانات تجريبية (Demo)", value=True if not uploaded_file else False)

# منطق التحميل
processor = DataProcessor(uploaded_file if not use_demo else None)
df, status = processor.load_data()

if df is not None:
    analytics = AnalyticsEngine(df)
    ai = AIEngine(df)

    # عرض رسالة الحالة
    if status == "demo":
        st.warning("⚠️ يتم العمل الآن على بيانات تجريبية وهمية.")
    else:
        st.success("✅ تم تحميل بياناتك بنجاح.")

    # --------------------------------------------
    # لوحة المعلومات (Dashboard)
    # --------------------------------------------
    st.subheader("📊 نظرة عامة (KPIs)")
    rev, prof, avg = analytics.get_kpis()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("إجمالي الإيرادات", f"${rev:,.0f}")
    col2.metric("إجمالي الأرباح", f"${prof:,.0f}")
    col3.metric("متوسط الصفقة", f"${avg:,.0f}")

    # --------------------------------------------
    # الذكاء الاصطناعي (AI Insights)
    # --------------------------------------------
    st.markdown("---")
    st.subheader("🧠 تحليلات الذكاء الاصطناعي")
    
    tab1, tab2, tab3 = st.tabs(["🚨 كشف الأخطاء (Anomalies)", "⚠️ خطر الانسحاب (Churn)", "🏆 أفضل العملاء"])
    
    with tab1:
        st.write("يقوم الذكاء الاصطناعي بالبحث عن أرقام مريبة أو غير منطقية:")
        anomalies = ai.detect_anomalies()
        if not anomalies.empty:
            st.error(f"تم اكتشاف {len(anomalies)} عملية مشبوهة!")
            st.dataframe(anomalies[['Date', 'Customer', 'Sales', 'Profit']])
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
        st.write("أفضل العملاء (VIP) بناءً على الإنفاق والحداثة:")
        st.dataframe(analytics.get_rfm_segments())

    # --------------------------------------------
    # الشات بوت (Chatbot Interaction)
    # --------------------------------------------
    st.markdown("---")
    st.subheader("💬 اسأل النظام (AI Chatbot)")
    
    user_query = st.text_input("اكتب سؤالك هنا (مثلاً: ما هو أفضل منتج؟، هل هناك أخطاء؟، تقرير):")
    
    if user_query:
        query = user_query.lower()
        response = ""
        
        if "مبيعات" in query or "ايراد" in query:
            response = f"💰 إجمالي الإيرادات: ${rev:,.2f}"
        elif "منتج" in query or "افضل" in query:
            top = analytics.get_top_products()
            st.bar_chart(top)
            response = "تم عرض رسم بياني لأفضل المنتجات."
        elif "عميل" in query or "vip" in query:
            vip = analytics.get_rfm_segments()
            st.table(vip)
            response = "هذه قائمة بأفضل عملائك."
        elif "خطر" in query or "انسحاب" in query:
            risk = ai.predict_churn_risk()
            st.dataframe(risk)
            response = "هؤلاء العملاء معرضون لخطر الانسحاب."
        elif "خطأ" in query or "مشكلة" in query:
            anomalies = ai.detect_anomalies()
            if not anomalies.empty:
                st.dataframe(anomalies)
                response = "تم العثور على هذه العمليات الشاذة."
            else:
                response = "✅ البيانات نظيفة تماماً."
        elif "تقرير" in query:
            response = f"""
            📊 **تقرير سريع:**
            - المبيعات: ${rev:,.0f}
            - الأرباح: ${prof:,.0f}
            - عدد العمليات: {len(df)}
            """
        else:
            response = "🤔 لم أفهم السؤال بدقة. جرب أن تسأل عن: المبيعات، أفضل منتج، الأخطاء."
            
        st.info(response)

else:
    st.info("الرجاء رفع ملف بيانات للبدء.")
