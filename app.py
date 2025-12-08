import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import time

# --- 1. إعدادات الصفحة والتصميم ---
st.set_page_config(page_title="مدير المهام الاحترافي", page_icon="✅", layout="wide")

# تخصيص CSS بسيط لتحسين المظهر
st.markdown("""
<style>
    .stProgress > div > div > div > div {
        background-color: #4CAF50;
    }
    .task-card {
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
        border: 1px solid #eee;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. إدارة الحالة (Session State) ---
# لضمان حفظ المهام عند تحديث الصفحة
if 'tasks' not in st.session_state:
    st.session_state['tasks'] = []

# --- 3. الوظائف المساعدة ---
def add_task(name, time_obj, category, priority):
    st.session_state['tasks'].append({
        "Task": name,
        "Time": time_obj,
        "Category": category,
        "Priority": priority,
        "Completed": False,
        "ID": time.time() # معرف فريد
    })

def delete_task(index):
    del st.session_state['tasks'][index]

def toggle_complete(index):
    st.session_state['tasks'][index]['Completed'] = not st.session_state['tasks'][index]['Completed']

# --- 4. الشريط الجانبي (إضافة المهام) ---
with st.sidebar:
    st.header("📝 إضافة مهمة جديدة")
    
    with st.form("add_task_form", clear_on_submit=True):
        task_name = st.text_input("اسم المهمة")
        task_time = st.time_input("وقت المهمة", datetime.now())
        task_cat = st.selectbox("التصنيف", ["عمل", "شخصي", "صحة", "تطوير", "أخرى"])
        task_prio = st.select_slider("الأولوية", options=["منخفضة", "متوسطة", "عالية"])
        
        submitted = st.form_submit_button("إضافة للمحفظة")
        
        if submitted and task_name:
            add_task(task_name, task_time, task_cat, task_prio)
            st.success("تمت الإضافة بنجاح!")
        elif submitted and not task_name:
            st.warning("الرجاء كتابة اسم المهمة.")

    st.markdown("---")
    st.caption("برمجة بواسطة المساعد الذكي © 2024")

# --- 5. الواجهة الرئيسية ---
st.title("✅ لوحة التحكم اليومية")
st.markdown(f"**تاريخ اليوم:** {datetime.now().strftime('%Y-%m-%d')}")

# حساب نسبة الإنجاز
total_tasks = len(st.session_state['tasks'])
completed_tasks = len([t for t in st.session_state['tasks'] if t['Completed']])
progress = (completed_tasks / total_tasks) if total_tasks > 0 else 0

# عرض شريط التقدم
st.metric("نسبة الإنجاز اليومي", f"{int(progress * 100)}%")
st.progress(progress)

st.markdown("---")

# تقسيم الشاشة إلى تبويبات (Tabs)
tab1, tab2, tab3 = st.tabs(["📋 قائمة المهام", "📅 الجدول الزمني", "📊 الإحصائيات"])

# --- التبويب 1: قائمة المهام (List View) ---
with tab1:
    if not st.session_state['tasks']:
        st.info("لا توجد مهام اليوم. ابدأ بإضافة مهام من القائمة الجانبية!")
    else:
        # فرز المهام بحيث تظهر غير المكتملة أولاً
        sorted_tasks = sorted(st.session_state['tasks'], key=lambda x: x['Completed'])
        
        for i, task in enumerate(st.session_state['tasks']):
            # تصميم كارت لكل مهمة
            col1, col2, col3, col4, col5 = st.columns([0.5, 4, 2, 1.5, 1])
            
            with col1:
                # Checkbox للإنهاء
                is_checked = st.checkbox("", value=task['Completed'], key=f"check_{task['ID']}", on_change=toggle_complete, args=(i,))
            
            with col2:
                # تطبيق الشطب (Strikethrough)
                if task['Completed']:
                    st.markdown(f"~~**{task['Task']}**~~")
                else:
                    st.markdown(f"**{task['Task']}**")
            
            with col3:
                st.caption(f"🕒 {task['Time'].strftime('%I:%M %p')}")
                
            with col4:
                # ألوان للأولوية
                color = "red" if task['Priority'] == "عالية" else "orange" if task['Priority'] == "متوسطة" else "green"
                st.markdown(f":{color}[{task['Priority']}]")
            
            with col5:
                if st.button("🗑️", key=f"del_{task['ID']}"):
                    delete_task(i)
                    st.rerun()
            
            st.markdown("<hr style='margin: 5px 0; opacity: 0.2'>", unsafe_allow_html=True)

# --- التبويب 2: الجدول الزمني (Timeline) ---
with tab2:
    if st.session_state['tasks']:
        # تحويل البيانات لـ DataFrame
        df = pd.DataFrame(st.session_state['tasks'])
        df['Time'] = df['Time'].apply(lambda x: x.strftime('%H:%M'))
        df['Status'] = df['Completed'].apply(lambda x: 'منجزة' if x else 'قيد الانتظار')
        
        # ترتيب الجدول حسب الوقت
        df_sorted = df.sort_values(by="Time")
        
        st.dataframe(
            df_sorted[['Time', 'Task', 'Category', 'Priority', 'Status']],
            use_container_width=True,
            column_config={
                "Time": "التوقيت",
                "Task": "المهمة",
                "Category": "التصنيف",
                "Priority": "الأولوية",
                "Status": "الحالة"
            }
        )
    else:
        st.info("أضف مهام لعرض الجدول الزمني.")

# --- التبويب 3: الإحصائيات (Analytics) ---
with tab3:
    if st.session_state['tasks']:
        col_a, col_b = st.columns(2)
        
        df_stats = pd.DataFrame(st.session_state['tasks'])
        
        with col_a:
            st.subheader("المهام حسب التصنيف")
            fig_cat = px.pie(df_stats, names='Category', title='توزيع المهام حسب النوع')
            st.plotly_chart(fig_cat, use_container_width=True)
            
        with col_b:
            st.subheader("المهام حسب الأولوية")
            fig_prio = px.bar(df_stats, x='Priority', color='Priority', title='عدد المهام لكل أولوية')
            st.plotly_chart(fig_prio, use_container_width=True)
    else:
        st.info("لا توجد بيانات كافية للتحليل.")

