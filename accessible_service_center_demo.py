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
        line-height: 1.25 !important;
        margin-top: 1.8rem !important;
    }

    h3 {
        font-size: 1.5rem !important;
        line-height: 1.3 !important;
    }

    p, li {
        font-size: 1.05rem !important;
        line-height: 1.65 !important;
    }

    div[data-testid="stTextInput"] label p,
    div[data-testid="stMultiSelect"] label p {
        font-size: 1.1rem !important;
        font-weight: 700 !important;
    }

    div[data-baseweb="input"] input {
        min-height: 48px;
        font-size: 1.05rem !important;
    }

    div[data-testid="stMultiSelect"] > div {
        min-height: 50px;
    }

    div[data-testid="stLinkButton"] a {
        min-height: 52px;
        font-size: 1.05rem !important;
        font-weight: 700 !important;
    }

    *:focus-visible {
        outline: 3px solid #1f77b4 !important;
        outline-offset: 3px !important;
    }

    .intro-note {
        border-left: 6px solid #1f77b4;
        padding: 1rem 1.1rem;
        margin: 1rem 0 1.5rem 0;
        background: rgba(31,119,180,.08);
        border-radius: 8px;
        font-size: 1.03rem;
        line-height: 1.6;
    }

    .center-divider {
        margin: 1.5rem 0;
        border-top: 2px solid rgba(128,128,128,.35);
    }

    @media (max-width: 800px) {
        html, body, [class*="css"] {
            font-size: 18px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------------------------
# Page introduction
# -------------------------------------------------------------------
st.title("Accessible Service Center List")

st.markdown(
    """
    <div class="intro-note">
        This is a demonstration of a non-map version of the ASIAAN service-center search.
        It is designed so a user can search, filter, and read service-center information
        without needing to interpret map pins.
    </div>
    """,
    unsafe_allow_html=True,
)

st.write(
    "Use the search and filters below. The controls use visible labels, "
    "and the results are presented as headings and text so they can be "
    "navigated with a keyboard or screen reader."
)

# -------------------------------------------------------------------
# Search and filters
# -------------------------------------------------------------------
st.header("Find service centers")

search_text = st.text_input(
    "Search by service center name, address, language, or service",
    placeholder="Example: transportation, Mandarin, Xilin, or Chicago",
    help=(
        "Type any word that may appear in the center name, address, "
        "language list, or service list."
    ),
)

selected_services = st.multiselect(
    "Filter by service",
    options=ALL_SERVICES,
    placeholder="Choose one or more services",
    help=(
        "When more than one service is selected, this demo shows centers "
        "that provide all selected services."
    ),
)

selected_languages = st.multiselect(
    "Filter by language",
    options=ALL_LANGUAGES,
    placeholder="Choose one or more languages",
    help=(
        "A center is included when it supports at least one of the "
        "selected languages."
    ),
)

# -------------------------------------------------------------------
# Filtering helpers
# -------------------------------------------------------------------
def matches_search(center, query):
    query = query.strip().lower()

    if not query:
        return True

    searchable_text = " ".join(
        [
            center["name"],
            center["address"],
            center["phone"],
            " ".join(center["languages"]),
            " ".join(center["services"]),
        ]
    ).lower()

    return query in searchable_text


def matches_services(center, selected):
    if not selected:
        return True

    center_services = set(center["services"])
    return all(service in center_services for service in selected)


def matches_languages(center, selected):
    if not selected:
        return True

    center_languages = set(center["languages"])
    return any(language in center_languages for language in selected)


results = [
    center
    for center in CENTERS
    if matches_search(center, search_text)
    and matches_services(center, selected_services)
    and matches_languages(center, selected_languages)
]

# -------------------------------------------------------------------
# Results
# -------------------------------------------------------------------
st.header("Service center results")

if len(results) == 1:
    st.write("1 service center found.")
else:
    st.write(f"{len(results)} service centers found.")

if not results:
    st.warning(
        "No service centers match the current search and filters. "
        "Remove a filter or try another search word."
    )
else:
    for index, center in enumerate(results, start=1):
        st.subheader(f"{index}. {center['name']}")

        st.markdown(f"**Location:** {center['address']}")

        maps_query = quote_plus(center["address"])

        google_maps_url = (
            "https://www.google.com/maps/search/"
            f"?api=1&query={maps_query}"
        )

        apple_maps_url = f"https://maps.apple.com/?q={maps_query}"

        col1, col2 = st.columns(2)

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
            character
            for character in center["phone"]
            if character.isdigit()
        )

        st.markdown(
            f"**Phone:** [{center['phone']}](tel:{phone_digits})"
        )

        st.markdown(
            f"**Languages:** {', '.join(center['languages'])}"
        )

        st.markdown(
            f"**Website:** "
            f"[Visit {center['name']} website]({center['website']})"
        )

        st.markdown("### Services provided")

        for service in center["services"]:
            st.markdown(f"- {service}")

        if index < len(results):
            st.markdown(
                '<div class="center-divider"></div>',
                unsafe_allow_html=True,
            )

# -------------------------------------------------------------------
# Reviewer explanation
# -------------------------------------------------------------------
st.header("What this demo is showing")

st.write(
    "The purpose of this page is to demonstrate an accessible alternative "
    "to the map. A clearly labeled button at the top of the ArcGIS page "
    "could open a page like this for users who prefer or need a text-based "
    "experience."
)

st.markdown(
    """
    The final version could later add:

    - the complete ASIAAN service-center dataset
    - all service and language filters
    - location or ZIP-code filtering
    - pagination for large result sets
    - PDF download
    - additional accessibility testing with NVDA, keyboard-only navigation, and WAVE
    """
)

st.caption(
    "Demo only. The service-center records on this page are sample data "
    "used to show the planned interaction."
)
