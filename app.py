import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import IsolationForest
from dateutil import parser
import re
import warnings

# تجاهل التحذيرات لضمان نظافة الواجهة
warnings.filterwarnings('ignore')

# ==========================================
# 1. إعدادات الصفحة الاحترافية
# ==========================================
st.set_page_config(
    page_title="Enterprise AI Analyst",
    layout="wide",
    page_icon="🏢",
    initial_sidebar_state="expanded"
)

# CSS لتحسين شكل الشات ليكون احترافياً
st.markdown("""
<style>
    .stChatMessage {border-radius: 10px; padding: 10px;}
    .stChatInput {position: fixed; bottom: 20px;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. المحرك الإدراكي (Cognitive Engine)
# ==========================================
class AutoIdentifier:
    """
    يقوم هذا الكلاس بقراءة الملف وتحديد نوع كل عمود تلقائياً
    بناءً على الاسم والمحتوى (عربي/إنجليزي)
    """
    def __init__(self, df):
        self.df = df
        self.column_roles = {}
        self._detect_roles()

    def _detect_roles(self):
        """خوارزمية تحديد الأدوار"""
        cols = self.df.columns
        
        # قواميس الكلمات المفتاحية (عربي وإنجليزي)
        keywords = {
            'date': ['date', 'time', 'تاريخ', 'وقت', 'زمن', 'يوم', 'شهر', 'day', 'month', 'year'],
            'money': ['price', 'sales', 'amount', 'total', 'salary', 'revenue', 'profit', 'cost', 'balance', 
                      'سعر', 'مبيعات', 'مبلغ', 'اجمالي', 'راتب', 'ربح', 'تكلفة', 'رصيد', 'قيمة', 'دخل'],
            'quantity': ['qty', 'quantity', 'stock', 'count', 'inventory', 'units', 
                         'كمية', 'عدد', 'مخزون', 'وحدات'],
            'category': ['category', 'product', 'item', 'name', 'customer', 'employee', 'branch', 'region', 'status', 
                         'فئة', 'منتج', 'صنف', 'اسم', 'عميل', 'موظف', 'فرع', 'منطقة', 'حالة', 'قسم']
        }

        self.column_roles = {
            'date_col': None,
            'target_col': None,  # الهدف الرقمي الرئيسي (مبيعات/راتب)
            'cat_cols': []       # أعمدة التصنيف
        }

        # 1. البحث عن التاريخ
        for col in cols:
            col_lower = str(col).lower()
            if any(k in col_lower for k in keywords['date']) or pd.api.types.is_datetime64_any_dtype(self.df[col]):
                self.column_roles['date_col'] = col
                # محاولة تحويله لتاريخ فعلي لضمان الدقة
                try:
                    self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
                except: pass
                break # نكتفي بأول عمود تاريخ نجده

        # 2. البحث عن الأهداف الرقمية (Target)
        potential_targets = []
        for col in cols:
            col_lower = str(col).lower()
            # إذا كان العمود رقمياً
            if pd.api.types.is_numeric_dtype(self.df[col]):
                # نرى هل اسمه يدل على مال أو كمية
                score = 0
                if any(k in col_lower for k in keywords['money']): score += 2
                if any(k in col_lower for k in keywords['quantity']): score += 1
                potential_targets.append((col, score))
        
        # ترتيب المرشحين واختيار الأقوى
        if potential_targets:
            potential_targets.sort(key=lambda x: x[1], reverse=True)
            self.column_roles['target_col'] = potential_targets[0][0]

        # 3. البحث عن التصنيفات (Categories)
        for col in cols:
            if col == self.column_roles['date_col'] or col == self.column_roles['target_col']:
                continue
            # إذا كان نصياً وعدد القيم الفريدة معقول (أقل من 500) نعتبره تصنيف
            if self.df[col].dtype == 'object' or pd.api.types.is_string_dtype(self.df[col]):
                if self.df[col].nunique() < 1000: 
                    self.column_roles['cat_cols'].append(col)

# ==========================================
# 3. العقل المحلل (Analytical Brain)
# ==========================================
class EnterpriseAI:
    def __init__(self, df, roles):
        self.df = df
        self.roles = roles
        self.date_col = roles['date_col']
        self.target = roles['target_col']
        self.cats = roles['cat_cols']

    def detect_anomalies(self):
        """كشف الأخطاء المؤسسية"""
        if not self.target: return pd.DataFrame()
        
        model = IsolationForest(contamination=0.02, random_state=42)
        data = self.df[[self.target]].fillna(0)
        preds = model.fit_predict(data)
        return self.df[preds == -1]

    def find_smart_filter(self, query):
        """البحث الدلالي داخل البيانات"""
        query_words = query.lower().split()
        filtered_df = self.df.copy()
        applied_filters = []

        # البحث في كل أعمدة التصنيف
        for col in self.cats:
            for word in query_words:
                clean_word = re.sub(r'[^\w\s]', '', word)
                if len(clean_word) < 2: continue
                
                # هل الكلمة موجودة كقيمة في هذا العمود؟
                mask = self.df[col].astype(str).str.contains(clean_word, case=False, na=False)
                if mask.any():
                    # تأكد أن الكلمة ليست مجرد حرف جر
                    if clean_word not in ['من', 'في', 'على', 'the', 'in', 'at']:
                        filtered_df = filtered_df[mask]
                        applied_filters.append(f"{col}={clean_word}")

        return filtered_df, applied_filters

    def process_query(self, query):
        """معالجة اللغة الطبيعية وفهم النية"""
        df_filtered, filters = self.find_smart_filter(query)
        response = ""
        chart = None
        
        # تحديد سياق الحديث (عن من نتحدث؟)
        context_msg = f" (بناءً على فلتر: {' + '.join(filters)})" if filters else " (على كامل البيانات)"
        
        if not self.target:
            return "عذراً، لم أستطع تحديد عمود رقمي رئيسي (مثل المبيعات أو الرواتب) في الملف تلقائياً. تأكد من صحة الملف.", None

        # 1. تحليل النية: المجموع والإجمالي
        if any(x in query for x in ['اجمالي', 'مجموع', 'total', 'sum', 'حجم', 'قيمة']):
            val = df_filtered[self.target].sum()
            response = f"💰 **إجمالي {self.target}** {context_msg}:\n# {val:,.2f}"
            
        # 2. تحليل النية: المتوسط
        elif any(x in query for x in ['متوسط', 'معدل', 'avg', 'average']):
            val = df_filtered[self.target].mean()
            response = f"📊 **متوسط {self.target}** {context_msg}:\n# {val:,.2f}"

        # 3. تحليل النية: الأفضل/الأعلى
        elif any(x in query for x in ['افضل', 'اعلى', 'اكثر', 'top', 'best', 'highest', 'max']):
            # نبحث عن أفضل تصنيف
            best_col = self.cats[0] if self.cats else None
            if best_col:
                grouped = df_filtered.groupby(best_col)[self.target].sum().sort_values(ascending=False).head(5)
                response = f"🏆 **الأعلى أداءً في {best_col}**:\n"
                chart = px.bar(grouped, x=grouped.index, y=self.target, title=f"Top 5 {best_col}", color=self.target)
            else:
                val = df_filtered[self.target].max()
                response = f"🚀 **أعلى قيمة مسجلة** هي: {val:,.2f}"

        # 4. تحليل النية: التطور الزمني
        elif any(x in query for x in ['تطور', 'زمن', 'تاريخ', 'trend', 'time', 'date', 'متى']) and self.date_col:
            # التجميع حسب الشهر أو اليوم
            df_filtered['Period'] = df_filtered[self.date_col].dt.to_period('M').astype(str)
            trend = df_filtered.groupby('Period')[self.target].sum().reset_index()
            response = f"📈 **التحليل الزمني لـ {self.target}**:"
            chart = px.line(trend, x='Period', y=self.target, markers=True, title="Growth Over Time")

        # 5. تحليل النية: الأخطاء/الشواذ
        elif any(x in query for x in ['خطأ', 'مشكلة', 'شاذ', 'anomaly', 'error', 'weird']):
            anomalies = self.detect_anomalies()
            count = len(anomalies)
            if count > 0:
                response = f"🚨 **تقرير التدقيق الذكي:**\nتم اكتشاف **{count}** عمليات تحتوي على أرقام غير منطقية في عمود {self.target}.\nهذه عينة منها:"
                chart = go.Figure(data=[go.Table(
                    header=dict(values=list(anomalies.columns), fill_color='paleturquoise', align='left'),
                    cells=dict(values=[anomalies[k].tolist() for k in anomalies.columns], align='left'))
                ])
            else:
                response = "✅ قمت بعمل مسح كامل للبيانات ولم أجد أي قيم شاذة إحصائياً."

        # 6. تقرير عام (الوضع الافتراضي)
        else:
            total = df_filtered[self.target].sum()
            count = len(df_filtered)
            response = f"""
            🤖 **تحليل فوري {context_msg}:**
            - **الهدف المحلل:** {self.target}
            - **عدد السجلات:** {count}
            - **الإجمالي:** {total:,.2f}
            
            💡 *أنا تعرفت على الأعمدة تلقائياً. يمكنك سؤالي عن: "تطور المبيعات"، "أفضل موظف"، "هل توجد أخطاء".*
            """
            
        return response, chart

# ==========================================
# 4. واجهة المستخدم (UI)
# ==========================================

# إدارة الحالة (Session State)
if 'df' not in st.session_state: st.session_state.df = None
if 'ai_brain' not in st.session_state: st.session_state.ai_brain = None
if 'messages' not in st.session_state: st.session_state.messages = []

# العنوان
st.title("🤖 Enterprise Data AI")
st.markdown("#### نظام تحليل بيانات الشركات الذكي (Auto-Detect Mode)")

# الشريط الجانبي للرفع فقط
with st.sidebar:
    st.header("📂 مركز البيانات")
    uploaded_file = st.file_uploader("ارفع الملف واترك الباقي علي (Excel/CSV)", type=['xlsx', 'csv'])
    
    if uploaded_file and st.session_state.df is None:
        try:
            # قراءة الملف
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            # 1. تشغيل المصنف التلقائي
            identifier = AutoIdentifier(df)
            roles = identifier.column_roles
            
            # حفظ في الذاكرة
            st.session_state.df = df
            st.session_state.ai_brain = EnterpriseAI(df, roles)
            
            # رسالة ترحيب ذكية
            detected_msg = f"""
            **تم تحليل هيكل الملف بنجاح! 🧠**
            - العمود الرقمي الرئيسي: `{roles['target_col']}`
            - عمود التاريخ: `{roles['date_col'] if roles['date_col'] else 'غير موجود'}`
            - عدد أعمدة التصنيف: {len(roles['cat_cols'])}
            """
            st.session_state.messages.append({"role": "assistant", "content": f"أهلاً بك! {detected_msg}\nأنا جاهز للأسئلة."})
            st.rerun()
            
        except Exception as e:
            st.error(f"حدث خطأ في الملف: {e}")

    if st.button("🔄 تصفير المحادثة"):
        st.session_state.df = None
        st.session_state.ai_brain = None
        st.session_state.messages = []
        st.rerun()

# منطقة الشات
if st.session_state.df is not None:
    # عرض الرسائل السابقة
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "chart" in msg:
                st.plotly_chart(msg["chart"], use_container_width=True)

    # استقبال السؤال
    if prompt := st.chat_input("اسألني عن المبيعات، الموظفين، المخزون، الأخطاء..."):
        # عرض سؤال المستخدم
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # معالجة الرد
        with st.chat_message("assistant"):
            with st.spinner("جاري تحليل البيانات المؤسسية..."):
                brain = st.session_state.ai_brain
                response_text, chart = brain.process_query(prompt)
                
                st.markdown(response_text)
                if chart:
                    st.plotly_chart(chart, use_container_width=True)
                
                # حفظ الرد
                msg_data = {"role": "assistant", "content": response_text}
                if chart: msg_data["chart"] = chart
                st.session_state.messages.append(msg_data)

else:
    # شاشة الترحيب عند فتح الموقع
    st.info("👋 مرحباً! هذا النظام مصمم للشركات. فقط ارفع ملف (مبيعات، مخزون، HR) وسأقوم بفهمه وتجهيز الردود تلقائياً.")
    st.markdown("""
    ### 🚀 قدرات النظام:
    - **Auto-Detect:** يكتشف الأعمدة العربية والإنجليزية تلقائياً.
    - **Anomaly Detection:** يكشف الاحتيال والأخطاء.
    - **Deep Context:** يفهم الفلاتر (مثلاً: "مبيعات قسم الصيانة").
    """)
