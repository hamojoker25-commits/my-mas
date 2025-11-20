import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import warnings

# تجاهل التحذيرات
warnings.filterwarnings('ignore')

# ==========================================
# 1. إعداد الصفحة
# ==========================================
st.set_page_config(
    page_title="نظام المحلل الذكي الشامل AI", 
    layout="wide", 
    page_icon="🤖"
)

# ==========================================
# 2. إدارة الذاكرة (Session State) - حل مشكلة نسيان الملف
# ==========================================
if 'data' not in st.session_state:
    st.session_state.data = None
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# ==========================================
# 3. كلاسات الذكاء الاصطناعي (AI Core)
# ==========================================
class AIEngine:
    def __init__(self, df):
        self.df = df

    def detect_anomalies(self):
        """كشف القيم الشاذة باستخدام Isolation Forest"""
        try:
            # نستخدم المبيعات والأرباح للكشف
            features = self.df[['Sales', 'Profit']].fillna(0)
            model = IsolationForest(contamination=0.02, random_state=42)
            self.df['Is_Anomaly'] = model.fit_predict(features)
            anomalies = self.df[self.df['Is_Anomaly'] == -1]
            return anomalies
        except:
            return pd.DataFrame()

    def segment_customers(self):
        """تصنيف العملاء باستخدام K-Means Clustering"""
        try:
            # تجميع البيانات حسب العميل
            customer_data = self.df.groupby('Customer').agg({
                'Sales': 'sum',
                'Date': 'max' # للحداثة
            }).reset_index()
            
            # تجهيز البيانات
            X = customer_data[['Sales']]
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # تطبيق التقسيم لـ 3 فئات
            kmeans = KMeans(n_clusters=3, random_state=42)
            customer_data['Cluster'] = kmeans.fit_predict(X_scaled)
            
            # تسمية الفئات بناء على متوسط الإنفاق
            cluster_avg = customer_data.groupby('Cluster')['Sales'].mean().sort_values()
            mapping = {
                cluster_avg.index[0]: 'عميل عادي (Bronze)',
                cluster_avg.index[1]: 'عميل مميز (Silver)',
                cluster_avg.index[2]: 'عميل VIP (Gold)'
            }
            customer_data['Segment'] = customer_data['Cluster'].map(mapping)
            return customer_data
        except:
            return pd.DataFrame()

    def generate_report(self):
        """توليد تقرير نصي ذكي"""
        total_sales = self.df['Sales'].sum()
        total_profit = self.df['Profit'].sum()
        top_product = self.df.groupby('Product')['Sales'].sum().idxmax()
        anomalies_count = len(self.detect_anomalies())
        
        report = f"""
        📊 **التقرير التحليلي الذكي:**
        - **الأداء المالي:** حققت الشركة مبيعات إجمالية قدرها {total_sales:,.2f} وأرباحاً {total_profit:,.2f}.
        - **المنتج النجم:** المنتج الأكثر مبيعاً هو "{top_product}".
        - **جودة البيانات:** قام الذكاء الاصطناعي بفحص العمليات ووجد ({anomalies_count}) عملية تبدو غير طبيعية (شاذة).
        - **التوصية:** يرجى مراجعة قسم "اكتشاف الأخطاء" للتأكد من سلامة العمليات الكبيرة.
        """
        return report

# ==========================================
# 4. الواجهة الجانبية (Sidebar)
# ==========================================
st.sidebar.title("📂 مركز البيانات")

# السماح برفع ملف جديد فقط إذا لم يتم التحليل أو إذا أراد المستخدم التغيير
uploaded_file = st.sidebar.file_uploader("1. ارفع ملف البيانات (Excel/CSV)", type=['xlsx', 'csv'])

