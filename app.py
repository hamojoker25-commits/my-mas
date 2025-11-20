import streamlit as st
import pandas as pd
import plotly.express as px
import warnings

warnings.filterwarnings('ignore')

# ==========================================
# 1. إعدادات الصفحة
# ==========================================
st.set_page_config(page_title="المحلل الذكي (النسخة النهائية)", layout="wide", page_icon="✅")

st.markdown("""
<style>
    .stChatInput {position: fixed; bottom: 20px; z-index: 1000;}
    .stChatMessage {padding: 1.5rem; border-radius: 15px; margin-bottom: 1rem; border: 1px solid #e0e0e0;}
    .block-container {padding-bottom: 150px;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. تهيئة الذاكرة (Session State)
# ==========================================
if 'brain' not in st.session_state: st.session_state.brain = None
if 'messages' not in st.session_state: st.session_state.messages = []
if 'pending_action' not in st.session_state: st.session_state.pending_action = None
if 'df' not in st.session_state: st.session_state.df = None # هنا الحل: بنخزن الداتا نفسها

# ==========================================
# 3. المخ (Logic Core)
# ==========================================
class InteractiveBrain:
    def __init__(self, df):
        self.df = df
        self.df.columns = [str(c).strip() for c in self.df.columns]
        self.cols = self.df.columns.tolist()

    def identify_requirements(self, query):
        q = query.lower()
        reqs = {'needs_numeric': False, 'needs_category': False, 'needs_date': False, 'operation': 'sum', 'title': ''}

        if any(x in q for x in ['اكثر', 'اعلى', 'اكبر', 'افضل', 'top', 'max', 'best']):
            reqs.update({'operation': 'top', 'needs_numeric': True, 'needs_category': True, 'title': 'الأكثر/الأعلى'})
        elif any(x in q for x in ['اقل', 'ادنى', 'اصغر', 'اسوا', 'min', 'worst']):
            reqs.update({'operation': 'bottom', 'needs_numeric': True, 'needs_category': True, 'title': 'الأقل/الأدنى'})
        elif any(x in q for x in ['متوسط', 'معدل', 'avg']):
            reqs.update({'operation': 'mean', 'needs_numeric': True, 'title': 'المتوسط'})
        elif any(x in q for x in ['تطور', 'زمن', 'trend']):
            reqs.update({'operation': 'trend', 'needs_numeric': True, 'needs_date': True, 'title': 'التحليل الزمني'})
        elif any(x in q for x in ['عدد', 'count']):
            reqs.update({'operation': 'count', 'title': 'عدد السجلات'})
        else:
            reqs.update({'operation': 'sum', 'needs_numeric': True, 'title': 'الإجمالي'})
        return reqs

    def calculate(self, reqs, selected_cols):
        df_calc = self.df.copy()
        op = reqs['operation']
        num_col = selected_cols.get('numeric')
        cat_col = selected_cols.get('category')
        date_col = selected_cols.get('date')

        if num_col: df_calc[num_col] = pd.to_numeric(df_calc[num_col], errors='coerce')

        if op == 'top':
            grouped = df_calc.groupby(cat_col)[num_col].sum().sort_values(ascending=False).head(5)
            best_name = grouped.index[0]
            best_val = grouped.iloc[0]
            msg = f"🏆 **{reqs['title']} في ({cat_col}) حسب ({num_col}):**\n# {best_name}\n**(القيمة: {best_val:,.2f})**"
            fig = px.bar(grouped, x=grouped.index, y=grouped.values, title=f"أعلى 5 {cat_col}", color=grouped.values)
            return msg, fig
        
        elif op == 'bottom':
            grouped = df_calc.groupby(cat_col)[num_col].sum().sort_values(ascending=True).head(5)
            worst_name = grouped.index[0]
            worst_val = grouped.iloc[0]
            msg = f"📉 **{reqs['title']} في ({cat_col}) حسب ({num_col}):**\n# {worst_name}\n**(القيمة: {worst_val:,.2f})**"
            fig = px.bar(grouped, x=grouped.index, y=grouped.values, title=f"أقل 5 {cat_col}")
            return msg, fig

        elif op == 'trend':
            df_calc[date_col] = pd.to_datetime(df_calc[date_col], errors='coerce')
            trend = df_calc.groupby(date_col)[num_col].sum().reset_index()
            msg = f"📈 **تطور {num_col} عبر الزمن:**"
            fig = px.line(trend, x=date_col, y=num_col, markers=True)
            return msg, fig

        elif op == 'sum':
            val = df_calc[num_col].sum()
            return f"💰 **إجمالي {num_col}:**\n# {val:,.2f}", None

        elif op == 'mean':
            val = df_calc[num_col].mean()
            return f"📊 **متوسط {num_col}:**\n# {val:,.2f}", None

        elif op == 'count':
            val = len(df_calc)
            return f"🔢 **عدد الصفوف في الملف:**\n# {val}", None
            
        return "خطأ غير متوقع", None

# ==========================================
# 4. واجهة المستخدم (حل مشكلة الرفع)
# ==========================================
st.title("🎯 المحلل الذكي (النسخة المستقرة)")

# Sidebar
with st.sidebar:
    st.header("1. رفع الملف")
    uploaded_file = st.file_uploader("Excel/CSV", type=['xlsx', 'csv'])
    
    # هنا الحل الجذري: لو الملف اترفع، بنحفظه وننساه
    if uploaded_file:
        if st.session_state.df is None: # لو لسه مقرناش الملف
            try:
                if uploaded_file.name.endswith('.xlsx'): df = pd.read_excel(uploaded_file)
                else:
                    # محاولات قراءة CSV
                    try: df = pd.read_csv(uploaded_file, encoding='utf-8')
                    except: df = pd.read_csv(uploaded_file, encoding='cp1256') # عربي
                
                st.session_state.df = df
                st.session_state.brain = InteractiveBrain(df)
                st.session_state.messages = [{"role": "assistant", "content": "✅ الملف وصل! أنا جاهز، اسألني أي سؤال."}]
                st.rerun()
                
            except Exception as e:
                st.error(f"خطأ في الملف: {e}")
    
    if st.session_state.df is not None:
        st.success("✅ الملف محفوظ وجاهز للتحليل")
        if st.button("رفع ملف جديد"):
            st.session_state.df = None
            st.session_state.brain = None
            st.session_state.messages = []
            st.rerun()

    if st.button("مسح المحادثة"):
        st.session_state.messages = []
        st.session_state.pending_action = None
        st.rerun()

# Chat Display
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "chart" in msg and msg["chart"]:
            st.plotly_chart(msg["chart"], use_container_width=True)

# Input Area - بيظهر فقط لو الملف مرفوع
if st.session_state.df is not None:
    if prompt := st.chat_input("اسألني... (مثلاً: أكثر عميل اشترى)"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()
else:
    st.info("👈 من فضلك ارفع ملف Excel أو CSV من القائمة الجانبية لتبدأ.")

# Logic Processing
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user" and not st.session_state.pending_action:
    last_query = st.session_state.messages[-1]["content"]
    brain = st.session_state.brain
    if brain:
        reqs = brain.identify_requirements(last_query)
        st.session_state.pending_action = reqs
        st.rerun()

# Action Area (Dropdowns)
if st.session_state.pending_action:
    reqs = st.session_state.pending_action
    cols = st.session_state.brain.cols
    
    with st.chat_message("assistant"):
        st.markdown(f"🛠️ **لتحديد ({reqs['title']}) بدقة، اختر الأعمدة:**")
        
        if reqs['operation'] == 'count':
            msg, fig = st.session_state.brain.calculate(reqs, {})
            st.session_state.messages.append({"role": "assistant", "content": msg})
            st.session_state.pending_action = None
            st.rerun()
        else:
            c1, c2 = st.columns(2)
            sel_cols = {}
            
            with c1:
                if reqs['needs_category']:
                    sel_cols['category'] = st.selectbox("عمود الأسماء (منتج/عميل):", cols, key="cat_s")
                if reqs['needs_date']:
                    sel_cols['date'] = st.selectbox("عمود التاريخ:", cols, key="date_s")
            with c2:
                if reqs['needs_numeric']:
                    sel_cols['numeric'] = st.selectbox("عمود الأرقام (مبيعات/سعر):", cols, key="num_s")
            
            if st.button("احسب النتيجة ✅"):
                msg, fig = st.session_state.brain.calculate(reqs, sel_cols)
                st.session_state.messages.append({"role": "assistant", "content": msg, "chart": fig})
                st.session_state.pending_action = None
                st.rerun()
