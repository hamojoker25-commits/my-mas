import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from thefuzz import process, fuzz
import re
import warnings

warnings.filterwarnings('ignore')

# ==========================================
# 1. إعدادات الصفحة والتصميم (المصمم MOHAMED)
# ==========================================
st.set_page_config(
    page_title="المصمم MOHAMED", 
    layout="wide", 
    page_icon="👑"
)

st.markdown("""
<style>
    /* تخصيص شكل الشات */
    .stChatMessage {
        padding: 1.5rem; 
        border-radius: 15px; 
        margin-bottom: 1rem; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.1);
    }
    .stChatInput {position: fixed; bottom: 20px; z-index: 1000;}
    .block-container {padding-bottom: 150px;}
    
    /* تخصيص العنوان */
    h1 {
        background: linear-gradient(to right, #1FA2FF, #12D8FA, #A6FFCB);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. العقل المدبر (Maestro Brain)
# ==========================================
class MaestroBrain:
    def __init__(self, df):
        self.df = df.copy()
        # تنظيف أسماء الأعمدة
        self.df.columns = [str(c).strip() for c in self.df.columns]
        
        # قاموس المفاهيم
        self.concepts = {
            'money': ['sales', 'price', 'amount', 'total', 'revenue', 'cost', 'profit', 'salary', 'مبيعات', 'سعر', 'اجمالي', 'مبلغ', 'ربح', 'تكلفة', 'راتب', 'قيمة'],
            'product': ['product', 'item', 'sku', 'model', 'name', 'desc', 'منتج', 'صنف', 'نوع', 'اسم', 'موديل', 'سلعة'],
            'customer': ['cust', 'client', 'buyer', 'consumer', 'عميل', 'زبون', 'مشتري'],
            'date': ['date', 'time', 'day', 'month', 'year', 'تاريخ', 'وقت', 'يوم', 'شهر', 'سنة'],
            'location': ['city', 'branch', 'region', 'country', 'مدينة', 'فرع', 'منطقة', 'دولة', 'محافظة']
        }
        
        self.roles = self._diagnose_columns()
        self.search_index = self._build_search_index()

    def _diagnose_columns(self):
        roles = {'numeric': [], 'date': None, 'text_cols': [], 'best_name': None}
        
        for col in self.df.columns:
            c_lower = col.lower()
            
            # 1. التاريخ
            if not roles['date']:
                if pd.api.types.is_datetime64_any_dtype(self.df[col]) or any(x in c_lower for x in self.concepts['date']):
                    try:
                        self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
                        roles['date'] = col
                        continue
                    except: pass

            # 2. الأرقام
            if pd.api.types.is_numeric_dtype(self.df[col]):
                if 'id' not in c_lower and 'code' not in c_lower:
                    roles['numeric'].append(col)
                continue
            
            # 3. النصوص
            roles['text_cols'].append(col)

        # ترتيب الأرقام (الأهمية للمال)
        roles['numeric'].sort(key=lambda x: 2 if any(k in x.lower() for k in self.concepts['money']) else 1, reverse=True)
        
        # تحديد أفضل اسم (منتج/عميل)
        for col in roles['text_cols']:
            if any(x in col.lower() for x in self.concepts['product'] + self.concepts['customer']):
                roles['best_name'] = col
                break
        
        if not roles['best_name'] and roles['text_cols']:
             roles['best_name'] = roles['text_cols'][0]

        return roles

    def _build_search_index(self):
        index = {}
        for col in self.roles['text_cols']:
            vals = self.df[col].dropna().astype(str).unique()
            for v in vals:
                index[v.lower().strip()] = col
        return index

    def think_and_answer(self, query):
        q = query.lower()
        
        # 1. النية
        intent = {
            'op': 'sum', 
            'target': self.roles['numeric'][0] if self.roles['numeric'] else None, 
            'group': self.roles['best_name'],
            'filters': {}
        }

        if any(x in q for x in ['اكثر', 'اعلى', 'اكبر', 'افضل', 'top', 'max']): intent['op'] = 'top'
        elif any(x in q for x in ['اقل', 'ادنى', 'اصغر', 'min', 'worst']): intent['op'] = 'bottom'
        elif any(x in q for x in ['متوسط', 'معدل', 'avg']): intent['op'] = 'mean'
        elif any(x in q for x in ['تطور', 'زمن', 'trend']): intent['op'] = 'trend'
        elif any(x in q for x in ['عدد', 'count']): intent['op'] = 'count'

        # تحديد الهدف الرقمي
        for col in self.roles['numeric']:
            if fuzz.partial_ratio(col.lower(), q) > 85:
                intent['target'] = col
                break

        # تحديد الفلاتر
        words = q.split()
        for w in words:
            if len(w) < 2: continue
            match = process.extractOne(w, self.search_index.keys(), scorer=fuzz.ratio)
            if match and match[1] >= 90:
                col_found = self.search_index[match[0]]
                original_val = self.df[self.df[col_found].astype(str).str.lower().str.strip() == match[0]].iloc[0][col_found]
                intent['filters'][col_found] = original_val

        # 2. التنفيذ
        df_wk = self.df.copy()
        filter_msg = ""
        for col, val in intent['filters'].items():
            df_wk = df_wk[df_wk[col] == val]
            filter_msg += f" (لـ {val})"
            
        target = intent['target']
        group = intent['group']

        if intent['op'] in ['top', 'bottom']:
            if not group or not target: return "محتاج عمود أسماء وأرقام.", None
            grouped = df_wk.groupby(group)[target].sum().reset_index()
            asc = (intent['op'] == 'bottom')
            grouped = grouped.sort_values(target, ascending=asc)
            
            top_item = grouped.iloc[0]
            name = top_item[group]
            val = top_item[target]
            
            emoji = "🏆" if not asc else "📉"
            msg = f"### {emoji} النتيجة {filter_msg}:\nالـ **{name}** هو الأول بقيمة `{val:,.2f}`"
            fig = px.bar(grouped.head(10), x=group, y=target, title=f"الترتيب حسب {target}", color=target)
            return msg, fig

        elif intent['op'] == 'trend':
            date_col = self.roles['date']
            if not date_col: return "مفيش عمود تاريخ للأسف.", None
            trend = df_wk.set_index(date_col).resample('M')[target].sum().reset_index()
            msg = f"### 📈 التحليل الزمني لـ {target}"
            fig = px.line(trend, x=date_col, y=target, markers=True)
            return msg, fig

        else:
            if not target and intent['op'] != 'count': return "مش لاقي عمود أرقام.", None
            
            val = 0
            title = ""
            if intent['op'] == 'mean':
                val = df_wk[target].mean()
                title = "المتوسط"
            elif intent['op'] == 'count':
                val = len(df_wk)
                title = "العدد"
                return f"### 🔢 عدد السجلات {filter_msg}: `{val}`", None
            else:
                val = df_wk[target].sum()
                title = "الإجمالي"
            
            msg = f"### 💰 {title} {target} {filter_msg}\n# `{val:,.2f}`"
            return msg, None

# ==========================================
# 3. واجهة التطبيق (المصمم MOHAMED)
# ==========================================
st.title("المصمم MOHAMED 🧠")
st.caption("أقوى نظام تحليل بيانات بالذكاء الاصطناعي")

# Sidebar
with st.sidebar:
    st.header("📂 ملف البيانات")
    uploaded_file = st.file_uploader("ارفع الملف (Excel/CSV)", type=['xlsx', 'csv'])
    
    if uploaded_file:
        try:
            df = None
            # 1. قراءة Excel
            if uploaded_file.name.endswith('.xlsx'):
                df = pd.read_excel(uploaded_file)
            
            # 2. قراءة CSV (حل مشكلة الخطأ نهائياً)
            elif uploaded_file.name.endswith('.csv'):
                encodings = ['utf-8', 'utf-8-sig', 'cp1256', 'latin1']
                for enc in encodings:
                    try:
                        uploaded_file.seek(0)
                        df = pd.read_csv(uploaded_file, encoding=enc)
                        break
                    except: continue
            
            if df is not None:
                # تشغيل المايسترو
                if 'maestro' not in st.session_state or st.session_state.last_file != uploaded_file.name:
                    st.session_state.maestro = MaestroBrain(df)
                    st.session_state.last_file = uploaded_file.name
                    st.session_state.messages = [{"role": "assistant", "content": "أهلاً يا هندسة 👋\nالملف تمام والذكاء الاصطناعي جاهز.\nاسألني أي سؤال (مثلاً: هات مبيعات القاهرة، أو أفضل منتج)."}]
                    st.rerun()
            else:
                st.error("مش عارف أقرأ الملف، تأكد إنه سليم.")
                
        except Exception as e:
            st.error(f"خطأ: {e}")

    if st.button("مسح الشات 🗑️"):
        st.session_state.messages = []
        st.rerun()

# Chat UI
if 'messages' not in st.session_state: st.session_state.messages = []
if 'maestro' not in st.session_state: st.session_state.maestro = None

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "chart" in msg and msg["chart"]:
            st.plotly_chart(msg["chart"], use_container_width=True)

if prompt := st.chat_input("اكتب سؤالك هنا..."):
    if st.session_state.maestro:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("جاري التفكير..."):
                response, fig = st.session_state.maestro.think_and_answer(prompt)
                st.markdown(response)
                if fig: st.plotly_chart(fig, use_container_width=True)
                
                st.session_state.messages.append({"role": "assistant", "content": response, "chart": fig})
    else:
        st.info("👈 ارفع الملف الأول يا ريس.")
