import streamlit as st
import pandas as pd
import telebot
import time

# إعدادات الصفحة
st.set_page_config(page_title="أدات لإرسال تنبيهات تلغرام", layout="centered")

# التنسيق المخصص (CSS) لتطابق التصميم بدقة
st.markdown("""
    <style>
    /* خلفية الصفحة الرئيسية */
    .stApp {
        background-color: #a2f05a;
    }
    
    /* اتجاه النص من اليمين إلى اليسار */
    body, div, input, textarea {
        direction: rtl;
        text-align: right;
    }

    /* العنوان الرئيسي */
    .main-title {
        background-color: #3f3f3f;
        color: white;
        text-align: center;
        font-size: 26px;
        font-weight: bold;
        padding: 12px;
        border-radius: 4px;
        margin-bottom: 25px;
    }

    /* العنوان الفرعي */
    .sub-title {
        background-color: #3f3f3f;
        color: white;
        text-align: center;
        font-size: 18px;
        font-weight: bold;
        padding: 8px 15px;
        border-radius: 4px;
        width: fit-content;
        margin-right: 0;
        margin-left: auto;
        margin-bottom: 20px;
    }

    /* العناوين المجاورة للحقول */
    .field-label {
        font-weight: bold;
        font-size: 20px;
        color: black;
        text-align: right;
        padding-top: 10px;
    }

    /* زر إرسال أحمر مع زوايا دائرية */
    div.stButton > button:first-child {
        background: linear-gradient(180deg, #ff4d4d 0%, #cc0000 100%);
        color: white;
        font-size: 24px;
        font-weight: bold;
        border: none;
        border-radius: 25px;
        padding: 10px 60px;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.3);
        display: block;
        margin: 20px auto;
        width: 60%;
    }
    div.stButton > button:first-child:hover {
        background: linear-gradient(180deg, #ff6666 0%, #990000 100%);
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# رأس الواجهة
st.markdown('<div class="main-title">أدات لإرسال تنبيهات تلغرام</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">أدخل الاشياء المطلوبة</div>', unsafe_allow_html=True)

# 1. توكن البوت
col1, col2 = st.columns([1, 3])
with col1:
    st.markdown('<div class="field-label">TOKEN</div>', unsafe_allow_html=True)
with col2:
    api_token = st.text_input("", key="token", type="password", label_visibility="collapsed")

# 2. رابط الصورة
col1, col2 = st.columns([1, 3])
with col1:
    st.markdown('<div class="field-label">رابط الصورة</div>', unsafe_allow_html=True)
with col2:
    media_url = st.text_input("", key="media", label_visibility="collapsed")

# 3. إختر ملف الاكسل
col1, col2 = st.columns([1, 3])
with col1:
    st.markdown('<div class="field-label">إختر ملف الاكسل</div>', unsafe_allow_html=True)
with col2:
    uploaded_file = st.file_uploader("", type=["xlsx", "xls"], key="excel", label_visibility="collapsed")

# 4. الرسالة
col1, col2 = st.columns([1, 3])
with col1:
    st.markdown('<div class="field-label">الرسالة</div>', unsafe_allow_html=True)
with col2:
    message_text = st.text_area("", height=120, key="msg", label_visibility="collapsed")

# زر إرسال
send_btn = st.button("إرسال")

# نافذة إظهار سير العملية في الأسفل
st.markdown("---")
st.markdown("**سير العملية:**")
log_area = st.empty()

# منطق التشغيل والإرسال
if send_btn:
    if not api_token:
        st.error("❌ يرجى إدخال TOKEN البوت!")
    elif uploaded_file is None:
        st.error("❌ يرجى اختيار ملف الاكسل!")
    elif not message_text:
        st.error("❌ يرجى إدخال نص الرسالة!")
    else:
        try:
            bot = telebot.TeleBot(api_token)
            df = pd.read_excel(uploaded_file)

            if 'chat_id' not in df.columns:
                st.error("❌ ملف الاكسل يجب أن يحتوي على عمود اسمه 'chat_id'")
            else:
                total_users = len(df)
                logs = [f"بدء الإرسال إلى {total_users} مشترك..."]
                log_area.code("\n".join(logs))

                success = 0
                failed = 0

                for idx, chat_id in enumerate(df['chat_id'], start=1):
                    try:
                        if media_url and media_url.strip():
                            clean_url = media_url.strip()
                            if clean_url.lower().endswith(".mp4"):
                                bot.send_video(chat_id=chat_id, caption=message_text, video=clean_url)
                            else:
                                bot.send_photo(chat_id=chat_id, caption=message_text, photo=clean_url)
                        else:
                            bot.send_message(chat_id=chat_id, text=message_text)

                        success += 1
                        logs.append(f"[{idx}/{total_users}] تم الإرسال بنجاح -> {chat_id}")
                    except Exception as e:
                        failed += 1
                        logs.append(f"[{idx}/{total_users}] فشل الإرسال -> {chat_id} (السبب: {e})")

                    # تحديث نافذة سير العملية مباشر
                    log_area.code("\n".join(logs[-8:]))
                    time.sleep(0.05)

                st.success(f"اكتمل الإرسال! النجاح: {success} | الفشل: {failed}")

        except Exception as e:
            st.error(f"حدث خطأ أثناء التشغيل: {str(e)}")
