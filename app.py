import streamlit as st
import pandas as pd
import plotly.express as px
import warnings

warnings.filterwarnings('ignore')

# ==========================================
# 1. إعدادات الصفحة
# ==========================================
st.set_page_config(page_title="المحلل الذكي النهائي", layout="wide", page_icon="🛡️")

st.markdown("""
<style>
    .stChatInput {position: fixed; bottom: 20px; z-index: 1000;}
    .stChatMessage {padding: 1.5rem; border-radius: 15px; margin-bottom: 1rem; border: 1px solid #e0e0e0;}
    .block-container {padding-bottom: 150px;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. تهيئة الذاكرة (Fixing the Error Here)
# ==========================================
# هنا الحل: بنتأكد إن كل المتغيرات موجودة قبل ما نستخدمها
if 'brain' not in st.session_state: st.session_state.brain = None
if 'messages' not in st.session_state: st.session_state.messages = []
if 'pending_action' not in st.session_state: st.session_state.pending_action = None
if 'last_file' not in st.session_state: st.session_state.last_file = None  # <-- ده السطر اللي كان ناقص

# ==========================================
# 3. منطق التحليل (Logic Core)
# ==========================================
class InteractiveBrain:
    def __init__(self, df):
        self.df = df
        # تنظيف أسماء الأعمدة
        self.df.columns = [str(c).strip() for c in self.df.columns]
        self.cols = self.df.columns.tolist()

    def identify_requirements(self, query):
        q = query.lower()
        reqs = {
            'needs_numeric': False,
            'needs_category': False,
            'needs_date': False,
            'operation': 'sum',
            'title': ''
        }

        if any(x in q for x in ['اكثر', 'اعلى', 'اكبر', 'افضل', 'top', 'max', 'best']):
            reqs['operation'] = 'top'
            reqs['needs_numeric'] = True
            reqs['needs_category'] = True
            reqs['title'] = 'الأكثر/الأعلى'

        elif any(x in q for x in ['اقل', 'ادنى', 'اصغر', 'اسوا', 'min', 'worst']):
            reqs['operation'] = 'bottom'
            reqs['needs_numeric'] = True
            reqs['needs_category'] = True
            reqs['title'] = 'الأقل/الأدنى'

        elif any(x in q for x in ['متوسط', 'معدل', 'avg']):
            reqs['operation'] = 'mean'
            reqs['needs_numeric'] = True
            reqs['title'] = 'المتوسط'

        elif any(x in q for x in ['تطور', 'زمن', 'trend']):
            reqs['operation'] = 'trend'
            reqs['needs_numeric'] = True
            reqs['needs_date'] = True
            reqs['title'] = 'التحليل الزمني'

        elif any(x in q for x in ['عدد', 'count']):
            reqs['operation'] = 'count'
            reqs['title'] = 'عدد السجلات'

        else:
            reqs['operation'] = 'sum'
            reqs['needs_numeric'] = True
            reqs['title'] = 'الإجمالي'

        return reqs

    def calculate(self, reqs, selected_cols):
        df_calc = self.df.copy()
        op = reqs['operation']
        
        num_col = selected_cols.get('numeric')
        cat_col = selected_cols.get('category')
        date_col = selected_cols.get('date')

        # تنظيف الأرقام
        if num_col:
            df_calc[num_col] = pd.to_numeric(df_calc[num_col], errors='coerce')

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

        return "حدث خطأ غير متوقع", None

# ==========================================
# 4. واجهة المستخدم
# ==========================================
st.title("🎯 المحلل الذكي (إصلاح الأخطاء)")

# Sidebar - File Upload
with st.sidebar:
    st.header("1. رفع الملف")
    uploaded_file = st.file_uploader("Excel/CSV", type=['xlsx', 'csv'])
    
    if uploaded_file:
        try:
            # منطق قراءة الملف القوي (عربي/إنجليزي)
            if uploaded_file.name.endswith('.xlsx') or uploaded_file.name.endswith('.xls'):
                df = pd.read_excel(uploaded_file)
            elif uploaded_file.name.endswith('.csv'):
                try:
                    df = pd.read_csv(uploaded_file, encoding='utf-8')
                except:
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, encoding='utf-8-sig') # للعربي أحياناً
                except:
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, encoding='cp1256') # ويندوز عربي
            
            # هنا كان بيحصل الخطأ، دلوقتي صلحناه بوجود last_file في الأول
            if st.session_state.last_file != uploaded_file.name:
                st.session_state.brain = InteractiveBrain(df)
                st.session_state.last_file = uploaded_file.name
                st.session_state.messages = [{"role": "assistant", "content": "✅ الملف جاهز! اسألني وأنا هطلب منك توضحلي الأعمدة عشان الدقة."}]
                st.rerun()
                
        except Exception as e:
            st.error(f"مشكلة في الملف: {e}")

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

# Input Area
if prompt := st.chat_input("اسألني... (مثلاً: أكثر عميل اشترى)"):
    if st.session_state.brain:
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()
    else:
        st.warning("ارفع الملف أولاً")

# Logic Processing (After Input)
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user" and not st.session_state.pending_action:
    last_query = st.session_state.messages[-1]["content"]
    brain = st.session_state.brain
    if brain:
        reqs = brain.identify_requirements(last_query)
        st.session_state.pending_action = reqs
        st.rerun()

# Interactive Action Area
if st.session_state.pending_action:
    reqs = st.session_state.pending_action
    cols = st.session_state.brain.cols
    
    with st.chat_message("assistant"):
        st.markdown(f"🛠️ **عشان أحسب ({reqs['title']}) صح، اختارلي الأعمدة:**")
        
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
