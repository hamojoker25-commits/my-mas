import streamlit as st
import pandas as pd
import plotly.express as px
import warnings

warnings.filterwarnings('ignore')

# ==========================================
# 1. إعداد الصفحة (الشكل والجو العام)
# ==========================================
st.set_page_config(
    page_title="أكاديمية تحليل البيانات",
    layout="wide",
    page_icon="🎓"
)

# تنسيق بسيط ومريح للعين
st.markdown("""
<style>
    .stChatInput {position: fixed; bottom: 20px; z-index: 1000;}
    .stChatMessage {
        padding: 1.5rem; 
        border-radius: 15px; 
        margin-bottom: 1rem; 
        border: 1px solid #eee;
        background-color: #f9f9f9;
    }
    .stButton button {
        width: 100%;
        border-radius: 10px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. مخ التعليم (The Tutor Brain)
# ==========================================
if 'step' not in st.session_state: st.session_state.step = 1
if 'df' not in st.session_state: st.session_state.df = None
if 'messages' not in st.session_state: 
    st.session_state.messages = [{"role": "assistant", "content": "أهلاً يا بطل! 👋 أنا مساعدك التعليمي.\nعشان نبدأ رحلة تحليل البيانات، أول خطوة هي إننا نجيب البيانات نفسها.\n**ممكن ترفع ملف Excel أو CSV من القائمة اللي في الجنب؟**"}]

# ==========================================
# 3. القائمة الجانبية (المعمل)
# ==========================================
with st.sidebar:
    st.header("📂 معمل البيانات")
    st.info("هنا بنرفع الملفات عشان نشتغل عليها.")
    
    uploaded_file = st.file_uploader("ارفع ملفك هنا", type=['xlsx', 'csv'])
    
    if uploaded_file:
        try:
            # كود قراءة الملف (بسيط ومباشر)
            if uploaded_file.name.endswith('.xlsx'):
                df = pd.read_excel(uploaded_file)
            else:
                # محاولة قراءة CSV بأمان
                try: df = pd.read_csv(uploaded_file, encoding='utf-8')
                except: df = pd.read_csv(uploaded_file, encoding='cp1256')
            
            st.session_state.df = df
            st.success(f"تمام! تم قراءة الملف: {len(df)} صف.")
            
            # الانتقال للخطوة الثانية لو لسه في الأولى
            if st.session_state.step == 1:
                st.session_state.step = 2
                st.session_state.messages.append({"role": "assistant", "content": "عظيم! 🎉 الملف اترفع بنجاح.\nدلوقتي البيانات بقت معانا. تقدر تشوف عينة منها في الجدول تحت.\n**جرب تسألني سؤال بسيط زي: 'كام عدد الصفوف؟' أو 'اعرض أول 5 صفوف'.**"})
                st.rerun()
                
        except Exception as e:
            st.error("في مشكلة في الملف ده، جرب ملف تاني.")

    if st.button("🗑️ ابدأ من جديد"):
        st.session_state.clear()
        st.rerun()

# ==========================================
# 4. منطقة الشات (الفصل الدراسي)
# ==========================================
st.title("🎓 أكاديمية تحليل البيانات التفاعلية")
st.caption("اتعلم تحليل البيانات وإنت بتدردش")

# عرض المحادثة
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "chart" in msg:
            st.plotly_chart(msg["chart"], use_container_width=True)
        if "data" in msg:
            st.dataframe(msg["data"])

# استقبال الأسئلة
if prompt := st.chat_input("اكتب سؤالك هنا..."):
    # 1. عرض سؤال الطالب
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. رد المعلم (المنطق)
    with st.chat_message("assistant"):
        response = ""
        chart = None
        data_view = None
        
        if st.session_state.df is None:
            response = "يا صديقي، لازم نرفع ملف الأول عشان نلاقي حاجة نحللها! 😉 بص على القائمة الجانبية."
        else:
            df = st.session_state.df
            q = prompt.lower()
            
            # --- درس 1: استكشاف البيانات ---
            if any(x in q for x in ['صفوف', 'عدد', 'count', 'كم']):
                response = f"سؤال ممتاز! في لغة تحليل البيانات، بنستخدم دالة اسمها `len()` أو `shape` عشان نعرف الحجم.\nملفك فيه **{len(df)}** صف (سجل)."
            
            elif any(x in q for x in ['اعرض', 'وريني', 'show', 'head', 'عينة']):
                response = "حاضر، دي أول 5 صفوف من بياناتك. الدالة المستخدمة هنا اسمها `df.head()`:"
                data_view = df.head()
            
            elif any(x in q for x in ['اعمدة', 'اسماء', 'columns']):
                response = "دي أسماء الأعمدة (Columns) اللي في ملفك:"
                data_view = pd.DataFrame(df.columns, columns=["اسم العمود"])

            # --- درس 2: الحسابات البسيطة ---
            elif any(x in q for x in ['مجموع', 'اجمالي', 'sum']):
                # نحاول نلاقي عمود أرقام
                num_cols = df.select_dtypes(include=['number']).columns
                if len(num_cols) > 0:
                    col = num_cols[0] # ناخد أول واحد كمثال
                    total = df[col].sum()
                    response = f"عشان نحسب المجموع، بنستخدم `sum()`. مثلاً لعمود **{col}**:\nالإجمالي = `{total:,.2f}`"
                else:
                    response = "ملفك مفيهوش أرقام عشان أجمعها! 😅"

            # --- درس 3: الرسم البياني ---
            elif any(x in q for x in ['رسم', 'بياني', 'chart', 'plot']):
                # نحاول نرسم حاجة بسيطة
                num_cols = df.select_dtypes(include=['number']).columns
                if len(num_cols) > 0:
                    col = num_cols[0]
                    response = f"الرسم البياني بيخلي البيانات تنطق! ده توزيع لقيم عمود **{col}**:"
                    chart = px.histogram(df, x=col, title=f"توزيع {col}")
                else:
                    response = "محتاجين أعمدة رقمية عشان نرسم."

            # --- رد عام ---
            else:
                response = "سؤال حلو! بس أنا لسه بتعلم. جرب تسألني عن: 'عدد الصفوف'، 'المجموع'، أو 'رسم بياني'."

        st.markdown(response)
        if data_view is not None: st.dataframe(data_view)
        if chart is not None: st.plotly_chart(chart, use_container_width=True)
        
        # حفظ الرد في الذاكرة
        msg_data = {"role": "assistant", "content": response}
        if chart: msg_data["chart"] = chart
        if data_view is not None: msg_data["data"] = data_view
        st.session_state.messages.append(msg_data)
