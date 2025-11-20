import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import IsolationForest
import re
import warnings

# تجاهل التحذيرات لضمان نظافة الواجهة
warnings.filterwarnings('ignore')

# ==========================================
# 1. إعدادات الصفحة وتصميم الواجهة (UI/UX)
# ==========================================
st.set_page_config(
    page_title="Enterprise AI Analyst",
    layout="wide",
    page_icon="🧠",
    initial_sidebar_state="expanded"
)

# تحسين مظهر الشات باستخدام CSS
st.markdown("""
<style>
    .stChatInput {
        position: fixed;
        bottom: 20px;
        z-index: 1000;
    }
    .block-container {
        padding-bottom: 100px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. المحرك الإدراكي (Auto-Detection Engine)
# ==========================================
class AutoIdentifier:
    def __init__(self, df):
        self.df = df.copy()
        self.roles = {
            'date_col': None,
            'target_col': None,
            'cat_cols': []
        }
        self._detect_roles()

    def _detect_roles(self):
        # 1. تنظيف أسماء الأعمدة
        self.df.columns = [str(c).strip() for c in self.df.columns]
        cols = self.df.columns
        
        # القواميس (عربي/إنجليزي)
        keywords = {
            'date': ['date', 'time', 'تاريخ', 'وقت', 'زمن', 'يوم', 'شهر'],
            'money_qty': ['price', 'sales', 'amount', 'total', 'salary', 'revenue', 'profit', 'cost', 'qty', 'stock', 
                          'سعر', 'مبيعات', 'مبلغ', 'اجمالي', 'راتب', 'ربح', 'تكلفة', 'رصيد', 'قيمة', 'كمية', 'مخزون', 'عدد']
        }

        # A. البحث عن التاريخ
        for col in cols:
            # لو العمود أصلاً نوعه تاريخ
            if pd.api.types.is_datetime64_any_dtype(self.df[col]):
                self.roles['date_col'] = col
                break
            # لو الاسم يوحي بتاريخ، نحاول نحوله
            if any(k in col.lower() for k in keywords['date']):
                try:
                    self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
                    # نتأكد إنه اتحول فعلاً
                    if pd.api.types.is_datetime64_any_dtype(self.df[col]):
                        self.roles['date_col'] = col
                        break
                except: pass

        # B. البحث عن الهدف الرقمي (Target)
        potential_targets = []
        for col in cols:
            # لازم يكون رقمي
            if pd.api.types.is_numeric_dtype(self.df[col]):
                score = 0
                if any(k in col.lower() for k in keywords['money_qty']): score += 2
                # نفضل العمود اللي فيه قيم فريدة كتير (عشان مش يكون ID أو كود)
                if self.df[col].nunique() > 5: score += 1
                potential_targets.append((col, score))
        
        if potential_targets:
            # نختار صاحب أعلى سكور
            potential_targets.sort(key=lambda x: x[1], reverse=True)
            self.roles['target_col'] = potential_targets[0][0]

        # C. البحث عن التصنيفات (Categories)
        for col in cols:
            if col == self.roles['date_col'] or col == self.roles['target_col']:
                continue
            # نعتبره تصنيف لو هو نصي وعدد قيمه معقول
            if self.df[col].dtype == 'object' or pd.api.types.is_string_dtype(self.df[col]):
                if self.df[col].nunique() < 2000: # رقم تقديري
                    self.roles['cat_cols'].append(col)

# ==========================================
# 3. المحلل الذكي (Analytical Brain)
# ==========================================
class SmartAnalyst:
    def __init__(self, df, roles):
        self.df = df
        self.roles = roles
        self.target = roles['target_col']
        self.date_col = roles['date_col']
        self.cats = roles['cat_cols']

    def process_query(self, query):
        # إذا لم يتم تحديد عمود رقمي، لا يمكن التحليل
        if not self.target:
            return "⚠️ عذراً، لم أستطع تحديد عمود للأرقام (مبيعات/رواتب/كميات) تلقائياً. يرجى التأكد من الملف.", None

        query = query.lower()
        filtered_df = self.df.copy()
        filters_applied = []

        # 1. البحث والفلترة الذكية
        for cat in self.cats:
            # البحث عن قيم العمود داخل سؤال المستخدم
            unique_vals = self.df[cat].dropna().unique()
            for val in unique_vals:
                val_str = str(val).lower()
                # تنظيف القيمة للبحث
                if len(val_str) > 1 and val_str in query:
                    mask = filtered_df[cat].astype(str).str.contains(val_str, case=False, na=False)
                    if mask.any():
                        filtered_df = filtered_df[mask]
                        filters_applied.append(f"{val}")
                        break # نكتفي بقيمة واحدة من نفس العمود لمنع التضارب

        context = f" (في: {' + '.join(filters_applied)})" if filters_applied else " (الإجمالي)"
        
        # 2. فهم نوع السؤال (Intent)

        # --- المجموع / الإجمالي ---
        if any(x in query for x in ['اجمالي', 'مجموع', 'total', 'sum', 'كم']):
            val = filtered_df[self.target].sum()
            return f"💰 **إجمالي {self.target}** {context}:\n# {val:,.2f}", None

        # --- المتوسط ---
        elif any(x in query for x in ['متوسط', 'معدل', 'avg', 'average']):
            val = filtered_df[self.target].mean()
            return f"📊 **متوسط {self.target}** {context}:\n# {val:,.2f}", None

        # --- الأفضل / الأعلى ---
        elif any(x in query for x in ['افضل', 'اعلى', 'اكثر', 'top', 'best', 'max']):
            if self.cats:
                # نختار أول عمود تصنيف مناسب (أو العمود اللي تم الفلترة عليه لو مفيش غيره)
                group_col = self.cats[0]
                # لو المستخدم سأل عن تصنيف محدد (مثلاً "أفضل موظف") نحاول نلاقيه
                for c in self.cats:
                    if c.lower() in query:
                        group_col = c
                        break
                
                top = filtered_df.groupby(group_col)[self.target].sum().sort_values(ascending=False).head(5)
                fig = px.bar(top, x=top.index, y=self.target, title=f"Top 5 - {group_col}", color=self.target)
                return f"🏆 **الأعلى أداءً** {context}:", fig
            else:
                val = filtered_df[self.target].max()
                return f"🚀 **أعلى رقم مسجل:** {val:,.2f}", None

        # --- التطور الزمني (Time Series) ---
        elif any(x in query for x in ['تطور', 'زمن', 'تاريخ', 'trend', 'time', 'date']) and self.date_col:
            # التأكد أن التواريخ مرتبة
            trend = filtered_df.sort_values(self.date_col)
            fig = px.line(trend, x=self.date_col, y=self.target, title=f"{self.target} Trend")
            return f"📈 **التحليل الزمني** {context}:", fig

        # --- الأخطاء / الشواذ (Anomaly) ---
        elif any(x in query for x in ['خطأ', 'مشكلة', 'شاذ', 'anomaly', 'error']):
            model = IsolationForest(contamination=0.01, random_state=42)
            data_fit = self.df[[self.target]].fillna(0) # نستخدم الداتا الأصلية للكشف الأدق
            preds = model.fit_predict(data_fit)
            anomalies = self.df[preds == -1]
            
            if not anomalies.empty:
                fig = go.Figure(data=[go.Table(
                    header=dict(values=list(anomalies.columns), fill_color='red', font=dict(color='white')),
                    cells=dict(values=[anomalies[k].tolist() for k in anomalies.columns])
                )])
                return f"🚨 **كشف الأخطاء:** وجدت {len(anomalies)} عمليات غير منطقية (شاذة إحصائياً):", fig
            else:
                return "✅ البيانات سليمة تماماً، لم أجد أي قيم شاذة.", None

        # --- تقرير عام ---
        else:
            val = filtered_df[self.target].sum()
            count = len(filtered_df)
            msg = f"""
            🤖 **تحليل سريع {context}:**
            - **الهدف:** {self.target}
            - **عدد العمليات:** {count}
            - **الإجمالي:** {val:,.2f}
            
            💡 *اسألني: "أفضل منتج"، "تطور المبيعات"، "هل توجد أخطاء؟"*
            """
            return msg, None

# ==========================================
# 4. الواجهة الرئيسية (Main App Logic)
# ==========================================

# إدارة الذاكرة
if 'df' not in st.session_state: st.session_state.df = None
if 'analyst' not in st.session_state: st.session_state.analyst = None
if 'messages' not in st.session_state: 
    st.session_state.messages = [{"role": "assistant", "content": "مرحباً! 👋 ارفع ملف البيانات وسأقوم بتحليله فوراً."}]

st.title("🧠 Enterprise AI Analyst")

# --- Sidebar (File Upload) ---
with st.sidebar:
    st.header("📂 البيانات")
    uploaded_file = st.file_uploader("ارفع ملف (Excel/CSV)", type=['xlsx', 'csv'])
    
    if uploaded_file and st.session_state.df is None:
        try:
            # قراءة الملف
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            # التشغيل التلقائي (Auto-ML)
            identifier = AutoIdentifier(df)
            
            # حفظ النتائج
            st.session_state.df = identifier.df # الداتا بعد تنظيف التواريخ
            st.session_state.analyst = SmartAnalyst(st.session_state.df, identifier.roles)
            
            # رسالة ترحيب توضح ما تم اكتشافه
            roles = identifier.roles
            welcome_msg = f"""
            **✅ تم تحليل الملف بنجاح!**
            - العمود الرقمي (الهدف): `{roles['target_col']}`
            - عمود التاريخ: `{roles['date_col'] if roles['date_col'] else 'غير موجود'}`
            - أعمدة التصنيف: `{len(roles['cat_cols'])}` أعمدة.
            
            **أنا جاهز للأسئلة الآن!** 🚀
            """
            st.session_state.messages.append({"role": "assistant", "content": welcome_msg})
            st.rerun()
            
        except Exception as e:
            st.error(f"حدث خطأ في الملف: {e}")

    if st.button("🔄 بدء جديد"):
        st.session_state.df = None
        st.session_state.analyst = None
        st.session_state.messages = [{"role": "assistant", "content": "مرحباً! 👋 ارفع ملف البيانات وسأقوم بتحليله فوراً."}]
        st.rerun()

# --- Chat Interface ---

# عرض الرسائل
for msg in st.session_state.messages:
    # تحديد الأفاتار (شكل الايقونة)
    avatar = "🤖" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])
        # عرض الرسم البياني إن وجد
        if "chart" in msg and msg["chart"]:
            st.plotly_chart(msg["chart"], use_container_width=True)

# استقبال المدخلات
if prompt := st.chat_input("اسألني عن بياناتك..."):
    if st.session_state.analyst:
        # 1. عرض رسالة المستخدم
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        # 2. معالجة الرد
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("جاري التحليل..."):
                response_text, chart = st.session_state.analyst.process_query(prompt)
                
                st.markdown(response_text)
                if chart:
                    st.plotly_chart(chart, use_container_width=True)
                
                # حفظ الرد في الذاكرة
                st.session_state.messages.append({"role": "assistant", "content": response_text, "chart": chart})
    else:
        st.error("يرجى رفع ملف البيانات أولاً!")
