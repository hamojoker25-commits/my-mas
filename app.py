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
# 1. تصميم الواجهة الفخم (High-End UI)
# ==========================================
st.set_page_config(page_title="The Maestro AI", layout="wide", page_icon="🧠")

st.markdown("""
<style>
    /* خلفية الشات */
    .stChatMessage {
        padding: 1.5rem; 
        border-radius: 15px; 
        margin-bottom: 1rem; 
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.1);
    }
    /* تحسين المدخلات */
    .stChatInput {position: fixed; bottom: 20px; z-index: 1000;}
    .block-container {padding-bottom: 150px;}
    
    /* تنسيق الجداول */
    .dataframe {font-size: 14px !important;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. العقل المدبر (The Super Intelligence)
# ==========================================
class MaestroBrain:
    def __init__(self, df):
        self.df = df.copy()
        # تنظيف أسماء الأعمدة
        self.df.columns = [str(c).strip() for c in self.df.columns]
        
        # قاموس المفاهيم (عربي/إنجليزي)
        self.concepts = {
            'money': ['sales', 'price', 'amount', 'total', 'revenue', 'cost', 'profit', 'salary', 'مبيعات', 'سعر', 'اجمالي', 'مبلغ', 'ربح', 'تكلفة', 'راتب', 'قيمة'],
            'product': ['product', 'item', 'sku', 'model', 'name', 'desc', 'منتج', 'صنف', 'نوع', 'اسم', 'موديل', 'سلعة'],
            'customer': ['cust', 'client', 'buyer', 'consumer', 'عميل', 'زبون', 'مشتري'],
            'date': ['date', 'time', 'day', 'month', 'year', 'تاريخ', 'وقت', 'يوم', 'شهر', 'سنة'],
            'location': ['city', 'branch', 'region', 'country', 'مدينة', 'فرع', 'منطقة', 'دولة', 'محافظة']
        }
        
        # التشخيص الذاتي (Auto-Diagnosis)
        self.roles = self._diagnose_columns()
        self.search_index = self._build_search_index()

    def _diagnose_columns(self):
        """الذكاء الاصطناعي يحدد هوية كل عمود"""
        roles = {'numeric': [], 'date': None, 'text_cols': [], 'best_name': None, 'best_cat': None}
        
        for col in self.df.columns:
            c_lower = col.lower()
            
            # 1. اكتشاف التاريخ
            if not roles['date']:
                if pd.api.types.is_datetime64_any_dtype(self.df[col]) or any(x in c_lower for x in self.concepts['date']):
                    try:
                        self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
                        roles['date'] = col
                        continue
                    except: pass

            # 2. اكتشاف الأرقام (الفلوس/الكميات)
            if pd.api.types.is_numeric_dtype(self.df[col]):
                # نستبعد أعمدة الكود والـ ID
                if 'id' not in c_lower and 'code' not in c_lower and 'كود' not in c_lower:
                    roles['numeric'].append(col)
                continue
            
            # 3. النصوص (للتصنيف)
            roles['text_cols'].append(col)

        # ترتيب الأعمدة الرقمية بالأهمية (اللي اسمها فيه فلوس الأول)
        roles['numeric'].sort(key=lambda x: 2 if any(k in x.lower() for k in self.concepts['money']) else 1, reverse=True)
        
        # تحديد أفضل عمود للأسماء (منتج/عميل)
        for col in roles['text_cols']:
            c_lower = col.lower()
            # هل هو منتج؟
            if any(x in c_lower for x in self.concepts['product']):
                roles['best_name'] = col
                break
        
        # لو ملقاش، يدور على عميل
        if not roles['best_name']:
            for col in roles['text_cols']:
                if any(x in col.lower() for x in self.concepts['customer']):
                    roles['best_name'] = col
                    break
        
        # لو لسه ملقاش، ياخد أول عمود نصي فيه تنوع
        if not roles['best_name'] and roles['text_cols']:
             roles['best_name'] = roles['text_cols'][0]

        return roles

    def _build_search_index(self):
        """فهرسة كل كلمة في الملف عشان يفهم الفلاتر"""
        index = {}
        for col in self.roles['text_cols']:
            # نأخذ القيم الفريدة فقط
            vals = self.df[col].dropna().astype(str).unique()
            for v in vals:
                # تنظيف الكلمة
                clean_v = v.lower().strip()
                index[clean_v] = col
        return index

    def think_and_answer(self, query):
        """المخ الرئيسي: يحلل السؤال -> يقرر الاستراتيجية -> ينفذ -> يرد"""
        q = query.lower()
        
        # 1. استخراج النية (Intent Extraction)
        intent = {
            'op': 'sum', # العملية الافتراضية
            'target': self.roles['numeric'][0] if self.roles['numeric'] else None, # الهدف الرقمي
            'group': self.roles['best_name'], # التصنيف
            'filters': {},
            'chart': None
        }

        # A. العملية الحسابية
        if any(x in q for x in ['اكثر', 'اعلى', 'اكبر', 'افضل', 'top', 'max', 'best']): intent['op'] = 'top'
        elif any(x in q for x in ['اقل', 'ادنى', 'اصغر', 'اسوا', 'min', 'worst']): intent['op'] = 'bottom'
        elif any(x in q for x in ['متوسط', 'معدل', 'avg']): intent['op'] = 'mean'
        elif any(x in q for x in ['تطور', 'زمن', 'trend']): intent['op'] = 'trend'
        elif any(x in q for x in ['عدد', 'count']): intent['op'] = 'count'

        # B. هل ذكر عمود رقمي محدد؟ (مثلاً "سعر" بدل "مبيعات")
        for col in self.roles['numeric']:
            if col.lower() in q: # بحث بسيط
                intent['target'] = col
                break
            # بحث ذكي (Fuzzy)
            if fuzz.partial_ratio(col.lower(), q) > 85:
                intent['target'] = col
                break

        # C. هل ذكر تصنيف محدد؟ (مثلاً "حسب الفرع")
        for col in self.roles['text_cols']:
            if col.lower() in q or fuzz.partial_ratio(col.lower(), q) > 85:
                intent['group'] = col
                break

        # D. هل ذكر فلتر محدد؟ (مثلاً "مبيعات أحمد")
        words = q.split()
        for w in words:
            if len(w) < 2: continue
            # ندور على أقرب كلمة في الفهرس
            match = process.extractOne(w, self.search_index.keys(), scorer=fuzz.ratio)
            if match and match[1] >= 90: # دقة عالية
                val_found = match[0]
                col_found = self.search_index[val_found]
                # نجيب القيمة الأصلية
                original_val = self.df[self.df[col_found].astype(str).str.lower().str.strip() == val_found].iloc[0][col_found]
                intent['filters'][col_found] = original_val

        # ---------------- التنفيذ (Execution) ----------------
        
        # 1. تطبيق الفلاتر أولاً
        df_wk = self.df.copy()
        filter_msg = ""
        for col, val in intent['filters'].items():
            df_wk = df_wk[df_wk[col] == val]
            filter_msg += f" (لـ {val})"
            
        target = intent['target']
        group = intent['group']

        # 2. السيناريوهات
        
        # سيناريو: الترتيب (أفضل/أسوأ)
        if intent['op'] in ['top', 'bottom']:
            if not group or not target: return "محتاج عمود أسماء وعمود أرقام عشان أقدر أرتب.", None
            
            grouped = df_wk.groupby(group)[target].sum().reset_index()
            asc = (intent['op'] == 'bottom')
            grouped = grouped.sort_values(target, ascending=asc)
            
            top_item = grouped.iloc[0]
            name = top_item[group]
            val = top_item[target]
            
            emoji = "🏆" if not asc else "📉"
            txt = "الأكثر/الأعلى" if not asc else "الأقل/الأدنى"
            
            msg = f"""
            ### {emoji} {txt} {group} {filter_msg}
            هو: **{name}**
            **القيمة:** `{val:,.2f}`
            """
            
            # رسم بياني
            fig = px.bar(grouped.head(10), x=group, y=target, title=f"ترتيب الـ {group}", color=target, color_continuous_scale='Viridis')
            return msg, fig

        # سيناريو: التريند الزمني
        elif intent['op'] == 'trend':
            date_col = self.roles['date']
            if not date_col: return "للأسف مفيش عمود تاريخ في الملف عشان أعمل تحليل زمني.", None
            
            trend = df_wk.set_index(date_col).resample('M')[target].sum().reset_index()
            msg = f"### 📈 التطور الزمني لـ {target} {filter_msg}"
            fig = px.line(trend, x=date_col, y=target, markers=True)
            return msg, fig

        # سيناريو: الإجمالي/المتوسط (سؤال عام)
        else:
            if not target: return "مش لاقي عمود أرقام أحسبه.", None
            
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
            
            msg = f"""
            ### 💰 {title} {target} {filter_msg}
            # `{val:,.2f}`
            """
            
            # إضافة ذكية: توزيع البيانات
            fig = px.histogram(df_wk, x=target, title=f"توزيع قيم {target}", nbins=30)
            return msg, fig

# ==========================================
# 3. واجهة التطبيق (The App)
# ==========================================
st.title("🧠 The Maestro AI")
st.caption("مساعدك الشخصي لتحليل البيانات - يفهمك من كلمة")

# Sidebar
with st.sidebar:
    st.header("📂 ملف البيانات")
    uploaded_file = st.file_uploader("ارفع الملف واتفرج (Excel/CSV)", type=['xlsx', 'csv'])
    
    if uploaded_file:
        try:
            # قراءة قوية للملفات
            if uploaded_file.name.endswith('.xlsx'): df = pd.read_excel(uploaded_file)
            else:
                try: df = pd.read_csv(uploaded_file, encoding='utf-8')
                except: df = pd.read_csv(uploaded_file, encoding='cp1256') # عربي ويندوز
            
            # تشغيل المايسترو
            if 'maestro' not in st.session_state or st.session_state.last_file != uploaded_file.name:
                st.session_state.maestro = MaestroBrain(df)
                st.session_state.last_file = uploaded_file.name
                
                # تقرير الفهم الذاتي
                roles = st.session_state.maestro.roles
                info = f"""
                **✅ تم التحليل بنجاح!**
                - فهمت إن العمود الأساسي هو: `{roles['best_name']}`
                - وعمود الأرقام هو: `{roles['numeric'][0] if roles['numeric'] else 'لا يوجد'}`
                - وعمود التاريخ: `{roles['date'] if roles['date'] else 'لا يوجد'}`
                """
                st.session_state.messages = [{"role": "assistant", "content": f"أهلاً يا مدير 👋\n{info}\n**أنا جاهز، اسألني براحتك (مثلاً: هات مبيعات القاهرة، أو أفضل منتج).**"}]
                st.rerun()
        except Exception as e:
            st.error(f"خطأ في الملف: {e}")

    if st.button("مسح الشات 🗑️"):
        st.session_state.messages = []
        st.rerun()

# إدارة الذاكرة
if 'messages' not in st.session_state: st.session_state.messages = []
if 'maestro' not in st.session_state: st.session_state.maestro = None

# عرض الشات
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "chart" in msg and msg["chart"]:
            st.plotly_chart(msg["chart"], use_container_width=True)

# استقبال الأسئلة
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
        st.info("👈 من فضلك ارفع الملف الأول من القائمة الجانبية.")
