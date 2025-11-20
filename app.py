import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import IsolationForest
from thefuzz import process, fuzz
import re
import warnings

# تجاهل التحذيرات
warnings.filterwarnings('ignore')

# ==========================================
# 1. إعدادات الصفحة والتصميم
# ==========================================
st.set_page_config(
    page_title="AI Data Analyst Pro",
    layout="wide",
    page_icon="🧠",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stChatInput {position: fixed; bottom: 20px; z-index: 1000;}
    .block-container {padding-bottom: 120px;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. المحرك الإدراكي العميق (Deep AI Core)
# ==========================================
class DataBrain:
    def __init__(self, df):
        self.df = df.copy()
        # تنظيف أسماء الأعمدة
        self.df.columns = [str(c).strip() for c in self.df.columns]
        
        # 1. فهرسة البيانات (Indexing)
        self.column_types = self._identify_columns()
        self.value_index = self._index_unique_values()

    def _identify_columns(self):
        """تحديد أنواع الأعمدة بدقة عالية"""
        roles = {'numeric': [], 'date': [], 'text': []}
        
        for col in self.df.columns:
            # هل هو تاريخ؟
            if pd.api.types.is_datetime64_any_dtype(self.df[col]):
                roles['date'].append(col)
            # هل هو رقم؟
            elif pd.api.types.is_numeric_dtype(self.df[col]):
                roles['numeric'].append(col)
            # إذن هو نص
            else:
                roles['text'].append(col)
                
        # محاولة اكتشاف تواريخ مختبئة في نصوص
        for col in roles['text']:
            if 'date' in col.lower() or 'تاريخ' in col or 'وقت' in col:
                try:
                    self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
                    if pd.api.types.is_datetime64_any_dtype(self.df[col]):
                        roles['text'].remove(col)
                        roles['date'].append(col)
                except: pass
                
        return roles

    def _index_unique_values(self):
        """إنشاء خريطة لكل كلمة موجودة في الملف للبحث السريع"""
        index = {}
        for col in self.column_types['text']:
            # نأخذ القيم الفريدة وننظفها
            unique_vals = self.df[col].dropna().astype(str).unique()
            for val in unique_vals:
                # المفتاح هو القيمة، والقيمة هي اسم العمود
                index[val.lower()] = col
        return index

    def normalize_text(self, text):
        """توحيد النصوص العربية والإنجليزية للبحث"""
        text = str(text).lower()
        text = re.sub(r'[إأآا]', 'ا', text) # توحيد الألف
        text = re.sub(r'ة', 'ه', text)     # توحيد التاء المربوطة
        text = re.sub(r'ى', 'ي', text)     # توحيد الياء
        text = re.sub(r'[^\w\s]', '', text) # إزالة التشكيل والرموز
        return text

    def understand_query(self, query):
        """
        المخ الحقيقي: يفهم نية المستخدم ويستخرج الفلاتر والأهداف
        """
        query_norm = self.normalize_text(query)
        
        intent = {
            'operation': 'sum', # default
            'target_col': None,
            'filters': {},
            'group_by': None,
            'time_frame': None,
            'chart_type': None
        }

        # 1. اكتشاف العملية المطلوبة (Operation)
        if any(x in query_norm for x in ['متوسط', 'معدل', 'avg', 'average']): 
            intent['operation'] = 'mean'
        elif any(x in query_norm for x in ['عدد', 'count', 'كم']): 
            intent['operation'] = 'count'
        elif any(x in query_norm for x in ['اقصى', 'اعلى', 'اكبر', 'max', 'best', 'top']): 
            intent['operation'] = 'max'
        elif any(x in query_norm for x in ['ادنى', 'اقل', 'اصغر', 'min', 'worst']): 
            intent['operation'] = 'min'
        elif any(x in query_norm for x in ['تطور', 'نمو', 'trend', 'line']): 
            intent['chart_type'] = 'line'
        elif any(x in query_norm for x in ['توزيع', 'نسبة', 'pie']): 
            intent['chart_type'] = 'pie'

        # 2. اكتشاف العمود المستهدف (Target Column)
        # نبحث عن اسم عمود رقمي في السؤال
        best_score = 0
        for col in self.column_types['numeric']:
            col_norm = self.normalize_text(col)
            # استخدام Fuzzy Matching للتعامل مع الأخطاء الإملائية
            score = fuzz.partial_ratio(col_norm, query_norm)
            if score > 80 and score > best_score:
                intent['target_col'] = col
                best_score = score
        
        # لو ملقاش عمود محدد، بياخد أول عمود فلوس أو كمية
        if not intent['target_col'] and self.column_types['numeric']:
            # تفضيل الأعمدة اللي فيها "Sales", "Price", "Total"
            priority_cols = [c for c in self.column_types['numeric'] if any(x in c.lower() for x in ['sales', 'total', 'price', 'amount', 'مبيعات', 'سعر', 'اجمالي'])]
            intent['target_col'] = priority_cols[0] if priority_cols else self.column_types['numeric'][0]

        # 3. اكتشاف الفلاتر (Filters) - أذكى جزء
        # يفحص كل كلمة في السؤال هل هي موجودة كقيمة في الداتا؟
        words = query.split()
        for word in words:
            word_clean = self.normalize_text(word)
            if len(word_clean) < 2: continue
            
            # البحث في فهرس القيم
            # نستخدم process.extractOne للبحث الذكي عن أقرب كلمة
            matches = process.extractOne(word, self.value_index.keys(), scorer=fuzz.ratio)
            if matches and matches[1] > 85: # لو نسبة التطابق أعلى من 85%
                found_val = matches[0]
                col_name = self.value_index[found_val]
                # نأخذ القيمة الأصلية من الداتا فريم
                # (نبحث عن القيمة الأصلية التي طابقت القيمة المصغرة)
                original_val = self.df[self.df[col_name].astype(str).str.lower() == found_val].iloc[0][col_name]
                intent['filters'][col_name] = original_val

        # 4. اكتشاف التجميع (Group By)
        # لو السؤال فيه "لكل موظف" أو "حسب المنتج"
        if 'لكل' in query_norm or 'حسب' in query_norm or 'by' in query.lower():
            for col in self.column_types['text']:
                col_norm = self.normalize_text(col)
                if fuzz.partial_ratio(col_norm, query_norm) > 85:
                    intent['group_by'] = col
                    break
        
        return intent

    def execute_query(self, query):
        intent = self.understand_query(query)
        
        # 1. تطبيق الفلاتر
        filtered_df = self.df.copy()
        filter_desc = []
        for col, val in intent['filters'].items():
            filtered_df = filtered_df[filtered_df[col] == val]
            filter_desc.append(f"{col} = {val}")
        
        context_msg = f" (لـ {' و '.join(filter_desc)})" if filter_desc else " (للكل)"
        target = intent['target_col']
        
        # 2. معالجة الأوامر الخاصة (الشواذ)
        if any(x in query for x in ['خطأ', 'مشكلة', 'شاذ', 'anomaly']):
            model = IsolationForest(contamination=0.01, random_state=42)
            data = self.df[[target]].fillna(0)
            preds = model.fit_predict(data)
            anomalies = self.df[preds == -1]
            return f"🚨 **كشف الأخطاء:** وجدت {len(anomalies)} حالات شاذة في {target}.", anomalies

        # 3. تنفيذ الحسابات
        result_text = ""
        chart = None
        
        try:
            # حالة التجميع (Group By) أو الرسم البياني
            if intent['group_by'] or intent['chart_type'] or 'افضل' in query or 'top' in query:
                group_col = intent['group_by']
                
                # لو مفيش عمود تجميع محدد بس طلب "أفضل"، نخمن عمود تصنيف
                if not group_col and self.column_types['text']:
                    group_col = self.column_types['text'][0] # افتراض
                
                if group_col:
                    grouped = filtered_df.groupby(group_col)[target].sum().sort_values(ascending=False)
                    
                    if 'افضل' in query or 'top' in query or 'max' in intent['operation']:
                        grouped = grouped.head(5)
                        title = f"🏆 أفضل 5 {group_col} حسب {target}"
                    else:
                        grouped = grouped.head(10) # عرض أول 10 لتجنب الزحمة
                        title = f"تحليل {target} حسب {group_col}"
                    
                    if intent['chart_type'] == 'pie':
                        chart = px.pie(names=grouped.index, values=grouped.values, title=title)
                    else:
                        chart = px.bar(x=grouped.index, y=grouped.values, title=title, labels={'x': group_col, 'y': target})
                    
                    result_text = f"📊 **تحليل مفصل {context_msg}:**\nتم التجميع حسب **{group_col}**. انظر الرسم البياني."
            
            # حالة التطور الزمني
            elif intent['chart_type'] == 'line' and self.column_types['date']:
                date_col = self.column_types['date'][0]
                # التجميع الشهري افتراضياً
                trend = filtered_df.set_index(date_col).resample('M')[target].sum().reset_index()
                chart = px.line(trend, x=date_col, y=target, title=f"تطور {target} عبر الزمن")
                result_text = f"📈 **التريند الزمني {context_msg}:**"

            # الحالة العادية (رقم واحد)
            else:
                val = 0
                op_name = ""
                if intent['operation'] == 'sum':
                    val = filtered_df[target].sum()
                    op_name = "إجمالي"
                elif intent['operation'] == 'mean':
                    val = filtered_df[target].mean()
                    op_name = "متوسط"
                elif intent['operation'] == 'max':
                    val = filtered_df[target].max()
                    op_name = "أقصى"
                elif intent['operation'] == 'min':
                    val = filtered_df[target].min()
                    op_name = "أدنى"
                elif intent['operation'] == 'count':
                    val = len(filtered_df)
                    op_name = "عدد"
                
                result_text = f"🔢 **النتيجة {context_msg}:**\n{op_name} **{target}** = `{val:,.2f}`"

        except Exception as e:
            result_text = f"⚠️ عذراً، حدث خطأ أثناء الحساب. تأكد أن العمود '{target}' يحتوي على أرقام.\n(الخطأ: {str(e)})"

        return result_text, chart

# ==========================================
# 3. واجهة المستخدم
# ==========================================
st.title("🤖 العقل المحلل (AI Brain)")

# --- Sidebar ---
with st.sidebar:
    st.header("📂 البيانات")
    uploaded_file = st.file_uploader("ارفع الملف (Excel/CSV)", type=['xlsx', 'csv'])
    
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            # تشغيل المخ
            if 'brain' not in st.session_state or st.session_state.last_file != uploaded_file.name:
                st.session_state.brain = DataBrain(df)
                st.session_state.last_file = uploaded_file.name
                st.session_state.messages = [{"role": "assistant", "content": f"✅ تم قراءة الملف وفهرسة {len(df)} سجل.\nأنا جاهز! جرب تقول: 'مبيعات احمد' أو 'أفضل منتج' أو 'تطور الأرباح'."}]
                st.rerun()
                
        except Exception as e:
            st.error("فشل قراءة الملف.")

    if st.button("🗑️ مسح المحادثة"):
        st.session_state.messages = []
        st.rerun()

# --- Chat Logic ---
if 'messages' not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "مرحباً 👋 ارفع الملف واسألني أي سؤال بالعامية أو الفصحى."}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "chart" in msg and msg["chart"] is not None:
            # التحقق إذا كان الرسم البياني عبارة عن داتا فريم (للأخطاء) أو رسم (Plotly)
            if isinstance(msg["chart"], pd.DataFrame):
                st.dataframe(msg["chart"])
            else:
                st.plotly_chart(msg["chart"], use_container_width=True)

if prompt := st.chat_input("اكتب سؤالك هنا..."):
    if 'brain' in st.session_state:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("جاري التفكير..."):
                response, chart = st.session_state.brain.execute_query(prompt)
                st.markdown(response)
                if chart is not None:
                    if isinstance(chart, pd.DataFrame):
                        st.dataframe(chart)
                    else:
                        st.plotly_chart(chart, use_container_width=True)
                
                st.session_state.messages.append({"role": "assistant", "content": response, "chart": chart})
    else:
        st.warning("يرجى رفع الملف أولاً!")