if uploaded_file:
    # قراءة الملف مبدئياً لاستخراج الأعمدة
    try:
        if uploaded_file.name.endswith('.csv'):
            raw_df = pd.read_csv(uploaded_file)
        else:
            raw_df = pd.read_excel(uploaded_file)
        
        st.sidebar.success("تم قراءة الملف!")
        
        # واجهة اختيار الأعمدة (Mapping)
        st.sidebar.markdown("### 2. حدد الأعمدة")
        cols = raw_df.columns.tolist()
        
        col_date = st.sidebar.selectbox("عمود التاريخ", cols, index=0)
        col_customer = st.sidebar.selectbox("عمود العميل", cols, index=min(1, len(cols)-1))
        col_product = st.sidebar.selectbox("عمود المنتج", cols, index=min(2, len(cols)-1))
        col_sales = st.sidebar.selectbox("عمود المبيعات", cols, index=min(3, len(cols)-1))
        col_profit = st.sidebar.selectbox("عمود الأرباح (اختياري)", ["لا يوجد"] + cols)

        # زر البدء والحفظ في Session State
        if st.sidebar.button("🚀 بدء التحليل الذكي"):
            # تجهيز البيانات
            df_clean = raw_df.copy()
            rename_map = {
                col_date: 'Date',
                col_customer: 'Customer',
                col_product: 'Product',
                col_sales: 'Sales'
            }
            if col_profit != "لا يوجد":
                rename_map[col_profit] = 'Profit'
            
            df_clean.rename(columns=rename_map, inplace=True)
            
            # تنظيف الأنواع
            df_clean['Date'] = pd.to_datetime(df_clean['Date'], errors='coerce')
            df_clean['Sales'] = pd.to_numeric(df_clean['Sales'], errors='coerce')
            
            if 'Profit' not in df_clean.columns:
                df_clean['Profit'] = df_clean['Sales'] * 0.20 # تقدير ربح افتراضي
            else:
                df_clean['Profit'] = pd.to_numeric(df_clean['Profit'], errors='coerce')
            
            df_clean.dropna(subset=['Date', 'Sales'], inplace=True)
            
            # حفظ في الذاكرة الدائمة للجلسة
            st.session_state.data = df_clean
            st.session_state.analysis_done = True
            st.rerun() # إعادة تحميل الصفحة لتحديث الواجهة

    except Exception as e:
        st.sidebar.error(f"خطأ في الملف: {e}")

# زر مسح البيانات لبدء جديد
if st.session_state.analysis_done:
    if st.sidebar.button("🔄 إعادة ضبط النظام"):
        st.session_state.data = None
        st.session_state.analysis_done = False
        st.rerun()

# ==========================================
# 5. الواجهة الرئيسية (Main Dashboard)
# ==========================================
st.title("🤖 نظام المحلل المالي الذكي")
st.markdown("---")

