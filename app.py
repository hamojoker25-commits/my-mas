import streamlit as st
import random
import time
import json
import os
import hashlib
from typing import Dict, Any

# --- الثوابت والإعدادات ---
DATA_FILE = 'user_accounts.json'
MAX_LEVELS = 30
GAME_PHASES = ["LOGIN", "MENU", "GAME", "SETTINGS", "LEVEL_SELECTION"]

# --- 1. دوال إدارة البيانات والأمان ---

def load_accounts() -> Dict[str, Any]:
    """تحميل حسابات المستخدمين من ملف JSON."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {} # إذا كان الملف تالفاً
    return {}

def save_accounts(accounts: Dict[str, Any]):
    """حفظ حسابات المستخدمين إلى ملف JSON."""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(accounts, f, indent=4, ensure_ascii=False)

def hash_password(password: str) -> str:
    """تشفير كلمة المرور باستخدام SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def initialize_user_game_data() -> Dict[str, Any]:
    """تهيئة بيانات اللعبة لمستخدم جديد."""
    return {
        "max_level": 1,
        "current_level": 1,
        "annoyance": 0,
        "settings": {"language": "Arabic", "sound": True, "vibration": True},
        "is_premium": False
    }

# --- 2. إعداد الحالة الافتراضية والواجهة الأنيقة ---

def setup_session_state():
    """إعداد الحالة الافتراضية عند بدء التطبيق."""
    if 'current_phase' not in st.session_state:
        st.session_state.current_phase = "LOGIN"
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None
    if 'user_data' not in st.session_state:
        st.session_state.user_data = None
    if 'target_text' not in st.session_state:
        st.session_state.target_text = "انقر الآن!"

def apply_custom_css():
    """تطبيق CSS لجعل الواجهة أنيقة ومركزة."""
    st.markdown("""
        <style>
        /* توسيط المحتوى الرئيسي وإضافة خلفية بسيطة */
        .stApp {
            text-align: center;
        }
        /* توسيط جميع العناوين والأزرار في المنتصف */
        .css-1d391kg, .css-1y48h67 {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        /* تنسيق الأزرار الرئيسية لتبدو أكبر وأجمل */
        div.stButton > button {
            width: 250px;
            height: 50px;
            font-size: 18px;
            margin: 10px 0;
            border-radius: 10px;
        }
        /* تنسيق الأزرار المستفزة داخل اللعبة */
        .game-button button {
            width: 100%;
            height: 40px;
            font-size: 14px;
            margin: 5px 0;
        }
        </style>
    """, unsafe_allow_html=True)
    st.title("🕹️ The Shifting Button: اللعبة الجبارة")
    
# --- 3. واجهة تسجيل الدخول الشبه واقعية ---

def login_page():
    st.header("🔑 تسجيل الدخول / إنشاء حساب")
    
    # استخدام حاوية لتجميع عناصر تسجيل الدخول لتظهر كـ "فورم"
    with st.container(border=True):
        email = st.text_input("البريد الإلكتروني:", key="login_email")
        password = st.text_input("كلمة السر:", type="password", key="login_pass")
        
        # لتحديد الوضع: تسجيل دخول أو إنشاء حساب
        mode = st.radio("الوضع:", ("تسجيل الدخول", "إنشاء حساب جديد"), index=0, horizontal=True)

        if mode == "إنشاء حساب جديد":
            confirm_password = st.text_input("تأكيد كلمة السر:", type="password", key="confirm_pass")

            if st.button("إنشاء الحساب", type="primary"):
                accounts = load_accounts()
                if not email or not password or not confirm_password:
                    st.error("الرجاء ملء جميع الحقول.")
                elif password != confirm_password:
                    st.error("كلمة السر وتأكيدها غير متطابقتين.")
                elif len(password) < 6:
                    st.error("يجب أن تكون كلمة السر ٦ أحرف على الأقل.")
                elif email in accounts:
                    st.warning("هذا البريد مسجل بالفعل. حاول تسجيل الدخول.")
                else:
                    # تنفيذ إنشاء الحساب (شبه واقعي)
                    accounts[email] = {
                        "password": hash_password(password),
                        "game_data": initialize_user_game_data()
                    }
                    save_accounts(accounts)
                    st.success("🎉 تم إنشاء الحساب بنجاح! يمكنك الآن تسجيل الدخول.")
                    
        else: # وضع تسجيل الدخول
            if st.button("تسجيل الدخول", type="primary"):
                accounts = load_accounts()
                hashed_password = hash_password(password)
                
                if email in accounts and accounts[email]['password'] == hashed_password:
                    st.session_state.user_email = email
                    st.session_state.user_data = accounts[email]['game_data']
                    st.session_state.logged_in = True
                    st.session_state.current_phase = "MENU"
                    st.rerun()
                else:
                    st.error("البريد الإلكتروني أو كلمة السر غير صحيحة.")

