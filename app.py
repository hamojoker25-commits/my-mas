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
# 1. إعدادات الصفحة
# ==========================================
st.set_page_config(
    page_title="AI Data Genius",
    layout="wide",
    page_icon="🧠",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stChatInput {position: fixed; bottom: 20px; z-index: 1000;}
    .block-container {padding-bottom: 120px;}
    .stChatMessage {
        padding: 1.5rem; 
        border-radius: 15px; 
        margin-bottom: 1rem; 
        border: 1px solid #f0f2f6;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. العقل العبقري (The Genius Brain)
# ==========================================
class GeniusBrain:
    def __init__(self, df):
        self.df = df.copy()
        # تنظيف أسماء الأعمدة: إزالة المسافات وتحويلها لنص
        self.df.columns = [str(c).strip() for c in self.df.columns]
        
        # قاموس المفاهيم (السر في الذكاء)
        self.concepts = {
            'product': ['product', 'item', 'sku', 'model', 'name', 'desc', 'commodity', 'منتج', 'صنف', 'نوع', 'موديل', 'اسم', 'بضاعة', 'سلعة'],
            'customer': ['cust', 'client', 'buyer', 'consumer', 'عميل', 'زبون', 'مشتري', 'اسم العميل'],
            'location': ['branch', 'city', 'region', 'governorate', 'area', 'zone', 'فرع', 'مدينة', 'منطقة', 'محافظة', 'مكان'],
            'money': ['sales', 'price', 'amount', 'total', 'revenue', 'profit', 'cost', 'value', 'مبيعات', 'سعر', 'قيمة', 'اجمالي', 'مبلغ', 'ربح', 'تكلفة', 'دخل'],
            'date': ['date', 'time', 'day', 'month', 'year', 'تاريخ', 'وقت', 'زمن', 'يوم', 'شهر', 'سنة']
        }
        
        self.col_roles = self._assign_roles()
        self.value_index = self._index_values()

    def _assign_roles(self):
        """تحديد هوية كل عمود بدقة (هل هو منتج؟ عميل؟ فرع؟)"""
        roles = {
            'product_col': None,
            'customer_col': None,
            'location_col': None,
            'date_col': None,
            'money_cols': [],
            'text_cols': []
        }
        
        for col in self.df.columns:
            col_lower = col.lower()
            
            # 1. كشف التاريخ
            if pd.api.types.is_datetime64_any_dtype(self.df[col]) or any(x in col_lower for x in self.concepts['date']):
                try:
                    self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
                    roles['date_col'] = col
                    continue
                except: pass

            # 2. كشف الفلوس (الأرقام)
            if pd.api.types.is_numeric_dtype(self.df[col]):
                # لو الاسم فيه كلمة فلوس
                if any(x in col_lower for x in self.concepts['money']):
                    roles['money_cols'].append(col)
                # لو مفيهوش، بس رقمي وقيمه كتير (مش كود فرع مثلاً)
                elif self.df[col].nunique() > 10:
                    roles['money_cols'].append(col)
                continue

            # 3. كشف النصوص (منتج، عميل، فرع)
            roles['text_cols'].append(col)
            
            # تقييم العمود: هل هو منتج؟
            if not roles['product_col']:
                score = 0
                for keyword in self.concepts['product']:
                    if keyword in col_lower: score += 2
                # المنتجات عادة عددها كبير
                if self.df[col].nunique() > 5: score += 1
                if score >= 2: roles['product_col'] = col
                
            # تقييم العمود: هل هو عميل؟
            if not roles['customer_col'] and col != roles['product_col']:
                for keyword in self.concepts['customer']:
                    if keyword in col_lower: 
                        roles['customer_col'] = col
                        break
            
            # تقييم العمود: هل هو موقع/فرع؟
            if not roles['location_col'] and col != roles['product_col'] and col != roles['customer_col']:
                 for keyword in self.concepts['location']:
                    if keyword in col_lower: 
                        roles['location_col'] = col
                        break
        
        # Fallback: لو ملقاش عمود منتج صريح، ياخد أول عمود نصي يعتبره هو "الاسم"
        if not roles['product_col'] and roles['text_cols']:
            roles['product_col'] = roles['text_cols'][0]

        # ترتيب أعمدة الفلوس (الأولوية للمبيعات والسعر)
        roles['money_cols'].sort(key=lambda x: 2 if any(k in x.lower() for k in ['sales', 'total', 'price', 'مبيعات', 'اجمالي']) else 1, reverse=True)
        
        return roles

    def _index_values(self):
        """فهرسة القيم للبحث السريع"""
        index = {}
        for col in self.col_roles['text_cols']:
            vals = self.df[col].dropna().astype(str).unique()
            for v in vals:
                index[v.lower()] = col
        return index

    def normalize(self, text):
        text = str(text).lower()
        text = re.sub(r'[إأآا]', 'ا', text)
        text = re.sub(r'ة', 'ه', text)
        text = re.sub(r'ى', 'ي', text)
        return text

    def understand(self, query):
        """تحليل السؤال وفهم النية بدقة"""
        q = self.normalize(query)
        
        intent = {
            'target_numeric': self.col_roles['money_cols'][0] if self.col_roles['money_cols'] else None,
            'group_by': None,
            'operation': 'sum',
            'filters': {},
            'time_analysis': False
        }

        # 1. اكتشاف عمود التجميع (Group By) - أهم جزء
        # هل المستخدم بيسأل عن "منتج" ولا "فرع" ولا "عميل"؟
        
        # فحص كلمات المنتجات
        if any(x in q for x in self.concepts['product']):
            intent['group_by'] = self.col_roles['product_col']
        # فحص كلمات العملاء
        elif any(x in q for x in self.concepts['customer']):
            intent['group_by'] = self.col_roles['customer_col']
        # فحص كلمات الفروع
        elif any(x in q for x in self.concepts['location']):
            intent['group_by'] = self.col_roles['location_col']
        
        # لو المستخدم حدد عمود معين بالاسم (مثلاً "حسب المنطقة")
        if not intent['group_by']:
            match = process.extractOne(query, self.col_roles['text_cols'], scorer=fuzz.partial_ratio)
            if match and match[1] > 85:
                intent['group_by'] = match[0]

        # 2. اكتشاف العمود الرقمي (Target)
        # لو قال "سعر"، "عدد"، "مبيعات"
        for col in self.col_roles['money_cols']:
            if self.normalize(col) in q:
                intent['target_numeric'] = col
                break

        # 3. العملية الحسابية
        if any(x in q for x in ['متوسط', 'معدل', 'avg']): intent['operation'] = 'mean'
        elif any(x in q for x in ['عدد', 'count']): intent['operation'] = 'count'
        elif any(x in q for x in ['اعلى', 'اكبر', 'اقصى', 'اكثر', 'افضل', 'top', 'max', 'best']): intent['operation'] = 'top'
        elif any(x in q for x in ['اقل', 'ادنى', 'اصغر', 'اسوا', 'min', 'worst']): intent['operation'] = 'bottom'
        elif any(x in q for x in ['تطور', 'زمن', 'trend']): intent['time_analysis'] = True

        # 4. الفلاتر (قيمة محددة)
        # هل ذكر اسم "أحمد" أو "لابتوب"؟
        words = query.split()
        for w in words:
            w_clean = self.normalize(w)
            if len(w_clean) < 2: continue
            # البحث في الفهرس
            match = process.extractOne(w_clean, self.value_index.keys(), scorer=fuzz.ratio)
            if match and match[1] >= 90: # دقة عالية جداً
                found_val = match[0]
                col_name = self.value_index[found_val]
                # استرجاع القيمة الأصلية
                original = self.df[self.df[col_name].astype(str).str.lower() == found_val].iloc[0][col_name]
                intent['filters'][col_name] = original

        return intent

    def execute(self, query):
        intent = self.understand(query)
        df_res = self.df.copy()
        
        # تطبيق الفلاتر
        for col, val in intent['filters'].items():
            df_res = df_res[df_res[col] == val]
        
        target = intent['target_numeric']
        group = intent['group_by']
        op = intent['operation']

        # لو مفيش عمود رقمي خالص
        if not target and op != 'count':
             return "⚠️ عذراً، الملف لا يحتوي على أرقام (مبيعات/سعر) لتحليلها.", None

        # السيناريو 1: أفضل / أسوأ (Top/Bottom)
        if op in ['top', 'bottom']:
            # لو مفيش تجميع محدد، نستخدم عمود المنتجات افتراضياً
            if not group: 
                group = self.col_roles['product_col']
            
            if not group: # لو لسه مفيش، ناخد أي عمود نصي
                 group = self.col_roles['text_cols'][0]

            grouped = df_res.groupby(group)[target].sum().reset_index()
            grouped = grouped.sort_values(target, ascending=(op == 'bottom'))
            
            best_item = grouped.iloc[0]
            name = best_item[group]
            val = best_item[target]
            
            txt_op = "الأكثر" if op == 'top' else "الأقل"
            msg = f"💎 **{txt_op} {group} (حسب {target}):**\n# {name}\n**القيمة:** {val:,.2f}"
            
            fig = px.bar(grouped.head(7), x=group, y=target, title=f"{txt_op} 7 {group}", color=target)
            return msg, fig

        # السيناريو 2: تحليل زمني
        if intent['time_analysis'] and self.col_roles['date_col']:
            date_col = self.col_roles['date_col']
            trend = df_res.set_index(date_col).resample('M')[target].sum().reset_index()
            msg = f"📈 **التحليل الزمني لـ {target}:**"
            fig = px.line(trend, x=date_col, y=target, markers=True)
            return msg, fig

        # السيناريو 3: سؤال عام (المجموع/المتوسط)
        val = 0
        txt = ""
        if op == 'mean': 
            val = df_res[target].mean()
            txt = "متوسط"
        elif op == 'count':
            val = len(df_res)
            txt = "عدد السجلات"
        else:
            val = df_res[target].sum()
            txt = "إجمالي"
        
        context = f" (لـ {' و '.join(intent['filters'].values())})" if intent['filters'] else ""
        return f"💰 **{txt} {target} {context}:**\n# {val:,.2f}", None


# ==========================================
# 3. واجهة التطبيق
# ==========================================
st.title("🧠 AI Genius Analyst")

# Sidebar
with st.sidebar:
    st.header("📂 رفع البيانات")
    uploaded_file = st.file_uploader("ملف Excel/CSV", type=['xlsx', 'csv'])
    if uploaded_file:
        if uploaded_file.name.endswith('.csv'): df = pd.read_csv(uploaded_file)
        else: df = pd.read_excel(uploaded_file)
        
        if 'brain' not in st.session_state or st.session_state.last_file != uploaded_file.name:
            st.session_state.brain = GeniusBrain(df)
            st.session_state.last_file = uploaded_file.name
            
            # تقرير الذكاء عن الأعمدة
            roles = st.session_state.brain.col_roles
            summary = f"""
            **✅ تم تحليل هيكل الملف بذكاء:**
            - عمود المنتجات المتوقع: `{roles['product_col']}`
            - عمود العملاء المتوقع: `{roles['customer_col']}`
            - عمود الفروع المتوقع: `{roles['location_col']}`
            - العمود الرقمي الأساسي: `{roles['money_cols'][0] if roles['money_cols'] else 'غير موجود'}`
            """
            st.session_state.messages = [{"role": "assistant", "content": f"أهلاً! {summary}\nجرب تسألني: 'أكثر منتج مبيعا' وشوف الدقة! 😉"}]
            st.rerun()
            
    if st.button("🗑️ تصفير"):
        st.session_state.messages = []
        st.rerun()

# Chat
if 'messages' not in st.session_state: st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "chart" in msg and msg["chart"]: st.plotly_chart(msg["chart"], use_container_width=True)

if prompt := st.chat_input("اسألني... (مثلاً: هات أكثر فرع حقق مبيعات)"):
    if 'brain' in st.session_state:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("جاري تحليل السؤال..."):
                response, fig = st.session_state.brain.execute(prompt)
                st.markdown(response)
                if fig: st.plotly_chart(fig, use_container_width=True)
                st.session_state.messages.append({"role": "assistant", "content": response, "chart": fig})
    else:
        st.warning("من فضلك ارفع الملف الأول.")
