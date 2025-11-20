import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import warnings

warnings.filterwarnings('ignore')

# ==========================================
# 1. تصميم الواجهة الخارق (Futuristic UI)
# ==========================================
st.set_page_config(page_title="AI Data Beast", layout="wide", page_icon="🧠")

st.markdown("""
<style>
    /* تحسين شكل الشات */
    .stChatInput {position: fixed; bottom: 20px; z-index: 1000;}
    .stChatMessage {
        padding: 1.5rem; 
        border-radius: 20px; 
        margin-bottom: 1rem; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 1px solid #333;
    }
    
    /* تحسين شكل القوائم الجانبية */
    [data-testid="stSidebar"] {
        background-color: #111;
        border-right: 1px solid #333;
    }
    
    /* تحسين الأزرار */
    .stButton button {
        background: linear-gradient(45deg, #FF4B2B, #FF416C);
        color: white;
        border-radius: 10px;
        border: none;
        font-weight: bold;
        padding: 10px 20px;
    }
    .stButton button:hover {
        transform: scale(1.02);
    }

    /* العناوين */
    h1 {
        background: -webkit-linear-gradient(#eee, #333);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
    }
    
    .block-container {padding-bottom: 150px;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. المخيخ (State Management)
# ==========================================
if 'brain' not in st.session_state: st.session_state.brain = None
if 'messages' not in st.session_state: st.session_state.messages = []
if 'pending_action' not in st.session_state: st.session_state.pending_action = None
if 'df' not in st.session_state: st.session_state.df = None

# ==========================================
# 3. العقل المدبر (The Super Logic Core)
# ==========================================
class SuperBrain:
    def __init__(self, df):
        self.df = df
        self.df.columns = [str(c).strip() for c in self.df.columns]
        self.cols = self.df.columns.tolist()

    def identify_requirements(self, query):
        """يفهم السؤال ويحدد المطلوب + يقترح تحليلات إضافية"""
        q = query.lower()
        reqs = {
            'operation': 'sum',
            'needs_numeric': False,
            'needs_category': False,
            'needs_date': False,
            'title': '',
            'insight_mode': False # وضع التحليل العميق
        }

        # تحليل الكلمات المفتاحية
        if any(x in q for x in ['اكثر', 'اعلى', 'اكبر', 'افضل', 'top', 'max', 'best']):
            reqs.update({'operation': 'top', 'needs_numeric': True, 'needs_category': True, 'title': 'الأفضل / الأعلى'})
        elif any(x in q for x in ['اقل', 'ادنى', 'اصغر', 'اسوا', 'min', 'worst']):
            reqs.update({'operation': 'bottom', 'needs_numeric': True, 'needs_category': True, 'title': 'الأقل / الأدنى'})
        elif any(x in q for x in ['متوسط', 'معدل', 'avg']):
            reqs.update({'operation': 'mean', 'needs_numeric': True, 'title': 'المتوسط العام', 'insight_mode': True})
        elif any(x in q for x in ['تطور', 'زمن', 'trend', 'time']):
            reqs.update({'operation': 'trend', 'needs_numeric': True, 'needs_date': True, 'title': 'التحليل الزمني'})
        elif any(x in q for x in ['عدد', 'count']):
            reqs.update({'operation': 'count', 'title': 'التعداد'})
        else:
            # الافتراضي: مجموع + تحليل عميق
            reqs.update({'operation': 'sum', 'needs_numeric': True, 'title': 'الإجمالي والملخص', 'insight_mode': True})
            
        return reqs

    def calculate(self, reqs, selected_cols):
        df_c = self.df.copy()
        op = reqs['operation']
        num = selected_cols.get('numeric')
        cat = selected_cols.get('category')
        date = selected_cols.get('date')

        if num: df_c[num] = pd.to_numeric(df_c[num], errors='coerce')

        # --- 1. تحليل الترتيب (Top/Bottom) ---
        if op in ['top', 'bottom']:
            asc = (op == 'bottom')
            grouped = df_c.groupby(cat)[num].sum().sort_values(ascending=asc)
            top_item = grouped.index[0]
            top_val = grouped.iloc[0]
            
            # ذكاء إضافي: حساب النسبة المئوية
            total_val = df_c[num].sum()
            percent = (top_val / total_val) * 100 if total_val > 0 else 0
            
            emoji = "🏆" if op == 'top' else "📉"
            color = 'viridis' if op == 'top' else 'reds_r'
            
            msg = f"""
            ### {emoji} النتيجة:
            الـ **{cat}** رقم 1 هو: **{top_item}**
            - القيمة: `{top_val:,.2f}`
            - يمثل **{percent:.1f}%** من إجمالي البيانات!
            """
            
            fig = px.bar(grouped.head(10), x=grouped.index, y=grouped.values, 
                         title=f"ترتيب أهم 10 {cat}", color=grouped.values, color_continuous_scale=color)
            return msg, fig

        # --- 2. التحليل الزمني (Trend) ---
        elif op == 'trend':
            df_c[date] = pd.to_datetime(df_c[date], errors='coerce')
            trend = df_c.groupby(date)[num].sum().reset_index()
            
            # ذكاء إضافي: تحديد يوم الذروة
            peak_day = trend.loc[trend[num].idxmax()]
            
            msg = f"""
            ### 📈 التحليل الزمني:
            تم تتبع **{num}** عبر الزمن.
            - 📅 **يوم الذروة:** {peak_day[date].strftime('%Y-%m-%d')}
            - 💰 **القيمة في الذروة:** {peak_day[num]:,.2f}
            """
            fig = px.area(trend, x=date, y=num, title=f"مسار {num} الزمني", line_shape='spline')
            return msg, fig

        # --- 3. التحليل الرقمي الشامل (Insights) ---
        elif reqs['insight_mode'] and num:
            total = df_c[num].sum()
            avg = df_c[num].mean()
            maxx = df_c[num].max()
            count = len(df_c)
            
            msg = f"""
            ### 💰 تقرير الذكاء الاصطناعي عن ({num}):
            | المؤشر | القيمة |
            | :--- | :--- |
            | **الإجمالي (Sum)** | `{total:,.2f}` |
            | **المتوسط (Average)** | `{avg:,.2f}` |
            | **أعلى قيمة عملية** | `{maxx:,.2f}` |
            | **عدد العمليات** | `{count}` |
            
            ✅ **الخلاصة:** البيانات تظهر نشاطاً بقيمة إجمالية {total:,.0f}.
            """
            # رسم بياني لتوزيع القيم (Histogram)
            fig = px.histogram(df_c, x=num, title=f"توزيع قيم {num}", nbins=20, color_discrete_sequence=['#00CC96'])
            return msg, fig

        # --- 4. التعداد ---
        elif op == 'count':
            return f"### 🔢 عدد السجلات في الملف: `{len(df_c)}` صف.", None

        return "حدث خطأ غير متوقع.", None

# ==========================================
# 4. واجهة المستخدم (The Dashboard)
# ==========================================
st.title("🧠 AI Data Analyst Pro (Max Power)")
st.caption("أقوى نظام تحليل بيانات تفاعلي - دقة 100%")

# Sidebar
with st.sidebar:
    st.header("📂 مركز التحكم")
    uploaded_file = st.file_uploader("ارفع الملف (Excel/CSV)", type=['xlsx', 'csv'])
    
    if uploaded_file:
        if st.session_state.df is None:
            try:
                if uploaded_file.name.endswith('.xlsx'): df = pd.read_excel(uploaded_file)
                else:
                    # القارئ الذكي للغات المتعددة
                    try: df = pd.read_csv(uploaded_file, encoding='utf-8')
                    except: df = pd.read_csv(uploaded_file, encoding='cp1256')
                
                st.session_state.df = df
                st.session_state.brain = SuperBrain(df)
                st.session_state.messages = [{"role": "assistant", "content": "✅ **تم تفعيل النظام!**\nأنا جاهز للتحليل العميق. جرب تقول: 'تحليل شامل للمبيعات' أو 'أفضل منتج'."}]
                st.rerun()
            except Exception as e:
                st.error(f"خطأ: {e}")

    if st.session_state.df is not None:
        st.success(f"✅ ملف مفعل: {len(st.session_state.df)} سجل")
        if st.button("🗑️ تصفير النظام"):
            st.session_state.df = None
            st.session_state.brain = None
            st.session_state.messages = []
            st.session_state.pending_action = None
            st.rerun()

# Chat Feed
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "chart" in msg and msg["chart"]:
            st.plotly_chart(msg["chart"], use_container_width=True)

# User Input
if st.session_state.df is not None:
    if prompt := st.chat_input("اكتب سؤالك للذكاء الاصطناعي..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()
else:
    st.info("👋 يرجى رفع ملف البيانات من القائمة الجانبية للبدء.")

# Logic & Processing
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user" and not st.session_state.pending_action:
    last_query = st.session_state.messages[-1]["content"]
    brain = st.session_state.brain
    if brain:
        # تحليل السؤال
        reqs = brain.identify_requirements(last_query)
        st.session_state.pending_action = reqs
        st.rerun()

# Interactive Action (The Magic Part)
if st.session_state.pending_action:
    reqs = st.session_state.pending_action
    cols = st.session_state.brain.cols
    
    with st.chat_message("assistant"):
        st.markdown(f"⚡ **تحليل ذكي لـ ({reqs['title']})**\nعشان تكون الدقة 100%، أكد لي المعلومات دي:")
        
        # تخطي الخطوة لو العملية بسيطة
        if reqs['operation'] == 'count':
            msg, fig = st.session_state.brain.calculate(reqs, {})
            st.session_state.messages.append({"role": "assistant", "content": msg})
            st.session_state.pending_action = None
            st.rerun()
        
        # القوائم المنسدلة
        c1, c2 = st.columns(2)
        sel_cols = {}
        
        with c1:
            if reqs['needs_category']:
                sel_cols['category'] = st.selectbox("📌 عمود التصنيف (الأسماء):", cols, key="cat_super")
            if reqs['needs_date']:
                sel_cols['date'] = st.selectbox("📅 عمود التاريخ:", cols, key="date_super")
        
        with c2:
            if reqs['needs_numeric']:
                sel_cols['numeric'] = st.selectbox("🔢 عمود الأرقام (القيم):", cols, key="num_super")
        
        # زر التنفيذ
        if st.button("🚀 تنفيذ التحليل"):
            with st.spinner("جاري معالجة البيانات..."):
                msg, fig = st.session_state.brain.calculate(reqs, sel_cols)
                st.session_state.messages.append({"role": "assistant", "content": msg, "chart": fig})
                st.session_state.pending_action = None
                st.rerun()