# --- 4. القائمة الرئيسية الأنيقة ---

def main_menu():
    st.header("✨ القائمة الرئيسية ✨")
    
    data = st.session_state.user_data
    current_level = data.get('current_level', 1)
    max_level = data.get('max_level', 1)
    
    # عرض المستوى الحالي في واجهة جذابة
    st.info(f"👤 **المستخدم:** {st.session_state.user_email} | 🏆 **المستوى الحالي:** {current_level} | 🚀 **أعلى مستوى:** {max_level}")

    # ترتيب الأزرار في المنتصف
    st.button("🚀 بدأ اللعب", on_click=lambda: st.session_state.update(current_phase="GAME"))
    st.button("🏆 اختيار المستويات", on_click=lambda: st.session_state.update(current_phase="LEVEL_SELECTION"))
    st.button("⚙️ الإعدادات", on_click=lambda: st.session_state.update(current_phase="SETTINGS"))
    
    st.markdown("---")
    
    if st.button("تسجيل الخروج", type="secondary"):
        st.session_state.logged_in = False
        st.session_state.user_email = None
        st.session_state.user_data = None
        st.session_state.current_phase = "LOGIN"
        st.rerun()

# --- 5. منطق اللعبة الصعبة والمستفزة ---

def get_difficulty(level: int) -> tuple:
    """تحديد صعوبة اللعبة (عدد الأزرار، احتمالية التغيير)."""
    # عدد الأزرار المضللة (يزيد كل 5 مستويات)
    num_cols = min(4 + (level // 5), 8) 
    # احتمالية تغيير موقع الزر الخاطئ إلى زر صحيح (كلما زادت النسبة زادت الصعوبة)
    misdirection_chance = min(0.1 + (level * 0.005), 0.3) 
    
    return num_cols, misdirection_chance

def update_user_game_data(field: str, value: Any):
    """دالة مساعدة لحفظ البيانات وتحديثها."""
    st.session_state.user_data[field] = value
    
    accounts = load_accounts()
    accounts[st.session_state.user_email]['game_data'] = st.session_state.user_data
    save_accounts(accounts)

def handle_click(is_correct: bool):
    current_level = st.session_state.user_data['current_level']
    annoyance = st.session_state.user_data['annoyance']
    
    if is_correct:
        # النجاح
        if current_level < MAX_LEVELS:
            new_level = current_level + 1
            update_user_game_data('current_level', new_level)
            if new_level > st.session_state.user_data['max_level']:
                update_user_game_data('max_level', new_level)
            
            update_user_game_data('annoyance', 0) # إعادة ضبط الإحباط
            st.toast(f"🥳 المستوى {current_level} مكتمل! المستوى التالي: {new_level}")
            st.balloons()
        else:
            st.success("🎉 لقد فزت باللعبة المستفزة كلها!")
            
    else:
        # الفشل وزيادة الإحباط
        new_annoyance = annoyance + 1
        update_user_game_data('annoyance', new_annoyance)
        
        st.error("❌ أنت مخطئ! زاد إحباطك 😠!")
        
        # منطق الصعوبة الإضافية: عند ارتفاع الإحباط، يتغير نص الزر الصحيح بشكل مربك
        if new_annoyance > 3:
            st.session_state.target_text = random.choice(["لا تنقر هنا!", "هذا ليس صحيحاً", "خادع!"])
        else:
            st.session_state.target_text = "انقر هنا الآن!"

        # إعادة تشغيل الكود لرسم الأزرار في موقع جديد ومربك
        time.sleep(0.3) # تأخير مستفز
    st.rerun()


def game_page():
    current_level = st.session_state.user_data['current_level']
    annoyance = st.session_state.user_data['annoyance']
    num_cols, misdirection_chance = get_difficulty(current_level)
    
    st.header(f"🔥 المستوى {current_level} من {MAX_LEVELS}")
    
    # عرض الإحصائيات في عمودين
    col_a, col_b = st.columns(2)
    col_a.metric(label="😡 الإحباط الحالي", value=annoyance)
    col_b.metric(label="🔄 عدد الأزرار المضللة", value=num_cols - 1)
    
    st.markdown("---")
    
    # --- منطقة الأزرار المربكة ---
    
    # استخدام الأعمدة لتوزيع الأزرار أفقياً (العمود الأول فارغ للمنتصف)
    all_cols = st.columns(num_cols + 2) 
    
    # تحديد الموقع العشوائي للزر الصحيح ضمن الأعمدة
    target_column_index = random.randint(1, num_cols) 
    
    # قائمة نصوص الأزرار الخادعة
    wrong_texts = ["زر خاطئ", "لا تضغطني", "خداع بصري", "أين هو؟", "غير متاح"]
    
    for i in range(1, num_cols + 1):
        with all_cols[i]:
            is_correct = (i == target_column_index)
            
            if is_correct:
                # الزر المستهدف
                button_text = st.session_state.target_text
                st.button(button_text, 
                          key=f"target_{current_level}_{annoyance}", 
                          on_click=lambda: handle_click(True), 
                          type="primary", 
                          use_container_width=True)
            else:
                # الأزرار الخادعة
                
                # *** الصعوبة الإضافية: الزر الخادع يمكن أن يغير مظهره ليصبح "صحيحاً" للحظة (الخداع) ***
                if random.random() < misdirection_chance:
                    button_text = "انقر هنا!" # نص شبه صحيح للخداع
                    button_type = "primary" # لون شبه صحيح للخداع
                else:
                    button_text = random.choice(wrong_texts)
                    button_type = "secondary"

                # إضافة الزر
                # استخدام class 'game-button' لتنسيق CSS المخصص
                st.markdown(f'<div class="game-button">', unsafe_allow_html=True)
                st.button(button_text, 
                          key=f"wrong_{current_level}_{annoyance}_{i}", 
                          on_click=lambda: handle_click(False), 
                          type=button_type, 
                          use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.button("العودة للقائمة الرئيسية", on_click=lambda: st.session_state.update(current_phase="MENU"), key="back_from_game")

# --- 6. صفحة الإعدادات والمستويات (مختصرة) ---

def settings_page():
    st.header("⚙️ إعدادات اللعبة")
    
    settings = st.session_state.user_data['settings']

    st.subheader("إعدادات عامة")
    
    new_lang = st.selectbox("اختر اللغة:", ("Arabic", "English"), index=0 if settings['language'] == "Arabic" else 1)
    
    st.subheader("إعدادات الصوت والاهتزاز")
    
    new_sound = st.checkbox("تفعيل الأصوات المزعجة 🔊", value=settings['sound'])
    new_vibration = st.checkbox("تفعيل الاهتزازات المستفزة 📳", value=settings['vibration'])
    
    if st.button("حفظ الإعدادات", type="primary"):
        st.session_state.user_data['settings'] = {
            "language": new_lang,
            "sound": new_sound,
            "vibration": new_vibration
        }
        update_user_game_data('settings', st.session_state.user_data['settings']) # حفظ
        st.toast("تم حفظ الإعدادات بنجاح!")
        st.session_state.current_phase = "MENU"
        st.rerun()
    
    st.button("العودة للقائمة الرئيسية", on_click=lambda: st.session_state.update(current_phase="MENU"))

def level_selection_page():
    st.header("🏆 اختيار المستويات")
    max_unlocked = st.session_state.user_data['max_level']
    
    st.info(f"يمكنك البدء من أي مستوى تصل إليه. أعلى مستوى مفتوح: **{max_unlocked}**")
    
    # عرض المستويات في شبكة (4 أعمدة)
    cols = st.columns(4)
    
    for level in range(1, MAX_LEVELS + 1):
        col_index = (level - 1) % 4
        with cols[col_index]:
            is_unlocked = level <= max_unlocked
            button_label = f"المستوى {level}"
            
            if st.button(button_label, key=f"select_level_{level}", disabled=not is_unlocked, use_container_width=True):
                update_user_game_data('current_level', level)
                update_user_game_data('annoyance', 0)
                st.session_state.current_phase = "GAME"
                st.rerun()
    
    st.markdown("---")
    st.button("العودة للقائمة الرئيسية", on_click=lambda: st.session_state.update(current_phase="MENU"))

# --- 7. التحكم في مسار التطبيق (Main Flow) ---

def main():
    setup_session_state()
    st.set_page_config(page_title="The Shifting Button - اللعبة الجبارة", layout="wide")
    apply_custom_css() # تطبيق التنسيق الأنيق

    if not st.session_state.logged_in:
        login_page()
    else:
        # شريط جانبي لعرض معلومات المستخدم بشكل أنيق
        with st.sidebar:
            st.header(f"👤 مرحباً بك، {st.session_state.user_email.split('@')[0]}!")
            st.metric(label="أعلى مستوى تم الوصول إليه", value=st.session_state.user_data['max_level'])
            st.metric(label="المستوى الحالي للعب", value=st.session_state.user_data['current_level'])
            
            # زر إخفاء الشريط لترك مساحة أكبر للعبة
            if st.button("إخفاء الشريط الجانبي ➡️"):
                st.sidebar.markdown(f'<style>section[data-testid="stSidebar"] {{visibility: hidden;}}</style>', unsafe_allow_html=True)
            
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
