import streamlit as st
import google.generativeai as genai
import speech_recognition as sr
from gtts import gTTS
import json
import os
from PIL import Image
from googletrans import Translator

# إعداد الـ API الخاص بـ Google Gemini
genai.configure(api_key="AIzaSyCW-aA_qEVinV6DGeiwGLuKy-ygh_fu25s")

# تعريف التعليمات الخاصة بالشات بوت
AGRICULTURAL_INSTRUCTIONS = """أنت مساعد الآلي مهمتك هي الرد على استفسارات العملاء عن الأشياء في المجال الزراعي ولا تستطيع توفير معلومات أخرى."""

# دالة لاستدعاء Gemini للرد على استفسارات المستخدم
def get_bot_response(prompt):
    model = genai.GenerativeModel(model_name='gemini-pro')
    full_prompt = f"{AGRICULTURAL_INSTRUCTIONS} \nUser's question: {prompt}"
    response = model.generate_content(full_prompt)
    return response.text.strip()

# دالة معالجة الصور باستخدام Gemini Pro Vision
def get_image_response(prompt, image):
    model = genai.GenerativeModel('gemini-pro-vision')
    full_prompt = f"{AGRICULTURAL_INSTRUCTIONS} \nUser's question: {prompt}"
    response = model.generate_content([full_prompt, image])
    return response.text.strip()

# دالة الترجمة
def translate_text(text, target_lang):
    lang_map = {"الإنجليزية": "en", "الفرنسية": "fr", "الإسبانية": "es"}
    translator = Translator()
    translation = translator.translate(text, dest=lang_map[target_lang])
    return translation.text

# دالة لتخزين المحادثات في ملف JSON
def save_conversation(user_input, bot_response):
    conversation = {"user": user_input, "bot": bot_response}
    
    if not os.path.exists("conversations.json"):
        with open("conversations.json", "w", encoding='utf-8') as file:
            json.dump([], file)
    
    with open("conversations.json", "r", encoding='utf-8') as file:
        try:
            conversations = json.load(file)
        except json.JSONDecodeError:
            conversations = []
    
    conversations.append(conversation)
    
    with open("conversations.json", "w", encoding='utf-8') as file:
        json.dump(conversations, file, ensure_ascii=False, indent=4)

# دالة لتحويل النص إلى صوت
def text_to_speech(text):
    tts = gTTS(text=text, lang='ar')
    tts.save("response.mp3")
    os.system("start response.mp3")

# دالة لتحويل الصوت إلى نص
def speech_to_text():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("تكلم الآن...")
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio, language="ar-SA")
            return text
        except sr.UnknownValueError:
            return "لم يتم التعرف على الصوت"
        except sr.RequestError:
            return "خطأ في الاتصال بخدمة التعرف على الصوت"

# تحسين واجهة المستخدم باستخدام Streamlit
st.set_page_config(page_title="شات بوت غزة", page_icon="🌿", layout="centered")

# تصميم الصفحة
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@500&display=swap');

