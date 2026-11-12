"""
Audio and Speech Synthesis Utilities for AI Mock Interviewer.
Provides browser-native Web Speech API audio playback for Streamlit.
"""

import html
from typing import Optional


def get_speech_html(text: str, autoplay: bool = False, button_label: str = "🔊 Read Question Aloud") -> str:
    """
    Generate an HTML/JS widget using the Web Speech API (window.speechSynthesis)
    to speak the provided text aloud directly in the user's browser.
    """
    clean_text = html.escape(text.replace("\n", " ").replace('"', '\\"'))
    widget_id = "speech_widget_" + str(abs(hash(text)) % 1000000)

    html_code = f"""
    <div id="{widget_id}" style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 8px 0;">
        <button id="btn_{widget_id}" onclick="toggleSpeech_{widget_id}()"
            style="
                background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 7px 16px;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer;
                display: inline-flex;
                align-items: center;
                gap: 8px;
                transition: all 0.2s ease;
                box-shadow: 0 2px 4px rgba(79, 70, 229, 0.2);
            "
            onmouseover="this.style.opacity='0.9'; this.style.transform='translateY(-1px)'"
            onmouseout="this.style.opacity='1'; this.style.transform='translateY(0)'"
        >
            <span id="icon_{widget_id}">🔊</span>
            <span id="text_{widget_id}">{button_label}</span>
        </button>

        <script>
            (function() {{
                var isSpeaking = false;
                var textToSpeak = "{clean_text}";

                window.toggleSpeech_{widget_id} = function() {{
                    if (!('speechSynthesis' in window)) {{
                        alert("Speech synthesis is not supported in this browser.");
                        return;
                    }}

                    if (window.speechSynthesis.speaking) {{
                        window.speechSynthesis.cancel();
                        setButtonState(false);
                    }} else {{
                        var utterance = new SpeechSynthesisUtterance(textToSpeak);
                        utterance.rate = 1.0;
                        utterance.pitch = 1.0;
                        utterance.lang = 'en-US';

                        utterance.onstart = function() {{
                            setButtonState(true);
                        }};
                        utterance.onend = function() {{
                            setButtonState(false);
                        }};
                        utterance.onerror = function() {{
                            setButtonState(false);
                        }};

                        window.speechSynthesis.speak(utterance);
                    }}
                }};

                function setButtonState(speaking) {{
                    var icon = document.getElementById("icon_{widget_id}");
                    var text = document.getElementById("text_{widget_id}");
                    var btn = document.getElementById("btn_{widget_id}");
                    if (speaking) {{
                        icon.innerText = "⏹️";
                        text.innerText = "Stop Reading";
                        btn.style.background = "#DC2626";
                    }} else {{
                        icon.innerText = "🔊";
                        text.innerText = "{button_label}";
                        btn.style.background = "linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%)";
                    }}
                }}

                {"window.onload = function() { toggleSpeech_" + widget_id + "(); };" if autoplay else ""}
            }})();
        </script>
    </div>
    """
    return html_code
