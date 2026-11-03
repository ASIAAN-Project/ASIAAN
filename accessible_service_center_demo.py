
import streamlit as st
from urllib.parse import quote_plus

st.set_page_config(
    page_title="ASIAAN Accessible Service Center Search",
    page_icon="♿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# DEMO DATA
# Replace this section with the real ASIAAN dataset/API after
# the layout is reviewed.
# ============================================================

SERVICE_GROUPS = {
    "Home & Community Services": [
        "Home Repair",
        "Transportation",
        "Senior Centers",
        "Home Delivered Meals",
        "Congregate Meals",
        "Adult Day Service",
        "Home Health Services",
    ],
    "Health & Wellness": [
        "Senior Exercise Programs",
        "Dementia Support",
        "Mental Health",
        "Vaccinations",
        "Hospice Care",
        "Health Education Workshops",
    ],
    "Financial & Legal Assistance": [
        "Benefits Counseling",
        "Financial Counseling",
        "Long Term Care Ombudsman",
        "Case Management",
        "Immigration Assistance",
    ],
    "Housing, Care & Social Engagement": [
        "Elderly Housing Resources",
        "Assisted Living",
        "Long Term Care Nursing Homes",
        "Elder Abuse Support",
        "Caregiver Support Services",
        "Cultural Programs",
        "Technology Training",
    ],
}

LANGUAGES = [
    "English",
    "Arabic",
    "Hindi",
    "Urdu",
    "Cantonese",
    "Mandarin",
    "Chinese",
    "Spanish",
]

# Short demo descriptions. Replace/expand these with the wording
# approved for the production ASIAAN site.
SERVICE_INFO = {
    "Home Repair": "Help related to home repair or maintenance needs.",
    "Transportation": "Transportation support or transportation-related services.",
    "Senior Centers": "Programs or services offered through senior centers.",
    "Home Delivered Meals": "Meals delivered to a person's home.",
    "Congregate Meals": "Meals provided in a shared community setting.",
    "Adult Day Service": "Daytime programs and support for older adults.",
    "Home Health Services": "Health-related services provided in the home.",
    "Senior Exercise Programs": "Exercise or physical activity programs for older adults.",
    "Dementia Support": "Support for people living with dementia and their caregivers.",
    "Mental Health": "Mental health support or related services.",
    "Vaccinations": "Vaccination information or services.",
    "Hospice Care": "Hospice and end-of-life care support.",
    "Health Education Workshops": "Workshops or classes about health topics.",
    "Benefits Counseling": "Help understanding or applying for available benefits.",
    "Financial Counseling": "Help with financial questions or planning.",
    "Long Term Care Ombudsman": "Support related to long-term care rights and concerns.",
    "Case Management": "Help coordinating services and support needs.",
    "Immigration Assistance": "Help with immigration-related services or resources.",
    "Elderly Housing Resources": "Housing information or resources for older adults.",
    "Assisted Living": "Assisted-living information or services.",
    "Long Term Care Nursing Homes": "Nursing-home or long-term-care information and services.",
    "Elder Abuse Support": "Support related to elder abuse, neglect, or exploitation.",
    "Caregiver Support Services": "Support and resources for caregivers.",
    "Cultural Programs": "Cultural or community programs.",
    "Technology Training": "Help learning to use computers, phones, or other technology.",
}

CENTERS = [
    {
        "name": "Xilin Association",
        "address": "2538 S Blue Island Ave, Chicago, IL 60608, USA",
        "city": "Chicago",
        "zip": "60608",
        "phone": "773-741-4743",
        "languages": ["Mandarin", "Cantonese", "Spanish", "English"],
        "website": "https://xilin.org/",
        "services": [
            "Adult Day Service",
            "Transportation",
            "Senior Centers",
        ],
    },
    {
        "name": "ECCOA Ombudsman Program",
        "address": "209 S Merchant St, Effingham, IL 62401, USA",
        "city": "Effingham",
        "zip": "62401",
        "phone": "800-283-4070",
        "languages": ["English"],
        "website": "https://theconsumervoice.org/",
        "services": [
            "Long Term Care Ombudsman",
            "Transportation",
            "Case Management",
            "Financial Counseling",
        ],
    },
    {
        "name": "Chinese Mutual Aid Association",
        "address": "1016 W Argyle St, Chicago, IL 60640, USA",
        "city": "Chicago",
        "zip": "60640",
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
        "city": "Chicago",
        "zip": "60659",
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

# ============================================================
# ACCESSIBILITY / READABILITY STYLES
# ============================================================

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1250px;
        padding-top: 1.3rem;
        padding-bottom: 4rem;
    }

    html, body, [class*="css"] {
        font-size: 20px;
    }

    h1 {
        font-size: 2.55rem !important;
        line-height: 1.2 !important;
    }

    h2 {
        font-size: 1.95rem !important;
        line-height: 1.25 !important;
        margin-top: 1.8rem !important;
    }

    h3 {
        font-size: 1.45rem !important;
        line-height: 1.3 !important;
    }

    p, li {
        font-size: 1.05rem !important;
        line-height: 1.65 !important;
    }

    div[data-testid="stTextInput"] label p,
    div[data-testid="stCheckbox"] label p,
    div[data-testid="stSelectbox"] label p {
        font-size: 1.05rem !important;
    }

    div[data-testid="stTextInput"] label p,
    div[data-testid="stSelectbox"] label p {
        font-weight: 800 !important;
    }

    div[data-baseweb="input"] input {
        min-height: 52px;
        font-size: 1.05rem !important;
    }

    div[data-testid="stCheckbox"] {
        padding: .12rem 0;
    }

    div[data-testid="stCheckbox"] label {
        min-height: 44px;
        align-items: center;
    }

    div[data-testid="stButton"] button,
    div[data-testid="stLinkButton"] a {
        min-height: 54px;
        font-size: 1rem !important;
        font-weight: 750 !important;
    }

    *:focus-visible {
        outline: 4px solid #2B83D4 !important;
        outline-offset: 3px !important;
    }

    .intro-box {
        border-left: 7px solid #2B83D4;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin: .6rem 0 1.4rem 0;
        background: rgba(43,131,212,.09);
        line-height: 1.65;
    }

    .review-note {
        border: 2px solid rgba(128,128,128,.35);
        border-radius: 12px;
        padding: .9rem 1rem;
        margin-bottom: 1.5rem;
        background: rgba(128,128,128,.06);
    }

    .filter-group {
        border: 1px solid rgba(128,128,128,.30);
        border-radius: 14px;
        padding: 1rem 1.1rem;
        margin-bottom: 1rem;
        background: rgba(128,128,128,.035);
    }

    .filter-group-title {
        font-size: 1.25rem;
        font-weight: 850;
        margin-bottom: .5rem;
    }

    .filter-help {
        margin: -.1rem 0 .45rem 2rem;
        opacity: .82;
        font-size: .95rem;
        line-height: 1.45;
    }

    .selected-summary {
        border: 1px solid rgba(128,128,128,.35);
        border-radius: 12px;
        padding: .9rem 1rem;
        margin: 1rem 0;
        background: rgba(128,128,128,.05);
    }

    .result-card {
        border: 1px solid rgba(128,128,128,.35);
        border-radius: 16px;
        padding: 1.2rem 1.3rem;
        margin: 1rem 0 1.6rem 0;
        background: rgba(128,128,128,.035);
    }

    .info-box {
        border: 1px solid rgba(128,128,128,.28);
        border-radius: 12px;
        padding: .85rem 1rem;
        margin: .65rem 0;
    }

    .small-note {
        opacity: .78;
        font-size: .95rem;
        line-height: 1.5;
    }

    @media (max-width: 900px) {
        html, body, [class*="css"] {
            font-size: 18px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# HELPERS
# ============================================================

def clear_all():
    st.session_state["search_text"] = ""
    st.session_state["location_text"] = ""
    st.session_state["distance"] = "Any distance"

    for items in SERVICE_GROUPS.values():
        for service in items:
            st.session_state[f"service::{service}"] = False

    for language in LANGUAGES:
        st.session_state[f"language::{language}"] = False


def get_selected_services():
    selected = []
    for items in SERVICE_GROUPS.values():
        for service in items:
            if st.session_state.get(f"service::{service}", False):
                selected.append(service)
    return selected


def get_selected_languages():
    return [
        language
        for language in LANGUAGES
        if st.session_state.get(f"language::{language}", False)
    ]


def matches_search(center, query):
    query = query.strip().lower()
    if not query:
        return True

    searchable = " ".join(
        [
            center["name"],
            center["address"],
            center["phone"],
            center["city"],
            center["zip"],
            " ".join(center["languages"]),
            " ".join(center["services"]),
        ]
    ).lower()

    return query in searchable


def matches_location(center, location_query):
    location_query = location_query.strip().lower()
    if not location_query:
        return True

    searchable = " ".join(
        [center["address"], center["city"], center["zip"]]
    ).lower()

    return location_query in searchable


def matches_services(center, selected_services):
    if not selected_services:
        return True

    available = set(center["services"])
    return all(service in available for service in selected_services)


def matches_languages(center, selected_languages):
    if not selected_languages:
        return True

    available = set(center["languages"])
    return any(language in available for language in selected_languages)


# ============================================================
# PAGE INTRODUCTION
# ============================================================

st.title("Accessible Service Center Search")

st.markdown(
    """
    <div class="intro-box">
    This page is a non-map alternative to the ASIAAN map. It is designed so a user can
    search, filter, and read service-center information without needing to see or interpret
    map pins.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="review-note">
    <strong>Demo for review:</strong> This page shows the planned accessible layout.
    It uses sample records for now. The production version can later connect to the full ASIAAN dataset.
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# 1. SEARCH
# ============================================================

st.header("1. Search")

search_text = st.text_input(
    "Search by service center name, address, language, or service",
    key="search_text",
    placeholder="Example: Xilin, transportation, Mandarin, or Chicago",
    help="The results update automatically as you type.",
)

# ============================================================
# 2. LOCATION
# ============================================================

st.header("2. Location")

st.write(
    "Enter a city, ZIP code, or address. The production version can use this "
    "location together with the selected distance."
)

location_col1, location_col2 = st.columns([1.5, 1], gap="large")

with location_col1:
    location_text = st.text_input(
        "City, ZIP code, or address",
        key="location_text",
        placeholder="Example: Chicago or 60608",
    )

with location_col2:
    distance = st.selectbox(
        "Distance",
        ["Any distance", "1 mile", "5 miles", "10 miles", "25 miles"],
        key="distance",
    )

st.markdown(
    """
    <div class="small-note">
    In this demo, the city/ZIP/address text filters the sample records.
    The distance selector is shown for layout review. The production version can calculate real distance using geocoded locations.
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# 3. SERVICE FILTERS
# ============================================================

st.header("3. Filter by service")

st.write(
    "Each service is presented as its own labeled checkbox. The short description "
    "is placed directly with that service so a screen-reader user does not have to "
    "move through a separate column of information icons."
)

for group_name, services in SERVICE_GROUPS.items():
    st.markdown('<div class="filter-group">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="filter-group-title">{group_name}</div>',
        unsafe_allow_html=True,
    )

    for service in services:
        st.checkbox(
            service,
            key=f"service::{service}",
            help=SERVICE_INFO.get(service, ""),
        )

        st.markdown(
            f'<div class="filter-help">'
            f'<strong>About this service:</strong> '
            f'{SERVICE_INFO.get(service, "Service information will be added here.")}'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# 4. LANGUAGE FILTERS
# ============================================================

st.header("4. Filter by language")

st.write(
    "Choose one or more languages. A service center is included when it supports "
    "at least one of the selected languages."
)

language_cols = st.columns(2, gap="large")

for index, language in enumerate(LANGUAGES):
    with language_cols[index % 2]:
        st.checkbox(
            language,
            key=f"language::{language}",
        )

# ============================================================
# 5. CURRENT SELECTIONS
# ============================================================

services = get_selected_services()
languages = get_selected_languages()

st.header("5. Current selections")

summary_lines = []

if search_text.strip():
    summary_lines.append(f'Search: "{search_text.strip()}"')

if location_text.strip():
    summary_lines.append(f'Location: "{location_text.strip()}"')

if distance != "Any distance":
    summary_lines.append(f"Distance: {distance}")

if services:
    summary_lines.append("Services: " + ", ".join(services))

if languages:
    summary_lines.append("Languages: " + ", ".join(languages))

if summary_lines:
    st.markdown(
        '<div class="selected-summary">' +
        "<br>".join(summary_lines) +
        "</div>",
        unsafe_allow_html=True,
    )
else:
    st.write("No search or filters are currently selected.")

st.button(
    "Clear search and all filters",
    on_click=clear_all,
)

# ============================================================
# 6. RESULTS
# ============================================================

results = [
    center
    for center in CENTERS
    if matches_search(center, search_text)
    and matches_location(center, location_text)
    and matches_services(center, services)
    and matches_languages(center, languages)
]

st.header("6. Service center results")

if len(results) == 1:
    st.write("1 service center found.")
else:
    st.write(f"{len(results)} service centers found.")

if not results:
    st.warning(
        "No demo service centers match the current search and filters. "
        "Clear one or more selections and try again."
    )

for index, center in enumerate(results, start=1):
    st.markdown('<div class="result-card">', unsafe_allow_html=True)

    st.subheader(f"{index}. {center['name']}")

    st.markdown(
        f"""
        <div class="info-box">
        <strong>Location</strong><br>
        {center["address"]}
        </div>
        """,
        unsafe_allow_html=True,
    )

    maps_query = quote_plus(center["address"])

    google_maps_url = (
        "https://www.google.com/maps/search/"
        f"?api=1&query={maps_query}"
    )

    apple_maps_url = f"https://maps.apple.com/?q={maps_query}"

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.link_button(
            f"Get directions to {center['name']} with Google Maps",
            google_maps_url,
            use_container_width=True,
        )

    with col2:
        st.link_button(
            f"Get directions to {center['name']} with Apple Maps",
            apple_maps_url,
            use_container_width=True,
        )

    phone_digits = "".join(
        character for character in center["phone"] if character.isdigit()
    )

    st.markdown(
        f"""
        <div class="info-box">
        <strong>Phone</strong><br>
        <a href="tel:{phone_digits}">{center["phone"]}</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="info-box">
        <strong>Languages</strong><br>
        {", ".join(center["languages"])}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="info-box">
        <strong>Website</strong><br>
        <a href="{center["website"]}" target="_blank">
        Visit {center["name"]} website
        </a>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Services provided")

    for service in center["services"]:
        st.markdown(f"- {service}")

    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# REVIEW NOTES
# ============================================================

st.header("Planned production version")

st.write(
    "After this layout is reviewed, the page can be connected to the real ASIAAN data "
    "and tested with NVDA, keyboard-only navigation, browser zoom, and WAVE."
)

st.markdown(
    """
    The production version can add:

    - the complete ASIAAN service-center dataset
    - real distance/radius filtering
    - all fields available to users on the ArcGIS map
    - pagination for large result sets
    - PDF download
    - transportation information in a text-based format
    - final accessibility fixes identified during NVDA and WAVE testing
    """
)