.header {
    background: linear-gradient(45deg, #4B0082, #6A5ACD);
    padding: 2rem;
    border-radius: 15px;
    text-align: center;
    color: white;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    margin-bottom: 2rem;
    font-family: 'Tajawal', sans-serif;
}

.chat-container {
    border: 2px solid #6A5ACD40;
    border-radius: 10px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    background: black;
}

.upload-wrapper {
    position: relative;
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 1rem;
}

.chat-input {
    flex: 1;
    border: 2px solid #6A5ACD !important;
    border-radius: 25px !important;
    padding: 0.8rem 1.5rem !important;
    font-family: 'Tajawal', sans-serif !important;
    padding-right: 50px !important;
    transition: all 0.3s ease !important;
}

.chat-input:focus {
    box-shadow: 0 0 15px rgba(106, 90, 205, 0.3) !important;
}

.paperclip-btn {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    margin: 0 !important;
}

.paperclip-icon {
    font-size: 28px !important;
    color: #6A5ACD !important;
    cursor: pointer;
    transition: all 0.3s ease !important;
}

.paperclip-icon:hover {
    transform: rotate(-45deg) scale(1.1);
    color: #4B0082 !important;
}

.image-preview {
    border: 2px dashed #6A5ACD;
    border-radius: 15px;
    padding: 1rem;
    margin: 1rem 0;
    text-align: center;
}

.uploaded-image {
    max-width: 250px;
    border-radius: 10px;
    margin: 0 auto;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.stRadio > div {
    flex-direction: row-reverse;
    gap: 1rem;
    margin-bottom: 1.5rem;
}
</style>
""", unsafe_allow_html=True)

# هيكل الصفحة
st.markdown("""
<div class="header">
    <h1>🌿 شات بوت الزراعي الذكي</h1>
    <p>اسأل عن أي شيء في المجال الزراعي</p>
</div>
""", unsafe_allow_html=True)

# قسم الإدخال الرئيسي
input_mode = st.radio("", ["📝 نص", "🎤 صوت"], horizontal=True, label_visibility="collapsed")

if input_mode == "🎤 صوت":
    if st.button("بدء التسجيل الصوتي", use_container_width=True):
        user_input = speech_to_text()
        if user_input and user_input != "لم يتم التعرف على الصوت":
            with st.spinner("جاري المعالجة..."):
                bot_response = get_bot_response(user_input)
                st.markdown(f"""
                <div class='chat-container'>
                    <p><strong>سؤالك:</strong> {user_input}</p>
                    <p><strong>الرد:</strong> {bot_response}</p>
                </div>
                """, unsafe_allow_html=True)
                save_conversation(user_input, bot_response)
                if st.checkbox("تشغيل الرد صوتياً", key="voice"):
                    text_to_speech(bot_response)

if input_mode == "📝 نص":
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # تصميم حقل الإدخال مع مشبك الورق
    st.markdown('<div class="upload-wrapper">', unsafe_allow_html=True)
    
    # زر الرفع المخصص
    uploaded_image = st.file_uploader(
        "📎",
        type=['png', 'jpg', 'jpeg'],
        label_visibility="collapsed",
        key="image_uploader",
        accept_multiple_files=False,
    )
    
    # حقل الإدخال النصي
    user_input = st.text_input(" ", 
                             placeholder="أكتب سؤالك هنا أو أرفق صورة...", 
                             label_visibility="collapsed",
                             key="chat_input")
    
    st.markdown('</div>', unsafe_allow_html=True)

    # معاينة الصورة المرفوعة
    if uploaded_image:
        try:
            st.markdown('<div class="image-preview">', unsafe_allow_html=True)
            image = Image.open(uploaded_image)
            st.image(image, caption="الصورة المرفوعة", use_column_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        except Exception as e:
            st.error("حدث خطأ في معالجة الصورة")

    # قسم الترجمة
    translate_col, lang_col = st.columns([2, 3])
    with translate_col:
        translate_check = st.checkbox("🌐 ترجمة الرد")
    with lang_col:
        target_lang = st.selectbox("اللغة:", ["الإنجليزية", "الفرنسية", "الإسبانية"], disabled=not translate_check)
    
    if st.button("🚀 إرسال", use_container_width=True):
        if user_input or uploaded_image:
            with st.spinner("جاري توليد الرد..."):
                if uploaded_image:
                    image = Image.open(uploaded_image)
                    bot_response = get_image_response(user_input, image)
                else:
                    bot_response = get_bot_response(user_input)
                
                if translate_check:
                    translated = translate_text(bot_response, target_lang)
                    st.success(f"الترجمة: {translated}")
                
                st.markdown(f"""
                <div class='chat-container'>
                    <p><strong>سؤالك:</strong> {user_input}</p>
                    <p><strong>الرد:</strong> {bot_response}</p>
                </div>
                """, unsafe_allow_html=True)
                save_conversation(user_input, bot_response)
                
                if st.checkbox("تشغيل الرد صوتياً", key="tts"):
                    text_to_speech(bot_response)
        else:
            st.warning("الرجاء إدخال سؤال أو رفع صورة أولاً")
    
    st.markdown('</div>', unsafe_allow_html=True)

# عرض المحادثات السابقة
if st.button("عرض المحادثات السابقة", use_container_width=True):
    if os.path.exists("conversations.json"):
        with open("conversations.json", "r", encoding='utf-8') as file:
            try:
                conversations = json.load(file)
                for convo in reversed(conversations[-5:]):
                    with st.expander(f"محادثة {conversations.index(convo)+1}", expanded=False):
                        st.markdown(f"""
                        <div class='chat-container'>
                            <p><strong>السؤال:</strong> {convo['user']}</p>
                            <p><strong>الرد:</strong> {convo['bot']}</p>
                        </div>
                        """, unsafe_allow_html=True)
            except json.JSONDecodeError:
                st.warning("الملف تالف أو غير قابل للقراءة")
    else:
        st.info("لا يوجد محفوظات حتى الآن")