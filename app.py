import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from thefuzz import process, fuzz
import re
import warnings

# تجاهل التحذيرات
warnings.filterwarnings('ignore')

# ==========================================
# 1. إعدادات الصفحة والتصميم
# ==========================================
st.set_page_config(
    page_title="المحلل الذكي المحترف",
    layout="wide",
    page_icon="🤖",
    initial_sidebar_state="expanded"
)

# تحسين مظهر الشات ليكون مثل التطبيقات الحديثة
st.markdown("""
<style>
    .stChatInput {position: fixed; bottom: 20px; z-index: 1000; width: 80%; margin-right: 10%;}
    .block-container {padding-bottom: 120px;}
    .stChatMessage {
        padding: 1rem; 
        border-radius: 15px; 
        margin-bottom: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    [data-testid="stChatMessageContent"] { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. العقل المدبر (The Advanced Brain)
# ==========================================
class SmartBrain:
    def __init__(self, df):
        self.df = df.copy()
        # تنظيف أسماء الأعمدة
        self.df.columns = [str(c).strip() for c in self.df.columns]
        
        # تصنيف الأعمدة
        self.col_map = self._map_columns()
        
        # فهرسة القيم للبحث السريع
        self.value_index = self._create_value_index()

    def _map_columns(self):
        """تحديد وظيفة كل عمود بدقة"""
        mapping = {'numeric': [], 'date': [], 'text': [], 'id': []}
        
        for col in self.df.columns:
            # تجاهل أعمدة الـ ID لأنها لا تفيد في التحليل عادة
            if 'id' in col.lower() or 'code' in col.lower() or 'كود' in col:
                mapping['id'].append(col)
                continue
                
            if pd.api.types.is_datetime64_any_dtype(self.df[col]):
                mapping['date'].append(col)
            elif pd.api.types.is_numeric_dtype(self.df[col]):
                mapping['numeric'].append(col)
            else:
                mapping['text'].append(col)
                
        # محاولة إنقاذ أعمدة التاريخ النصية
        for col in mapping['text']:
            if any(x in col.lower() for x in ['date', 'time', 'تاريخ', 'وقت']):
                try:
                    self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
                    mapping['text'].remove(col)
                    mapping['date'].append(col)
                except: pass
        
        return mapping

    def _create_value_index(self):
        """فهرس ذكي لكل كلمة في الملف"""
        index = {}
        for col in self.col_map['text']:
            # نأخذ القيم الفريدة فقط لتسريع البحث
            vals = self.df[col].dropna().astype(str).unique()
            for v in vals:
                index[v.lower()] = col
        return index

    def normalize(self, text):
        """توحيد النص العربي للإنجليزي"""
        text = str(text).lower()
        text = re.sub(r'[إأآا]', 'ا', text)
        text = re.sub(r'ة', 'ه', text)
        text = re.sub(r'ى', 'ي', text)
        return text

    def get_best_match(self, query, candidates, threshold=80):
        """البحث عن أقرب كلمة (Fuzzy Matching)"""
        if not candidates: return None
        # نستخدم دالة process لاستخراج أفضل تطابق
        match = process.extractOne(query, candidates, scorer=fuzz.partial_ratio)
        if match and match[1] >= threshold:
            return match[0]
        return None

    def analyze_intent(self, query):
        """
        قلب النظام: يفهم المستخدم عايز إيه بالظبط (رقم ولا اسم؟)
        """
        q_norm = self.normalize(query)
        
        intent = {
            'type': 'general', # aggregation / grouping / lookup
            'target_col': None, # العمود الرقمي (مبيعات)
            'group_col': None,  # عمود التصنيف (منتج)
            'operation': 'sum', # العملية الحسابية
            'filters': {},
            'time_col': None
        }

        # 1. تحديد العمود الرقمي (Target)
        # هل المستخدم ذكر "مبيعات"، "سعر"، "راتب"؟
        for col in self.col_map['numeric']:
            if self.normalize(col) in q_norm or fuzz.partial_ratio(self.normalize(col), q_norm) > 85:
                intent['target_col'] = col
                break
        
        # لو ملقاش، بياخد أول عمود فلوس افتراضياً
        if not intent['target_col'] and self.col_map['numeric']:
            # تفضيل الأعمدة المالية
            priority = [c for c in self.col_map['numeric'] if any(k in c.lower() for k in ['sales', 'total', 'price', 'amount', 'مبيعات', 'سعر', 'اجمالي'])]
            intent['target_col'] = priority[0] if priority else self.col_map['numeric'][0]

        # 2. تحديد عمود التصنيف (Grouping)
        # هل المستخدم قال "منتج"، "عميل"، "موظف"؟
        # أو هل سأل عن "أفضل X"؟
        for col in self.col_map['text']:
            # تنظيف اسم العمود ومطابقته مع السؤال
            col_clean = self.normalize(col)
            if col_clean in q_norm or fuzz.partial_ratio(col_clean, q_norm) > 85:
                intent['group_col'] = col
                break
        
        # ذكاء إضافي: لو سأل عن "أكثر منتج" وكلمة منتج مش اسم عمود، نحاول نخمن
        if not intent['group_col']:
            if 'منتج' in q_norm or 'product' in q_norm or 'صنف' in q_norm:
                # ندور على عمود فيه كلمات زي "Name", "Item", "Product"
                candidates = [c for c in self.col_map['text'] if any(k in c.lower() for k in ['product', 'item', 'name', 'model', 'اسم', 'منتج', 'صنف'])]
                if candidates: intent['group_col'] = candidates[0]
            elif 'عميل' in q_norm or 'customer' in q_norm:
                candidates = [c for c in self.col_map['text'] if any(k in c.lower() for k in ['cust', 'client', 'name', 'عميل', 'اسم'])]
                if candidates: intent['group_col'] = candidates[0]

        # 3. تحديد العملية (Operation)
        if any(x in q_norm for x in ['متوسط', 'معدل', 'avg']): intent['operation'] = 'mean'
        elif any(x in q_norm for x in ['عدد', 'count']): intent['operation'] = 'count'
        elif any(x in q_norm for x in ['اكثر', 'اعلى', 'اكبر', 'اقصى', 'افضل', 'احسن', 'top', 'max', 'best', 'most']): 
            intent['operation'] = 'top'
            intent['type'] = 'grouping' if intent['group_col'] else 'aggregation'
        elif any(x in q_norm for x in ['اقل', 'ادنى', 'اصغر', 'اسوا', 'min', 'worst', 'least']): 
            intent['operation'] = 'bottom'
            intent['type'] = 'grouping' if intent['group_col'] else 'aggregation'
        elif any(x in q_norm for x in ['تطور', 'زمن', 'وقت', 'trend']):
            intent['type'] = 'trend'
            intent['time_col'] = self.col_map['date'][0] if self.col_map['date'] else None

        # 4. الفلاتر (هل ذكر اسم محدد؟ "مبيعات أحمد")
        words = query.split()
        for w in words:
            w_clean = self.normalize(w)
            if len(w_clean) < 2: continue
            match = process.extractOne(w, self.value_index.keys(), scorer=fuzz.ratio)
            if match and match[1] > 90: # دقة عالية
                val_found = match[0]
                col_found = self.value_index[val_found]
                # استرجاع القيمة الأصلية
                original_val = self.df[self.df[col_found].astype(str).str.lower() == val_found].iloc[0][col_found]
                intent['filters'][col_found] = original_val

        return intent

    def execute(self, query):
        intent = self.analyze_intent(query)
        
        df_wk = self.df.copy()
        
        # تطبيق الفلاتر
        filter_text = ""
        for col, val in intent['filters'].items():
            df_wk = df_wk[df_wk[col] == val]
            filter_text += f" (لـ {val})"

        target = intent['target_col']
        group = intent['group_col']
        op = intent['operation']

        # --- الحالة 1: أفضل / أسوأ (Grouping) ---
        # مثال: "أكثر منتج مبيعا"
        if op in ['top', 'bottom'] and group:
            # نجمع الأرقام حسب التصنيف (مثلاً نجمع مبيعات كل منتج)
            grouped = df_wk.groupby(group)[target].sum().reset_index()
            
            if op == 'top':
                res = grouped.sort_values(target, ascending=False).iloc[0]
                best_name = res[group]
                best_val = res[target]
                
                msg = f"🏆 **أكثر {group} مبيعاً/قيمة هو:**\n# {best_name}\n**بقيمة:** {best_val:,.2f}"
                fig = px.bar(grouped.sort_values(target, ascending=False).head(5), x=group, y=target, title=f"أفضل 5 {group}", color=target)
                return msg, fig
            else:
                res = grouped.sort_values(target, ascending=True).iloc[0]
                worst_name = res[group]
                worst_val = res[target]
                
                msg = f"📉 **أقل {group} مبيعاً/قيمة هو:**\n# {worst_name}\n**بقيمة:** {worst_val:,.2f}"
                fig = px.bar(grouped.sort_values(target, ascending=True).head(5), x=group, y=target, title=f"أقل 5 {group}", color_discrete_sequence=['red'])
                return msg, fig

        # --- الحالة 2: قيمة قصوى/دنيا فقط (Aggregation) ---
        # مثال: "أعلى سعر" (بدون ذكر منتج)
        elif op in ['top', 'bottom'] and not group:
            if op == 'top':
                val = df_wk[target].max()
                return f"🚀 **أعلى قيمة مسجلة في {target}:**\n# {val:,.2f}", None
            else:
                val = df_wk[target].min()
                return f"⬇️ **أدنى قيمة مسجلة في {target}:**\n# {val:,.2f}", None

        # --- الحالة 3: تريند زمني ---
        elif intent['type'] == 'trend' and intent['time_col']:
            time_col = intent['time_col']
            # تجميع شهري
            trend_df = df_wk.set_index(time_col).resample('M')[target].sum().reset_index()
            fig = px.line(trend_df, x=time_col, y=target, markers=True, title=f"تطور {target} عبر الزمن")
            return f"📈 **التحليل الزمني لـ {target}:**", fig

        # --- الحالة 4: سؤال عام (مجموع/متوسط) ---
        else:
            val = 0
            txt = ""
            if op == 'mean':
                val = df_wk[target].mean()
                txt = "متوسط"
            elif op == 'count':
                val = len(df_wk)
                txt = "عدد السجلات"
            else:
                val = df_wk[target].sum()
                txt = "إجمالي"
            
            return f"💰 **{txt} {target} {filter_text}:**\n# {val:,.2f}", None

# ==========================================
# 3. واجهة التطبيق
# ==========================================
st.title("🧠 المحلل الذكي (AI Analyst)")

# إدارة الحالة
if 'brain' not in st.session_state: st.session_state.brain = None
if 'messages' not in st.session_state: 
    st.session_state.messages = [{"role": "assistant", "content": "أهلاً! ارفع ملفك واسألني بذكاء، مثلاً: **'أكثر منتج مبيعا'** أو **'مبيعات القاهرة'**."}]

# Sidebar
with st.sidebar:
    st.header("📂 رفع البيانات")
    uploaded_file = st.file_uploader("ملف Excel/CSV", type=['xlsx', 'csv'])
    
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            # تفعيل المخ الجديد
            if st.session_state.brain is None:
                st.session_state.brain = SmartBrain(df)
                st.session_state.messages.append({"role": "assistant", "content": f"✅ تم تحليل الملف! وجدت {len(df)} صفاً.\nجرب تسألني الآن: **'من هو أفضل عميل؟'**"})
                st.rerun()
        except Exception as e:
            st.error(f"خطأ: {e}")

    if st.button("مسح المحادثة 🗑️"):
        st.session_state.messages = []
        st.rerun()

# Chat UI
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "chart" in msg and msg["chart"]:
            st.plotly_chart(msg["chart"], use_container_width=True)

if prompt := st.chat_input("اسألني... (مثلاً: هات أكثر منتج مبيعا)"):
    if st.session_state.brain:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("جاري التفكير..."):
                response, fig = st.session_state.brain.execute(prompt)
                st.markdown(response)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                
                st.session_state.messages.append({"role": "assistant", "content": response, "chart": fig})
    else:
        st.warning("ارفع الملف الأول يا هندسة! 😄")
