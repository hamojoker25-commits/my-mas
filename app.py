import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.ensemble import IsolationForest
from datetime import datetime
import re

# ==========================================
# 1. إعداد الصفحة (Page Config)
# ==========================================
st.set_page_config(
    page_title="المحلل الذكي الشامل (Super AI)",
    layout="wide",
    page_icon="🧠"
)

# ==========================================
# 2. محرك الذكاء الاصطناعي المنطقي (AI Logic Brain)
# ==========================================
class SmartDataAgent:
    def __init__(self, df, col_config):
        self.df = df
        self.cfg = col_config
        # تحويل كل النصوص لأحرف صغيرة لتسهيل البحث
        self.df_searchable = df.astype(str).apply(lambda x: x.str.lower())

    def find_filter_in_query(self, query):
        """
        هذه الدالة تبحث بذكاء عن أي كلمة في سؤال المستخدم 
        موجودة بالفعل داخل الداتا (مثل اسم موظف، اسم منتج)
        """
        query_words = query.lower().split()
        filters = {}
        
        # البحث في الأعمدة النصية عن قيم تطابق كلمات السؤال
        for col in self.df.select_dtypes(include=['object', 'string']).columns:
            for word in query_words:
                # تنظيف الكلمة
                clean_word = re.sub(r'[^\w\s]', '', word)
                if len(clean_word) < 2: continue
                
                # هل الكلمة موجودة في هذا العمود؟
                matches = self.df[self.df[col].astype(str).str.contains(clean_word, case=False, na=False)]
                if not matches.empty:
                    # تم العثور على فلتر محتمل
                    filters[col] = clean_word
        return filters

    def detect_anomalies(self):
        """كشف القيم الشاذة إحصائياً"""
        target_col = self.cfg.get('target')
        if not target_col: return None
        
        model = IsolationForest(contamination=0.02, random_state=42)
        data_to_fit = self.df[[target_col]].fillna(0)
        preds = model.fit_predict(data_to_fit)
        return self.df[preds == -1]

    def analyze_query(self, query):
        """
        المخ الرئيسي: يحلل السؤال ويقرر الإجابة والرسم البياني
        """
        query = query.lower()
        target_col = self.cfg.get('target') # العمود الرقمي (مبيعات/مخزون/راتب)
        cat_col = self.cfg.get('category')  # عمود التصنيف (منتج/موظف/فرع)
        date_col = self.cfg.get('date')     # عمود التاريخ
        
        response_text = ""
        chart = None
        
        # 1. البحث عن فلاتر (هل المستخدم يسأل عن شيء محدد؟)
        active_filters = self.find_filter_in_query(query)
        filtered_df = self.df.copy()
        filter_desc = ""
        
        for col, val in active_filters.items():
            filtered_df = filtered_df[filtered_df[col].astype(str).str.contains(val, case=False, na=False)]
            filter_desc += f" (الخاصة بـ {val})"

        # 2. تحليل النية (Intent Analysis)
        
        # --- كشف الأخطاء ---
        if any(w in query for w in ['خطأ', 'مشكلة', 'غريب', 'شاذ', 'anomalies', 'error']):
            anomalies = self.detect_anomalies()
            if anomalies is not None and not anomalies.empty:
                response_text = f"🚨 **تحذير ذكي:** قمت بفحص البيانات ووجدت {len(anomalies)} سجلات تحتوي على أرقام غير منطقية (شاذة إحصائياً) في عمود '{target_col}'.\n\nهذه عينة منها:"
                return response_text, anomalies.head()
            else:
                return "✅ قمت بفحص البيانات بخوارزميات الذكاء الاصطناعي ولم أجد أي قيم شاذة أو أخطاء واضحة.", None

        # --- المجموع والإجماليات ---
        if any(w in query for w in ['اجمالي', 'مجموع', 'total', 'sum', 'كم']):
            total = filtered_df[target_col].sum()
            response_text = f"💰 **الإجمالي{filter_desc}:**\n# {total:,.2f}"
            
        # --- المتوسط ---
        elif any(w in query for w in ['متوسط', 'معدل', 'average', 'avg']):
            avg = filtered_df[target_col].mean()
            response_text = f"📊 **المتوسط{filter_desc}:**\n# {avg:,.2f}"
            
        # --- الأفضل / الأعلى ---
        elif any(w in query for w in ['افضل', 'احسن', 'اعلى', 'اكثر', 'top', 'best', 'max']):
            if cat_col:
                best = filtered_df.groupby(cat_col)[target_col].sum().sort_values(ascending=False).head(5)
                response_text = f"🏆 **الأعلى أداءً{filter_desc}:**"
                # رسم بياني تلقائي
                chart = px.bar(best, x=best.index, y=target_col, title=f"الأفضل في {cat_col}", color=target_col)
            else:
                max_val = filtered_df[target_col].max()
                response_text = f"🚀 **أعلى قيمة مسجلة:** {max_val:,.2f}"

        # --- الأقل / الأسوأ ---
        elif any(w in query for w in ['اسوا', 'اقل', 'lowest', 'min']):
            if cat_col:
                worst = filtered_df.groupby(cat_col)[target_col].sum().sort_values().head(5)
                response_text = f"📉 **الأقل أداءً{filter_desc}:**"
                chart = px.bar(worst, x=worst.index, y=target_col, title=f"الأقل في {cat_col}", color_discrete_sequence=['red'])
            else:
                min_val = filtered_df[target_col].min()
                response_text = f"⬇️ **أقل قيمة مسجلة:** {min_val:,.2f}"
                
        # --- تحليل زمني (تريند) ---
        elif any(w in query for w in ['زمن', 'وقت', 'تطور', 'تاريخ', 'trend', 'time']) and date_col:
            trend = filtered_df.groupby(date_col)[target_col].sum().reset_index()
            response_text = f"📈 **التحليل الزمني{filter_desc}:** انظر للرسم البياني أدناه لتتبع التطور."
            chart = px.line(trend, x=date_col, y=target_col, title="تطور الأداء عبر الزمن")

        # --- توزيع / نسب ---
        elif any(w in query for w in ['توزيع', 'نسبة', 'pie', 'dist']):
            if cat_col:
                response_text = "بناءً على طلبك، هذا هو توزيع البيانات:"
                chart = px.pie(filtered_df, names=cat_col, values=target_col, title=f"توزيع {target_col} حسب {cat_col}")

        # --- سؤال عام أو تقرير ---
        else:
            # Default Report
            total = filtered_df[target_col].sum()
            count = len(filtered_df)
            response_text = f"""
            🤖 **تحليل سريع{filter_desc}:**
            - عدد السجلات التي تم تحليلها: {count}
            - الإجمالي: {total:,.2f}
            
            💡 *جرب أن تسألني عن: "أفضل منتج"، "المبيعات في القاهرة"، "هل هناك أخطاء"، "تطور المبيعات".*
            """

        return response_text, chart