# التحقق هل البيانات موجودة في الذاكرة أم لا
if st.session_state.analysis_done and st.session_state.data is not None:
    df = st.session_state.data
    ai_engine = AIEngine(df)
    
    # التبويبات الرئيسية
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 لوحة القيادة (Analytics)", 
        "🧠 الذكاء الاصطناعي (AI Core)", 
        "🚨 كشف الأخطاء (Errors)",
        "💬 المساعد الذكي (AI Chat)"
    ])

    # -------------------------------
    # Tab 1: التحليلات العامة
    # -------------------------------
    with tab1:
        # KPIs
        tot_sales = df['Sales'].sum()
        tot_profit = df['Profit'].sum()
        count = len(df)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("إجمالي المبيعات", f"${tot_sales:,.0f}")
        c2.metric("إجمالي الأرباح", f"${tot_profit:,.0f}")
        c3.metric("عدد العمليات", count)
        
        col_graph1, col_graph2 = st.columns(2)
        
        with col_graph1:
            st.subheader("📈 المبيعات عبر الزمن")
            daily_sales = df.groupby('Date')['Sales'].sum().reset_index()
            fig_line = px.line(daily_sales, x='Date', y='Sales', title='اتجاه المبيعات')
            st.plotly_chart(fig_line, use_container_width=True)
            
        with col_graph2:
            st.subheader("🏆 أفضل المنتجات")
            top_prod = df.groupby('Product')['Sales'].sum().nlargest(5).reset_index()
            fig_bar = px.bar(top_prod, x='Product', y='Sales', color='Sales', title='أعلى 5 منتجات مبيعاً')
            st.plotly_chart(fig_bar, use_container_width=True)

    # -------------------------------
    # Tab 2: الذكاء الاصطناعي (تصنيف العملاء)
    # -------------------------------
    with tab2:
        st.subheader("🧠 تقسيم العملاء الذكي (AI Segmentation)")
        st.info("يستخدم النظام خوارزمية K-Means لتقسيم العملاء بناءً على سلوكهم الشرائي.")
        
        segmented_df = ai_engine.segment_customers()
        
        if not segmented_df.empty:
            col_a, col_b = st.columns([2, 1])
            
            with col_a:
                fig_scatter = px.scatter(
                    segmented_df, x='Customer', y='Sales', 
                    color='Segment', size='Sales',
                    title="توزيع العملاء (الذهبي، الفضي، البرونزي)",
                    color_discrete_map={'عميل VIP (Gold)': 'gold', 'عميل مميز (Silver)': 'silver', 'عميل عادي (Bronze)': '#cd7f32'}
                )
                st.plotly_chart(fig_scatter, use_container_width=True)
            
            with col_b:
                st.write("📋 **قائمة كبار العملاء (VIP):**")
                vip_list = segmented_df[segmented_df['Segment'] == 'عميل VIP (Gold)'].sort_values('Sales', ascending=False).head(10)
                st.dataframe(vip_list[['Customer', 'Sales']])
        else:
            st.warning("البيانات غير كافية للتقسيم.")

    # -------------------------------
    # Tab 3: كشف الأخطاء
    # -------------------------------
    with tab3:
        st.subheader("🚨 كشف العمليات المشبوهة (Anomaly Detection)")
        st.write("يقوم الذكاء الاصطناعي بفحص كل عملية لتحديد ما إذا كانت الأرقام غير منطقية.")
        
        anomalies = ai_engine.detect_anomalies()
        
        if not anomalies.empty:
            st.error(f"تم اكتشاف {len(anomalies)} عملية شاذة قد تكون أخطاء أو احتيال.")
            st.dataframe(anomalies[['Date', 'Customer', 'Product', 'Sales', 'Profit']])
            
            fig_anom = px.scatter(df, x='Date', y='Sales', color=df['Is_Anomaly'].astype(str), 
                                title="توزيع العمليات الطبيعية (1) والشاذة (-1)",
                                color_discrete_map={'1': 'blue', '-1': 'red'})
            st.plotly_chart(fig_anom, use_container_width=True)
        else:
            st.success("✅ لم يكتشف النظام أي أخطاء واضحة.")

    # -------------------------------
    # Tab 4: الشات بوت (متصل بالبيانات)
    # -------------------------------
    with tab4:
        st.subheader("💬 المساعد التحليلي")
        
        # عرض سجل المحادثة
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # استقبال السؤال
        if prompt := st.chat_input("اطلب تقريراً، أو اسأل عن المبيعات، الأخطاء، أو أفضل منتج..."):
            # إضافة سؤال المستخدم
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # تحليل السؤال وتجهيز الرد
            response = ""
            q = prompt.lower()
            
            with st.chat_message("assistant"):
                with st.spinner("جاري تحليل البيانات..."):
                    if "تقرير" in q or "شامل" in q:
                        response = ai_engine.generate_report()
                    
                    elif "مبيعات" in q or "ايراد" in q:
                        response = f"💰 إجمالي المبيعات الحالية هو: **${df['Sales'].sum():,.2f}**"
                        
                    elif "خطأ" in q or "مشكلة" in q or "شاذ" in q:
                        anom_count = len(ai_engine.detect_anomalies())
                        if anom_count > 0:
                            response = f"🚨 نعم، وجدت **{anom_count}** عمليات شاذة. راجع تبويب 'كشف الأخطاء' للتفاصيل."
                        else:
                            response = "✅ البيانات نظيفة تماماً، لا توجد أخطاء واضحة."
                            
                    elif "عميل" in q or "vip" in q:
                        seg = ai_engine.segment_customers()
                        best_cust = seg.sort_values('Sales', ascending=False).iloc[0]['Customer']
                        response = f"👑 أفضل عميل لديك هو **{best_cust}**. يمكنك رؤية التصنيف الكامل في تبويب الذكاء الاصطناعي."
                        
                    elif "منتج" in q:
                        best_prod = df.groupby('Product')['Sales'].sum().idxmax()
                        response = f"🏆 المنتج الأكثر مبيعاً هو: **{best_prod}**."
                        
                    else:
                        response = "🤖 أنا مساعد ذكي مرتبط ببياناتك. يمكنك سؤالي عن: 'تقرير شامل'، 'المبيعات'، 'الأخطاء'، أو 'أفضل العملاء'."
                
                st.markdown(response)
                st.session_state.chat_history.append({"role": "assistant", "content": response})

else:
    # رسالة ترحيبية في حالة عدم وجود بيانات
    st.info("👋 مرحباً! يرجى البدء برفع ملف البيانات من القائمة الجانبية وتحديد الأعمدة، ثم الضغط على 'بدء التحليل الذكي'.")
    
    # عرض توضيحي (Demo Visuals) عشان الصفحة متبقاش فاضية
    st.markdown("### مميزات النظام:")
    col_d1, col_d2, col_d3 = st.columns(3)
    col_d1.success("🧠 **ذكاء اصطناعي (Clustering)** لتصنيف العملاء")
    col_d2.error("🚨 **كشف احتيال (Isolation Forest)** للأخطاء")
    col_d3.info("💬 **شات بوت (Chatbot)** يكتب تقارير كاملة")
