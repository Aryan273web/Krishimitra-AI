import streamlit as st
import requests

st.set_page_config(
    page_title="KrishiMitra AI",
    page_icon="🌾",
    layout="centered"
)

st.title("🌾 KrishiMitra (कृषि मित्र)")
st.caption("Autonomous Multilingual Mandi Assistant for Farmers")

# Chat history initialization
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "assistant",
            "content": "Namaste! Speak or type in any language. I will automatically detect your language and respond! / नमस्ते! अपनी भाषा में बोलें या लिखें, कृषि मित्र उत्तर देगा।"
        }
    ]

# Display prior chat messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Voice Input Widget (Browser Auto-Detect Speech Recognition)
st.markdown("---")
st.markdown("### 🎙️ Autonomous Voice Search")

voice_html = """
<div style="display: flex; gap: 10px; align-items: center; font-family: sans-serif; margin-bottom: 10px;">
    <button id="start-btn" onclick="startDictation()" style="background-color: #2e7d32; color: white; border: none; padding: 12px 20px; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 16px;">
        🎤 Press & Speak (बोलना शुरू करें)
    </button>
    <span id="speech-status" style="font-size: 14px; color: #555;">Press button and speak in your native language...</span>
</div>

<script>
function startDictation() {
    if (window.hasOwnProperty('webkitSpeechRecognition') || window.hasOwnProperty('SpeechRecognition')) {
        var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        var recognition = new SpeechRecognition();

        recognition.continuous = false;
        recognition.interimResults = false;

        // Auto-detect browser/OS device primary speech locale fallback to hi-IN
        var userDeviceLangs = navigator.languages || [navigator.language || 'hi-IN'];
        recognition.lang = userDeviceLangs[0];

        document.getElementById('speech-status').innerText = "Listening... / सुन रहे हैं...";
        recognition.start();

        recognition.onresult = function(e) {
            var transcript = e.results[0][0].transcript;
            document.getElementById('speech-status').innerText = "Captured: " + transcript;
            
            // Auto-inject captured spoken text directly into Streamlit input
            var chatInput = window.parent.document.querySelector('textarea[data-testid="stChatInputTextArea"]');
            if (chatInput) {
                chatInput.value = transcript;
                chatInput.dispatchEvent(new Event('input', { bubbles: true }));
            }
            recognition.stop();
        };

        recognition.onerror = function(e) {
            document.getElementById('speech-status').innerText = "Voice input stopped or canceled.";
            recognition.stop();
        };
    } else {
        alert("Web Speech API is not supported in this browser. Please use Chrome or Edge.");
    }
}
</script>
"""

st.components.v1.html(voice_html, height=80)

# User Input Box
if prompt := st.chat_input("Speak or type... e.g., 'उत्तर प्रदेश में आलू का भाव क्या है?' or 'What is wheat rate in Punjab?'"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    backend_url = "http://127.0.0.1:8000/api/chat-text"
    
    with st.chat_message("assistant"):
        with st.spinner("KrishiMitra is detecting language and checking mandi prices..."):
            try:
                response = requests.post(
                    backend_url,
                    json={"user_input": prompt},
                    timeout=45
                )
                if response.status_code == 200:
                    data = response.json()
                    bot_reply = data.get("response", "No response text found.")
                else:
                    bot_reply = f"Error: Server responded with status {response.status_code}"
            except Exception as e:
                bot_reply = f"Could not connect to backend server: {str(e)}"
            
            st.write(bot_reply)
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})