# ==========================================
# 3. واجهة المستخدم (الذاكرة والرفع)
# ==========================================

# تهيئة الذاكرة (Session State)
if 'df' not in st.session_state: st.session_state.df = None
if 'chat_history' not in st.session_state: st.session_state.chat_history = []
if 'col_config' not in st.session_state: st.session_state.col_config = {}

# القائمة الجانبية: الإعداد لمرة واحدة فقط
st.sidebar.title("⚙️ إعدادات المحرك")
uploaded_file = st.sidebar.file_uploader("1. ارفع الملف (Excel/CSV)", type=['xlsx', 'csv', 'xls'])

if uploaded_file and st.session_state.df is None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.session_state.df = df
        st.sidebar.success("تم رفع الملف بنجاح!")
    except Exception as e:
        st.sidebar.error(f"خطأ: {e}")

# إعداد الأعمدة (Mapping)
if st.session_state.df is not None:
    df = st.session_state.df
    cols = df.columns.tolist()
    
    st.sidebar.markdown("### 2. عرفني على البيانات")
    st.sidebar.info("عشان الذكاء الاصطناعي يفهم ملفك، اختار الأعمدة دي:")
    
    target = st.sidebar.selectbox("العمود الرقمي (الهدف)", cols, help="المبيعات، المخزون، الراتب، العدد...")
    category = st.sidebar.selectbox("عمود التصنيف", ["لا يوجد"] + cols, help="المنتج، الموظف، الفرع، المنطقة...")
    date_col = st.sidebar.selectbox("عمود التاريخ (اختياري)", ["لا يوجد"] + cols)
    
    if st.sidebar.button("💾 حفظ الإعدادات وبدء الشات"):
        st.session_state.col_config = {
            'target': target,
            'category': category if category != "لا يوجد" else None,
            'date': date_col if date_col != "لا يوجد" else None
        }
        # تنظيف البيانات حسب الاختيار
        df[target] = pd.to_numeric(df[target], errors='coerce')
        if date_col != "لا يوجد":
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        
        st.session_state.df = df
        st.session_state.chat_history.append({"role": "assistant", "content": "أهلاً! أنا جاهز. البيانات معايا والإعدادات تمام. اسألني عن أي حاجة في ملفك! 🧠"})
        st.rerun()

# زر تصفير النظام
if st.sidebar.button("🔄 تصفير وبدء جديد"):
    st.session_state.clear()
    st.rerun()

# ==========================================
# 4. منطقة الشات (Main Chat Area)
# ==========================================
st.title("🧠 المحلل الذكي (Data AI)")

# إذا لم يتم رفع الملف
if st.session_state.df is None or not st.session_state.col_config:
    st.info("👈 من فضلك، ارفع الملف وحدد الأعمدة من القائمة الجانبية واضغط 'حفظ الإعدادات' لتبدأ المحادثة.")
else:
    # تهيئة الـ Agent
    agent = SmartDataAgent(st.session_state.df, st.session_state.col_config)

    # عرض الشات السابق
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            # إذا كان هناك رسم بياني محفوظ (هذا يتطلب منطقاً معقداً للحفظ، سنعرض النصوص فقط في السجل ونعيد توليد الرسم عند الطلب الجديد)
    
    # استقبال السؤال الجديد
    if user_input := st.chat_input("اسألني عن بياناتك..."):
        # 1. عرض سؤال المستخدم
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # 2. تفكير الذكاء الاصطناعي والرد
        with st.chat_message("assistant"):
            with st.spinner("جاري تحليل البيانات..."):
                response_text, chart_obj = agent.analyze_query(user_input)
                
                st.markdown(response_text)
                if chart_obj:
                    st.plotly_chart(chart_obj, use_container_width=True)
                
                # حفظ الرد (النص فقط) في السجل
                st.session_state.chat_history.append({"role": "assistant", "content": response_text})
