import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import paho.mqtt.client as paho
import json

st.set_page_config(
    page_title="Control por Voz",
    page_icon="🎙️",
    layout="centered"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Mulish:wght@400;700&display=swap');

html, body, .stApp {
    background: linear-gradient(to bottom right, #ffe5ec, #ffc8dd);
    color: #2c2c2c;
    font-family: 'Mulish', sans-serif;
    text-align: center;
}

h1, h2, h3, .stTitle, .stHeader {
    color: #d63384;
    text-align: center;
}

.stButton>button {
    background-color: #d63384;
    color: white;
    font-weight: bold;
    border-radius: 10px;
    padding: 0.6em 1.2em;
    border: none;
}

.stImage > img {
    display: block;
    margin-left: auto;
    margin-right: auto;
}

.bk-root .bk-btn {
    background-color: #ff69b4 !important;
    color: white !important;
    font-weight: bold;
    border-radius: 10px;
    font-size: 16px;
    padding: 8px 16px;
}

.block-container {
    padding-left: 5%;
    padding-right: 5%;
}
</style>
""", unsafe_allow_html=True)

def on_publish(client, userdata, result):
    print("✅ El dato ha sido publicado\n")
    pass

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.success("📩 Mensaje recibido:")
    st.code(message_received)

broker = "157.230.214.127"
port = 1883
client1 = paho.Client("Isis123")
client1.on_message = on_message

st.title("🎙️ Interfaces Multimodales")
st.subheader("✨ Control de dispositivos por voz")

image = Image.open('voice_ctrl.jpg')
st.image(image, width=200)

st.markdown("Toca el botón para comenzar a hablar 🎧")

stt_button = Button(label="🎤 Iniciar reconocimiento de voz", width=280)
stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
 
    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value !== "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
"""))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

if result:
    if "GET_TEXT" in result:
        st.write("🔊 Lo que dijiste:")
        st.success(result.get("GET_TEXT"))
        client1.on_publish = on_publish
        client1.connect(broker, port)
        message = json.dumps({"Act1": result.get("GET_TEXT").strip()})
        ret = client1.publish("controlvoz", message)

    try:
        os.mkdir("temp")
    except:
        pass
