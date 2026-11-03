import streamlit as st
from urllib.parse import quote_plus

st.set_page_config(
    page_title="ASIAAN Accessible Service Center Demo",
    page_icon="♿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -------------------------------------------------------------------
# Demo data only
# -------------------------------------------------------------------
CENTERS = [
    {
        "name": "ECCOA Ombudsman Program",
        "address": "209 S Merchant St, Effingham, IL 62401, USA",
        "phone": "800-283-4070",
        "languages": ["English"],
        "website": "https://theconsumervoice.org/",
        "services": [
            "Long-term Care Ombudsman",
            "Transportation",
            "Case Management",
            "Financial Counseling",
        ],
    },
    {
        "name": "Xilin Association",
        "address": "2538 S Blue Island Ave, Chicago, IL 60608, USA",
        "phone": "773-741-4743",
        "languages": ["Mandarin", "Cantonese", "Spanish", "English"],
        "website": "https://xilin.org/",
        "services": [
            "Adult Day Services",
            "Transportation",
            "Senior Centers",
        ],
    },
    {
        "name": "Chinese Mutual Aid Association",
        "address": "1016 W Argyle St, Chicago, IL 60640, USA",
        "phone": "773-784-2900",
        "languages": ["English", "Mandarin", "Cantonese"],
        "website": "https://www.chinesemutualaid.org/",
        "services": [
            "Benefits Counseling",
            "Immigration Assistance",
            "Senior Centers",
        ],
    },
    {
        "name": "Indo-American Center",
        "address": "6328 N California Ave, Chicago, IL 60659, USA",
        "phone": "773-973-4444",
        "languages": ["English", "Hindi", "Urdu"],
        "website": "https://indoamerican.org/",
        "services": [
            "Immigration Assistance",
            "Benefits Counseling",
            "Technology Training",
        ],
    },
]

ALL_SERVICES = sorted(
    {service for center in CENTERS for service in center["services"]}
)

ALL_LANGUAGES = sorted(
    {language for center in CENTERS for language in center["languages"]}
)

# -------------------------------------------------------------------
# Accessibility-focused visual styling
# -------------------------------------------------------------------
st.markdown(
    """
    <style>
    .block-container {
        max-width: 1100px;
        padding-top: 1.5rem;
        padding-bottom: 4rem;
    }

    html, body, [class*="css"] {
        font-size: 20px;
    }

    h1 {
        font-size: 2.5rem !important;
        line-height: 1.2 !important;
    }

    h2 {
        font-size: 1.9rem !important;
