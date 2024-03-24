import streamlit as st
import pyaudio
import base64
import json
import requests
from streamlit_chat import message as st_message

token_hugging_face = "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"

headers = {"Authorization": f"Bearer {token_hugging_face}"}
API_URL_RECOGNITION = "https://api-inference.huggingface.co/models/openai/whisper-tiny.en"
API_URL_DIAGNOSTIC = "https://api-inference.huggingface.co/models/abhirajeshbhai/symptom-2-disease-net"

def record_audio(seconds=5, sample_rate=44100, channels=2, chunk_size=1024):
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16,
                        channels=channels,
                        rate=sample_rate,
                        input=True,
                        frames_per_buffer=chunk_size)

    st.info(f"Recording audio for {seconds} seconds...")
    frames = []
    for _ in range(int(sample_rate / chunk_size * seconds)):
        data = stream.read(chunk_size)
        frames.append(data)

    st.info("Recording finished!")
    stream.stop_stream()
    stream.close()
    audio.terminate()

    audio_data = b''.join(frames)
    audio_data_base64 = base64.b64encode(audio_data).decode('utf-8')  # Convert to base64
    return audio_data_base64, sample_rate

def recognize_speech(audio_data, sample_rate):
    with st.spinner("Speech recognition in progress..."):
        data = {"file": audio_data, "sample_rate": sample_rate}
        response = requests.post(API_URL_RECOGNITION, headers=headers, json=data)
        output = response.json()
        final_output = output.get('text', 'Speech recognition failed: Text not found in response')
    return final_output

def diagnostic_medic(voice_text):
    synthomps = {"inputs": voice_text}
    data = json.dumps(synthomps)

    with st.spinner("Medical diagnosis in progress..."):
        response = requests.post(API_URL_DIAGNOSTIC, headers=headers, data=data)
        try:
            output = response.json()
            # Check if the response contains the expected structure
            if isinstance(output, list) and output and isinstance(output[0], list) and output[0]:
                final_output = output[0][0].get('label', 'Unknown')
            else:
                final_output = "Unknown"
        except json.JSONDecodeError as e:
            final_output = "Unknown"
            st.error(f"Error decoding JSON response: {e}")
    return final_output

def generate_answer(audio_data, sample_rate):
    text = recognize_speech(audio_data, sample_rate)
    diagnostic = diagnostic_medic(text)

    st.session_state.history.append({"message": text, "is_user": True})
    st.session_state.history.append({"message": f"Your disease would be {diagnostic}", "is_user": False})

    st.success("Medical consultation done")

if __name__ == "__main__":
    hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
        </style>
        """
    st.markdown(hide_menu_style, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.write(' ')

    with col2:
        st.image("./logo_.png", width=200)

    with col3:
        st.write(' ')

    if "history" not in st.session_state:
        st.session_state.history = []

    st.title("Medical Diagnostic Assistant")


    st.write("Click the 'Start Recording' button to record audio:")
    if st.button("Start Recording"):
        audio_data, sample_rate = record_audio()
        generate_answer(audio_data, sample_rate)

        for i, chat in enumerate(st.session_state.history):
            st_message(**chat, key=str(i))
