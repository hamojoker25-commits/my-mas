import streamlit as st
import random
import time
import json
import os

# --- إعدادات وثوابت اللعبة ---
DATA_FILE = 'users_data.json'
MAX_LEVELS = 30
GAME_PHASES = ["MENU", "GAME", "LEVEL_SELECTION", "SETTINGS"]

# --- 1. إدارة البيانات (تحميل/حفظ ملف JSON) ---

def load_user_data():
    """تحميل بيانات المستخدمين من ملف JSON."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_user_data(data):
    """حفظ بيانات المستخدمين إلى ملف JSON."""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def initialize_user(user_id):
    """تهيئة بيانات مستخدم جديد."""
    data = load_user_data()
    if user_id not in data:
        data[user_id] = {
            "max_level": 1,
            "score": 0,
            "settings": {"language": "Arabic", "sound": True, "vibration": True},
            # يمكن إضافة "is_premium": False لاحقاً
        }
        save_user_data(data)
    return data[user_id]

# --- 2. إعداد الحالة الافتراضية للعبة ---

def setup_session_state():
    """إعداد الحالة الافتراضية عند بدء التطبيق."""
    if 'current_phase' not in st.session_state:
        st.session_state.current_phase = "MENU" # نبدأ من القائمة الرئيسية
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None # سيكون هذا معرّف جوجل أو اسم مستعار
    if 'user_data' not in st.session_state:
        st.session_state.user_data = None
    if 'current_level' not in st.session_state:
        st.session_state.current_level = 1
    if 'annoyance' not in st.session_state:
        st.session_state.annoyance = 0
    if 'target_text' not in st.session_state:
        st.session_state.target_text = "انقر الآن!"
    
# --- 3. تحديد صعوبة المستوى ---

def get_level_difficulty(level):
    """تحديد صعوبة اللعبة بناءً على المستوى."""
    # عدد الأزرار المضللة (يزيد كل 5 مستويات)
    num_cols = min(4 + (level // 5), 8) 
    
    # السرعة بالثواني (كلما كان الرقم أصغر، زادت السرعة وصعوبة النقر)
    # 0.1 يبدأ سريعاً و 0.01 يصبح جنونياً في المستوى 30
    delay = 0.1 - (level * 0.003) 
    delay = max(delay, 0.01) # لا تقل عن 0.01 ثانية
    
    return num_cols, delay

# --- 4. واجهة تسجيل الدخول (محاكاة Google Login) ---

def login_page():
    st.header("🔑 تسجيل الدخول (محاكاة Google)")
    
    # في التطبيق الحقيقي، هنا يتم توجيه المستخدم لـ Google OAuth
    user_input = st.text_input("أدخل اسم المستخدم/البريد (للتجربة):")
    
    if st.button("تسجيل الدخول / إنشاء حساب", type="primary"):
        if user_input:
            st.session_state.user_id = user_input
            st.session_state.user_data = initialize_user(user_input)
            st.session_state.logged_in = True
            st.session_state.current_phase = "MENU"
            st.success(f"مرحباً بك، {user_input}!")
            st.rerun()
        else:
            st.warning("الرجاء إدخال اسم مستخدم.")

# --- 5. واجهات التنقل الرئيسية ---

def main_menu():
    st.title("🕹️ The Shifting Button: اللعبة الجبارة")
    st.subheader(f"المستوى الحالي: {st.session_state.current_level}")
    
    # واجهة منسقة في المنتصف
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.button("🚀 بدأ اللعب", on_click=lambda: st.session_state.update(current_phase="GAME"), use_container_width=True, type="primary")
        st.button("⚙️ الإعدادات", on_click=lambda: st.session_state.update(current_phase="SETTINGS"), use_container_width=True)
        st.button("🏆 اختيار المستويات", on_click=lambda: st.session_state.update(current_phase="LEVEL_SELECTION"), use_container_width=True)
        
        st.markdown("---")
        st.info(f"أعلى مستوى تم الوصول إليه: **{st.session_state.user_data['max_level']}**")

def settings_page():
    st.header("⚙️ إعدادات اللعبة")
    
    user_settings = st.session_state.user_data['settings']

    st.subheader("إعدادات عامة")
    
    # اختيار اللغة (للتأثير البصري حالياً)
    new_lang = st.selectbox(
        "اختر اللغة:",
        ("Arabic", "English"),
        index=0 if user_settings['language'] == "Arabic" else 1
    )
    
    st.subheader("إعدادات الصوت والاهتزاز")
    
    # الصوت
    new_sound = st.checkbox("تفعيل الأصوات المزعجة 🔊", value=user_settings['sound'])
    # الاهتزاز (للتطبيق على الجوال لاحقاً)
    new_vibration = st.checkbox("تفعيل الاهتزازات المستفزة 📳", value=user_settings['vibration'])
    
    if st.button("حفظ الإعدادات", type="primary"):
        st.session_state.user_data['settings'] = {
            "language": new_lang,
            "sound": new_sound,
            "vibration": new_vibration
        }
        save_user_data(load_user_data()) # تحديث وحفظ البيانات
        st.toast("تم حفظ الإعدادات بنجاح!")
        st.session_state.current_phase = "MENU"
        st.rerun()
    
    st.button("العودة للقائمة الرئيسية", on_click=lambda: st.session_state.update(current_phase="MENU"))

def level_selection_page():
    st.header("🏆 اختيار المستويات")
    max_unlocked = st.session_state.user_data['max_level']
    
    # عرض المستويات في شبكة (3 أعمدة)
    cols = st.columns(3)
    
    for level in range(1, MAX_LEVELS + 1):
        with cols[(level - 1) % 3]:
            # إذا كان المستوى متاحاً (تم الوصول إليه أو هو المستوى التالي)
            is_unlocked = level <= max_unlocked
            
            button_label = f"المستوى {level}"
            if not is_unlocked:
                button_label += " 🔒"
                
            if st.button(button_label, key=f"select_level_{level}", disabled=not is_unlocked, use_container_width=True):
                st.session_state.current_level = level
                st.session_state.annoyance = 0 # إعادة ضبط الإحباط عند تغيير المستوى
                st.session_state.current_phase = "GAME"
                st.rerun()
    
    st.markdown("---")
    st.button("العودة للقائمة الرئيسية", on_click=lambda: st.session_state.update(current_phase="MENU"))

# --- 6. منطق اللعبة (The Shifting Button) ---

def handle_success():
    """عند النقر على الزر الصحيح."""
    current_level = st.session_state.current_level
    
    if current_level < MAX_LEVELS:
        # ترقية المستوى
        st.session_state.current_level += 1
        
        # تحديث أعلى مستوى تم الوصول إليه وحفظه
        if st.session_state.current_level > st.session_state.user_data['max_level']:
            st.session_state.user_data['max_level'] = st.session_state.current_level
            save_user_data(load_user_data()) # حفظ التقدم
            
        st.success(f"🥳 تهانينا! المستوى {current_level} مكتمل. تم الانتقال إلى المستوى {st.session_state.current_level}")
        st.balloons()
        st.session_state.annoyance = 0 # إعادة ضبط الإحباط
    else:
        st.success("🎉 لقد فزت باللعبة المستفزة كلها! أنت لست مستفزاً بعد الآن.")
        
    st.session_state.target_text = random.choice(["لا بأس، لكن حظك لن يدوم!", "أنت محظوظ!", "انقر مجدداً"])
    st.rerun()

def handle_fail():
    """عند النقر على زر خاطئ."""
    st.session_state.annoyance += 1
    st.error("أنت مخطئ! زاد إحباطك 😠!")
    st.snow()
    
    # زيادة الإحباط تزيد من صعوبة الزر المستهدف نفسه!
    if st.session_state.annoyance > 3:
        st.session_state.target_text = random.choice(["", "!", "أين أنا؟", "انقر هنا!"])
    
    # تأخير مستفز
    time.sleep(0.5) 
    st.rerun()

def game_page():
    current_level = st.session_state.current_level
    num_cols, delay = get_level_difficulty(current_level)
    
    st.title(f"🔥 المستوى {current_level} من {MAX_LEVELS}")
    st.metric(label="😡 الإحباط الحالي", value=st.session_state.annoyance)

    st.markdown(f"**الصعوبة:** يتم إنشاء {num_cols} زر. النقر يجب أن يتم في {delay:.2f} ثانية تقريباً (أمر Streamlit مستفز بطبعه).")

    # تحديد الأعمدة عشوائياً
    all_cols = st.columns(num_cols)
    target_column_index = random.randint(0, num_cols - 1)
    
    # 1. إظهار الأزرار
    for i in range(num_cols):
        with all_cols[i]:
            if i == target_column_index:
                # الزر المستهدف (الناجح)
                st.button(st.session_state.target_text, key=f"target_{current_level}_{st.session_state.annoyance}", on_click=handle_success, type="primary", use_container_width=True)
            else:
                # أزرار الخداع (الفشل)
                st.button(random.choice(["زر خاطئ", "لا تضغطني!", "خطأ", "انتظرني"]), key=f"wrong_{current_level}_{st.session_state.annoyance}_{i}", on_click=handle_fail, use_container_width=True)
    
    st.markdown("---")
    st.button("العودة للقائمة الرئيسية", on_click=lambda: st.session_state.update(current_phase="MENU"))

# --- 7. التحكم في مسار التطبيق ---

def main():
    setup_session_state()
    st.set_page_config(page_title="The Shifting Button - اللعبة الجبارة", layout="wide")

    if not st.session_state.logged_in:
        login_page()
    else:
        # عرض شريط جانبي مع معلومات اللاعب
        with st.sidebar:
            st.header("👤 ملف اللاعب")
            st.markdown(f"**المستخدم:** {st.session_state.user_id}")
            st.metric(label="أعلى مستوى تم الوصول إليه", value=st.session_state.user_data['max_level'])
            st.metric(label="اللغة الحالية", value=st.session_state.user_data['settings']['language'])
            
            if st.button("تغيير المستخدم / تسجيل الخروج"):
                st.session_state.logged_in = False
                st.session_state.user_id = None
                st.session_state.user_data = None
                st.rerun()
            
        # التنقل بين الواجهات
        if st.session_state.current_phase == "MENU":
            main_menu()
        elif st.session_state.current_phase == "GAME":
            game_page()
        elif st.session_state.current_phase == "SETTINGS":
            settings_page()
        elif st.session_state.current_phase == "LEVEL_SELECTION":
            level_selection_page()

if __name__ == "__main__":
    main()
