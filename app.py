import streamlit as st
import pandas as pd
import plotly.express as px
import warnings

warnings.filterwarnings('ignore')

# ==========================================
# 1. إعدادات الصفحة
# ==========================================
st.set_page_config(page_title="المساعد التفاعلي الدقيق", layout="wide", page_icon="🎯")

st.markdown("""
<style>
    .stChatInput {position: fixed; bottom: 20px; z-index: 1000;}
    .stChatMessage {padding: 1.5rem; border-radius: 15px; margin-bottom: 1rem; border: 1px solid #e0e0e0;}
    .block-container {padding-bottom: 150px;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. منطق التحليل (Logic Core)
# ==========================================
class InteractiveBrain:
    def __init__(self, df):
        self.df = df
        self.cols = df.columns.tolist()

    def identify_requirements(self, query):
        """
        تحديد ماذا يحتاج الذكاء الاصطناعي للإجابة
        """
        q = query.lower()
        reqs = {
            'needs_numeric': False, # هل نحتاج عمود أرقام؟
            'needs_category': False, # هل نحتاج عمود تصنيف (أسماء)؟
            'needs_date': False,     # هل نحتاج عمود تاريخ؟
            'operation': 'sum',      # نوع العملية
            'title': ''              # وصف العملية
        }

        # 1. تحليل نوع العملية
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
            # العدد لا يحتاج تحديد أعمدة محددة، يمكن حسابه مباشرة

        else: # الافتراضي: المجموع
            reqs['operation'] = 'sum'
            reqs['needs_numeric'] = True
            reqs['title'] = 'الإجمالي'

        return reqs

    def calculate(self, reqs, selected_cols):
        """تنفيذ الحساب بناءً على اختيار المستخدم"""
        df_calc = self.df.copy()
        op = reqs['operation']
        
        # استخراج الأعمدة المختارة
        num_col = selected_cols.get('numeric')
        cat_col = selected_cols.get('category')
        date_col = selected_cols.get('date')

        # تنظيف الرقم إذا وجد
        if num_col:
            df_calc[num_col] = pd.to_numeric(df_calc[num_col], errors='coerce')

        # تنفيذ العملية
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
# 3. واجهة المستخدم وإدارة الحالة
# ==========================================
st.title("🎯 المحلل الدقيق (أنت تختار، هو يحسب)")

# إدارة الحالة (Session State)
if 'brain' not in st.session_state: st.session_state.brain = None
if 'messages' not in st.session_state: st.session_state.messages = []
if 'pending_action' not in st.session_state: st.session_state.pending_action = None # لتخزين العملية المعلقة

# Sidebar
with st.sidebar:
    st.header("1. الملف")
    uploaded_file = st.file_uploader("Excel/CSV", type=['xlsx', 'csv'])
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'): df = pd.read_csv(uploaded_file)
            else: df = pd.read_excel(uploaded_file)
            
            if 'brain' not in st.session_state or st.session_state.last_file != uploaded_file.name:
                st.session_state.brain = InteractiveBrain(df)
                st.session_state.last_file = uploaded_file.name
                st.session_state.messages = [{"role": "assistant", "content": "أهلاً! ارفع الملف، واسألني أي سؤال. سأطلب منك تحديد الأعمدة لضمان الدقة."}]
                st.rerun()
        except: st.error("خطأ في الملف")

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

# Input Handling
if prompt := st.chat_input("اسألني... (مثلاً: أكثر منتج مبيعا)"):
    if st.session_state.brain:
        # 1. عرض سؤال المستخدم
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()
    else:
        st.warning("ارفع الملف أولاً")

# معالجة الرد (خارج الـ chat input عشان نقدر نعرض أزرار)
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user" and not st.session_state.pending_action:
    last_query = st.session_state.messages[-1]["content"]
    
    # تحليل السؤال لمعرفة المطلوب
    brain = st.session_state.brain
    reqs = brain.identify_requirements(last_query)
    
    # تخزين الحالة لانتظار إدخال المستخدم
    st.session_state.pending_action = reqs
    st.rerun()

# ==========================================
# منطقة "التفاعل" - هنا يظهر السؤال عن الأعمدة
# ==========================================
if st.session_state.pending_action:
    reqs = st.session_state.pending_action
    cols = st.session_state.brain.cols
    
    with st.chat_message("assistant"):
        st.markdown(f"🛠️ **لإجابة سؤالك عن ({reqs['title']}) بدقة، يرجى اختيار الأعمدة الصحيحة:**")
        
        selected_cols = {}
        
        # لو العملية بسيطة (عدد) نحسب علطول
        if reqs['operation'] == 'count':
            msg, fig = st.session_state.brain.calculate(reqs, {})
            st.markdown(msg)
            st.session_state.messages.append({"role": "assistant", "content": msg, "chart": fig})
            st.session_state.pending_action = None
            # st.rerun() # لا حاجة لـ rerun هنا لتجنب loop
            
        else:
            # نعرض قوائم الاختيار (Dropdowns)
            c1, c2 = st.columns(2)
            
            with c1:
                if reqs['needs_category']:
                    selected_cols['category'] = st.selectbox("اختر عمود الأسماء (مثلاً: المنتج/الفرع):", cols, key="cat_sel")
                if reqs['needs_date']:
                    selected_cols['date'] = st.selectbox("اختر عمود التاريخ:", cols, key="date_sel")
            
            with c2:
                if reqs['needs_numeric']:
                    selected_cols['numeric'] = st.selectbox("اختر عمود الأرقام (مثلاً: المبيعات/السعر):", cols, key="num_sel")
            
            if st.button("✅ احسب النتيجة"):
                # الحساب الفعلي
                msg, fig = st.session_state.brain.calculate(reqs, selected_cols)
                
                # عرض النتيجة
                st.markdown(msg)
                if fig: st.plotly_chart(fig, use_container_width=True)
                
                # حفظ في السجل وإنهاء التعليق
                st.session_state.messages.append({"role": "assistant", "content": msg, "chart": fig})
                st.session_state.pending_action = None
                st.rerun()
