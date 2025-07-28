# app.py
import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load API keys from .env or Streamlit secrets
load_dotenv()
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY")
STRIPE_PRODUCT_ID = os.getenv("STRIPE_PRODUCT_ID")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

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

st.title("Dolby Atmos Conversion")

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

if submitted:
    if not uploaded_files or not email:
        st.warning("Please fill all required fields.")
        st.stop()

    with st.spinner("Uploading and triggering conversion..."):
        files_payload = [("audioFiles", (f.name, f, f.type)) for f in uploaded_files]
        data_payload = {
            "email": email,
            "quality": str(quality),
        }
        for fmt in output_format:
            data_payload.setdefault("outputFormat", []).append(fmt)
        for ctype in content_type:
            data_payload.setdefault("contentType", []).append(ctype)

        try:
            response = requests.post(WEBHOOK_URL, data=data_payload, files=files_payload)
            if response.ok:
                st.success("Form submitted successfully to Dolby Atmos Webhook!")
            else:
                st.error(f"Webhook submission failed: {response.status_code}")
        except Exception as e:
            st.error(f"Webhook error: {e}")

    with st.spinner("Redirecting to payment..."):
        checkout_payload = {
            "payment_method_types[]": "card",
            "line_items[0][price]": STRIPE_PRODUCT_ID,
            "mode": "payment",
            "success_url": "https://yourdomain.com/success",
            "cancel_url": "https://yourdomain.com/cancel"
        }
        headers = {
            "Authorization": f"Bearer {STRIPE_SECRET_KEY}"
        }
        try:
            r = requests.post("https://api.stripe.com/v1/checkout/sessions", data=checkout_payload, headers=headers)
            r.raise_for_status()
            checkout_url = r.json().get("url")
            st.markdown(f"[Click here to complete your payment]({checkout_url})")
        except Exception as e:
            st.error(f"Payment setup failed: {e}")
