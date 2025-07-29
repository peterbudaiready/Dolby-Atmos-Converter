import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load Webhook URL from .env or Streamlit secrets
load_dotenv()
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Stripe Payment URL
STRIPE_PAYMENT_LINK = "https://buy.stripe.com/28E9AM5UVg9Og5Oe3F18c00"

# Page Config and Styling
st.set_page_config(page_title="Dolby Atmos Conversion", layout="centered")
st.markdown("""
    <style>
        html, body, [class*="css"]  {
            background-color: white;
            color: black;
            font-family: 'Segoe UI', sans-serif;
        }
        .stButton button {
            background-color: black;
            color: white;
            padding: 0.75rem 2rem;
            border: none;
            border-radius: 12px;
            font-size: 1rem;
        }
        .stButton button:hover {
            background-color: #333333;
        }
        .block-container {
            max-width: 700px;
        }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("Dolby Atmos Conversion")

# Session state to manage button visibility
if "webhook_done" not in st.session_state:
    st.session_state.webhook_done = False

if not st.session_state.webhook_done:
    # Form UI
    with st.form("conversion_form", clear_on_submit=False):
        uploaded_files = st.file_uploader("Upload Audio Files (WAV or MP3):", type=["wav", "mp3"], accept_multiple_files=True)
        email = st.text_input("Your Email")
        st.caption("Note: please include your email where you want to receive your Dolby Atmos Files.")

        quality = st.slider("Mix wideness (immersion)", 0, 100, 50)
        st.caption("""
            100% means severely wide mix with some of main tracks overlapping in the back of audio space, 50% is a standard Mix when main instruments/objects are focused more in the front and additional background instruments are placed on the sides/back/above listener.
        """)

        output_format = st.multiselect("Output Format:", [
            "2.0 Stereo", "Binaural", "5.1 Surround", "7.1.4 Surround", "ADM BWF (Dolby Atmos file)"
        ])

        content_type = st.multiselect("Content Type:", [
            "Music content", "Sound design content", "Other content"
        ])

        submitted = st.form_submit_button("Convert")

    # Submission Logic
    if submitted:
        if not uploaded_files or not email:
            st.warning("Please fill all required fields.")
            st.stop()

        with st.spinner("Uploading and triggering conversion..."):
            # Prepare file and data payload
            files_payload = [("audioFiles", (f.name, f, f.type)) for f in uploaded_files]
            data_payload = {
                "email": email,
                "mix_wideness": str(quality),
                "output_formats": ",".join(output_format),
                "content_types": ",".join(content_type)
            }

            try:
                response = requests.post(WEBHOOK_URL, data=data_payload, files=files_payload)
                if response.ok:
                    st.success("Form submitted successfully to Dolby Atmos Webhook!")
                    st.session_state.webhook_done = True
                    st.experimental_rerun()
                else:
                    st.error(f"Webhook submission failed: {response.status_code}")
                    st.stop()
            except Exception as e:
                st.error(f"Webhook error: {e}")
                st.stop()
else:
    st.success("Conversion completed. Proceed to payment.")

    if st.button("Go to Payment"):
        st.markdown(f"""
            <script>
                window.location.href = "{STRIPE_PAYMENT_LINK}";
            </script>
            <p>Redirecting to payment... <a href="{STRIPE_PAYMENT_LINK}" target="_blank">Click here if not redirected.</a></p>
        """, unsafe_allow_html=True)
