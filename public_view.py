import html
import os
import re
import unicodedata
from math import ceil
from urllib.parse import quote_plus

import pandas as pd
import requests
import streamlit as st
from fpdf import FPDF

# -----------------------------------------------------------------------------
# Page + ArcGIS config
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Service Center Details",
    page_icon="🏢",
    layout="wide",
)

FEATURE_LAYER_URL = st.secrets["ARCGIS_FEATURE_LAYER"]
PAGE_SIZE = 5

# These are the service fields already used by main.py in the ASIAAN project.
SERVICE_FIELDS = [
    ("Home_Health_Services", "Home Health Services"),
    ("Adult_Day_Services", "Adult Day Services"),
    ("Benefits_Counseling", "Benefits Counseling"),
    ("Elder_Housing_Resources", "Elder Housing Resources"),
    ("Assisted_Living", "Assisted Living"),
    ("Elder_Abuse", "Elder Abuse"),
    ("Home_Repair", "Home Repair"),
    ("Immigration_Assistance", "Immigration Assistance"),
    ("Long_term_Care_Ombudsman", "Long-term Care Ombudsman"),
    ("Long_term_Care_Nursing_Homes", "Long-term Care / Nursing Homes"),
    ("Senior_Exercise_Programs", "Senior Exercise Programs"),
    ("Dementia_Support_Programs", "Dementia Support Programs"),
    ("Transportation", "Transportation"),
    ("Senior_Centers", "Senior Centers"),
    ("Caregiver_Support_Services", "Caregiver Support Services"),
    ("Case_Management", "Case Management"),
    ("Congregate_Meals", "Congregate Meals"),
    ("Financial_Counseling", "Financial Counseling"),
    ("Health_Education_Workshops", "Health Education Workshops"),
    ("Home_Delivered_Meals", "Home Delivered Meals"),
    ("Hospice_Care", "Hospice Care"),
    ("Technology_Training", "Technology Training"),
    ("Cultural_Programming", "Cultural Programming"),
    ("Mental_Health", "Mental Health"),
    ("Vaccinations_Screening", "Vaccinations / Screening"),
    ("Outreach_and_Advocacy", "Outreach and Advocacy"),
    ("Lending_Closet", "Lending Closet"),
    ("Independent_Living", "Independent Living"),
    ("Homemakers_Personal_Support", "Homemakers / Personal Support"),
    ("Independent_Housing", "Independent Housing"),
    ("Energy_Assistance", "Energy Assistance"),
    ("Adult_Guardianship", "Adult Guardianship"),
]

# -----------------------------------------------------------------------------
# Accessibility / readability
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
      .block-container {
        max-width: 1100px;
        padding-top: 2rem;
        padding-bottom: 3rem;
      }
      html, body, [class*="css"] {
        font-size: 18px;
      }
      h1 {
        font-size: 2.1rem !important;
        line-height: 1.2 !important;
      }
      h2, h3 {
        line-height: 1.3 !important;
      }
      p, li, label {
        line-height: 1.55 !important;
      }
      div[data-testid="stButton"] button,
      div[data-testid="stLinkButton"] a,
      div[data-testid="stDownloadButton"] button {
        min-height: 50px;
        font-size: 1rem;
        font-weight: 600;
      }
      .phone-link {
        font-size: 1.08rem;
        font-weight: 700;
        text-decoration: underline;
      }
      .result-count {
        font-size: 1.05rem;
        margin-bottom: 0.5rem;
      }
      .location-box,
      .contact-box {
        border: 1px solid rgba(128, 128, 128, 0.35);
        background: rgba(128, 128, 128, 0.08);
        border-radius: 12px;
        padding: 16px 18px;
        margin: 0.7rem 0 1rem 0;
      }
      .field-label {
        font-size: 0.82rem;
        font-weight: 800;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        opacity: 0.78;
        margin-bottom: 0.35rem;
      }
      .field-value {
        font-size: 1.13rem;
        font-weight: 650;
        line-height: 1.5;
      }
      .suite-value {
        font-size: 1rem;
        line-height: 1.4;
        margin-top: 0.4rem;
        opacity: 0.9;
      }
      .contact-box .phone-link {
        font-size: 1.13rem;
        font-weight: 700;
        text-decoration: underline;
      }
      .info-block {
        margin-top: 1.2rem;
        margin-bottom: 0.8rem;
      }
      .service-item {
        font-size: 1.05rem;
        line-height: 1.5;
        padding: 0.35rem 0;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Basic helpers
# -----------------------------------------------------------------------------
def safe(val) -> str:
    if val is None:
        return ""
    try:
        if pd.isna(val):
            return ""
    except Exception:
        pass

    text = str(val)
    text = (
        text.replace("\r", " ")
        .replace("\n", " ")
        .replace("\u00A0", " ")
        .replace("\u200B", "")
        .replace("\uFEFF", "")
    )
    return re.sub(r"\s+", " ", text).strip()


def parse_object_ids(ids_raw: str) -> list[int]:
    """Accept only numeric OBJECTIDs from the URL."""
    if not ids_raw:
        return []

    parsed = []
    seen = set()
    for piece in str(ids_raw).split(","):
        piece = piece.strip()
        if not piece.isdigit():
            continue
        value = int(piece)
        if value not in seen:
            seen.add(value)
            parsed.append(value)
    return parsed


def is_yes(value) -> bool:
    if value is True or value == 1:
        return True
    return safe(value).strip().lower() in {"1", "true", "yes", "y"}


def normalize_website(url: str) -> str:
    url = safe(url).strip().strip('"').strip("'")
    if not url:
        return ""
    if not url.lower().startswith(("http://", "https://")):
        url = "https://" + url
    return url


def phone_href(phone: str) -> str:
    phone = safe(phone)
    digits = re.sub(r"\D", "", phone)
    if len(digits) == 10:
        return f"+1{digits}"
    return digits


def addresses_equivalent(a: str, b: str) -> bool:
    """Treat formatting-only address differences as the same address."""
    def normalize(value: str) -> str:
        value = safe(value).lower()
        value = re.sub(r"\b(united states of america|united states|usa)\b", "", value)
        value = re.sub(r"[^a-z0-9]+", " ", value)
        return re.sub(r"\s+", " ", value).strip()

    return bool(a and b and normalize(a) == normalize(b))


def render_info_value(label: str, value: str):
    """Render a clearly separated label and value for easier scanning."""
    value = safe(value)
    if not value:
        return

    st.markdown(
        (
            '<div class="info-block">'
            f'<div class="field-label">{html.escape(label)}</div>'
            f'<div class="field-value">{html.escape(value)}</div>'
            '</div>'
        ),
        unsafe_allow_html=True,
    )


@st.cache_data(ttl=300, show_spinner=False)
def query_records(object_ids_tuple: tuple[int, ...]):
    if not object_ids_tuple:
        return []

    # IDs are numeric-only because parse_object_ids validates them first.
    id_string = ",".join(str(x) for x in object_ids_tuple)
    where = f"OBJECTID in ({id_string})"

    params = {
        "where": where,
        "outFields": "*",
        "returnGeometry": "false",
        "returnDistinctValues": "false",
        "f": "json",
    }

    resp = requests.get(f"{FEATURE_LAYER_URL}/query", params=params, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    if "error" in data:
        message = data.get("error", {}).get("message", "ArcGIS query failed")
        raise RuntimeError(message)

    return [f.get("attributes", {}) for f in data.get("features", [])]


# -----------------------------------------------------------------------------
# PDF helpers
# The PDF intentionally contains ONLY the same five fields as public_pdf.py.
# -----------------------------------------------------------------------------
def normalize_for_core_font(text: str) -> str:
    text = safe(text)
    if not text:
        return ""

    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201C": '"',
        "\u201D": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2212": "-",
        "\u2026": "...",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)

    text = unicodedata.normalize("NFKD", text)
    return text.encode("latin-1", "ignore").decode("latin-1")


def configure_pdf_font(pdf: FPDF):
    regular_candidates = [
        os.path.join(os.path.dirname(__file__), "fonts", "DejaVuSans.ttf"),
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    bold_candidates = [
        os.path.join(os.path.dirname(__file__), "fonts", "DejaVuSans-Bold.ttf"),
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]

    regular_font = next((p for p in regular_candidates if os.path.exists(p)), None)
    bold_font = next((p for p in bold_candidates if os.path.exists(p)), None)

    if regular_font and bold_font:
        pdf.add_font("DejaVu", style="", fname=regular_font)
        pdf.add_font("DejaVu", style="B", fname=bold_font)
        return "DejaVu", True

    return "Helvetica", False


def pdf_text(val, unicode_font_enabled: bool) -> str:
    text = safe(val)
    if unicode_font_enabled:
        return text
    return normalize_for_core_font(text)


def fit_to_width(pdf: FPDF, text: str, max_width: float) -> str:
    if not text:
        return ""
    while pdf.get_string_width(text) > max_width and len(text) > 3:
        text = text[:-4] + "..."
    return text


def records_to_pdf(df: pd.DataFrame) -> bytes:
    pdf = FPDF(orientation="P", unit="mm", format="Letter")
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.set_margins(left=15, top=20, right=15)

    font_family, unicode_font_enabled = configure_pdf_font(pdf)
    pdf.add_page()

    line_h = 6
    label_size = 10
    value_size = 10
    usable_width = pdf.w - pdf.l_margin - pdf.r_margin

    pdf.set_font(font_family, style="BU", size=14)
    pdf.cell(0, 8, "Service Center Details", ln=1, align="C")
    pdf.ln(4)

    for idx, row in df.iterrows():
        if idx > 0:
            pdf.ln(2)
            y = pdf.get_y()
            pdf.set_draw_color(180, 180, 180)
            pdf.set_line_width(0.3)
            pdf.line(pdf.l_margin, y, pdf.w - pdf.r_margin, y)
            pdf.ln(4)

        fields = [
            ("Agency Name", row.get("Agency_Name"), False),
            ("Address", row.get("Address"), False),
            ("Address w/ suite #", row.get("Address_w_suit__"), False),
            ("Languages", row.get("Languages"), False),
            ("Website", row.get("Website"), True),
        ]

        for label, raw_value, is_link in fields:
            pdf.set_x(pdf.l_margin)
            label_text = f"{label}:"

            pdf.set_font(font_family, style="BU", size=label_size)
            label_width = pdf.get_string_width(label_text + " ")
            if label_width > usable_width * 0.5:
                label_width = usable_width * 0.5

            remaining_width = usable_width - label_width
            value_text = pdf_text(raw_value, unicode_font_enabled)
            display_value = fit_to_width(pdf, value_text, remaining_width)

            pdf.set_text_color(0, 0, 0)
            pdf.cell(label_width, line_h, txt=label_text, ln=0)

            if is_link and display_value:
                link_target = normalize_website(raw_value)
                pdf.set_text_color(0, 0, 255)
                pdf.set_font(font_family, style="U", size=value_size)
                pdf.cell(
                    remaining_width,
                    line_h,
                    txt=display_value,
                    ln=1,
                    link=link_target if link_target else "",
                )
                pdf.set_text_color(0, 0, 0)
            else:
                pdf.set_font(font_family, style="", size=value_size)
                pdf.cell(remaining_width, line_h, txt=display_value, ln=1)

        pdf.ln(2)

    raw = pdf.output(dest="S")
    if isinstance(raw, (bytes, bytearray)):
        return bytes(raw)
    return raw.encode("latin-1", errors="ignore")


# -----------------------------------------------------------------------------
# Viewer helpers
# -----------------------------------------------------------------------------
def record_matches_search(record: dict, search_text: str) -> bool:
    search_text = safe(search_text).lower()
    if not search_text:
        return True

    # Search normal user-facing information.
    core_values = [
        record.get("Agency_Name"),
        record.get("Address"),
        record.get("Address_w_suit__"),
        record.get("Languages"),
        record.get("Phone_number"),
        record.get("Website"),
    ]

    haystack = " ".join(safe(v).lower() for v in core_values if safe(v))

    # A service name is searchable only when that center actually provides it.
    available_service_names = " ".join(
        label.lower()
        for field, label in SERVICE_FIELDS
        if is_yes(record.get(field))
    )

    return search_text in f"{haystack} {available_service_names}"


def render_core_details(record: dict):
    address = safe(record.get("Address"))
    suite_address = safe(record.get("Address_w_suit__"))
    phone = safe(record.get("Phone_number"))
    languages = safe(record.get("Languages"))
    website = normalize_website(record.get("Website"))

    primary_address = address or suite_address
    extra_suite = (
        suite_address
        if suite_address
        and primary_address
        and not addresses_equivalent(primary_address, suite_address)
        and suite_address != primary_address
        else ""
    )

    # LOCATION
    if primary_address:
        location_html = (
            '<div class="location-box">'
            '<div class="field-label">📍 Location</div>'
            f'<div class="field-value">{html.escape(primary_address)}</div>'
        )
        if extra_suite:
            location_html += (
                f'<div class="suite-value"><strong>Suite / unit:</strong> '
                f'{html.escape(extra_suite)}</div>'
            )
        location_html += '</div>'
        st.markdown(location_html, unsafe_allow_html=True)

        encoded = quote_plus(primary_address)
        google_url = f"https://www.google.com/maps/search/?api=1&query={encoded}"
        apple_url = f"https://maps.apple.com/?q={encoded}"

        col_google, col_apple = st.columns(2)
        with col_google:
            st.link_button(
                "Get directions with Google Maps",
                google_url,
                width="stretch",
            )
        with col_apple:
            st.link_button(
                "Get directions with Apple Maps",
                apple_url,
                width="stretch",
            )

    # PHONE
    if phone:
        href = phone_href(phone)
        if href:
            phone_value = (
                f'<a class="phone-link" href="tel:{href}">'
                f'{html.escape(phone)}</a>'
            )
        else:
            phone_value = f'<div class="field-value">{html.escape(phone)}</div>'

        st.markdown(
            (
                '<div class="contact-box">'
                '<div class="field-label">☎ Phone</div>'
                f'{phone_value}'
                '</div>'
            ),
            unsafe_allow_html=True,
        )

    # LANGUAGES
    if languages:
        st.markdown(
            (
                '<div class="contact-box">'
                '<div class="field-label">🗣 Languages</div>'
                f'<div class="field-value">{html.escape(languages)}</div>'
                '</div>'
            ),
            unsafe_allow_html=True,
        )

    # WEBSITE
    if website:
        st.markdown(
            '<div class="field-label" style="margin-top:1.2rem;">Website</div>',
            unsafe_allow_html=True,
        )
        st.link_button("Visit website", website, width="stretch")

def render_services(record: dict):
    # Show only services that this center actually provides.
    available_services = [
        display_name
        for field_name, display_name in SERVICE_FIELDS
        if is_yes(record.get(field_name))
    ]

    if not available_services:
        return

    st.markdown("### Services provided")

    for service in available_services:
        st.markdown(
            f'<div class="service-item">✓ <strong>{html.escape(service)}</strong></div>',
            unsafe_allow_html=True,
        )


def render_service_center(record: dict):
    agency = safe(record.get("Agency_Name")) or "Service Center"
    has_services = any(
        is_yes(record.get(field_name))
        for field_name, _ in SERVICE_FIELDS
    )

    with st.container(border=True):
        st.subheader(agency)
        render_core_details(record)

        if has_services:
            st.divider()
            render_services(record)


def render_pagination(total_results: int, position: str):
    """
    Render pagination controls.

    `position` must be unique for each rendered copy ("top" or "bottom").
    Explicit widget keys prevent StreamlitDuplicateElementId when the same
    Previous/Next controls appear above and below the results.
    """
    if total_results <= PAGE_SIZE:
        return

    total_pages = ceil(total_results / PAGE_SIZE)
    current_page = st.session_state.viewer_page

    left, middle, right = st.columns([1, 2, 1])

    with left:
        if st.button(
            "← Previous",
            disabled=current_page <= 0,
            width="stretch",
            key=f"viewer_previous_{position}",
        ):
            st.session_state.viewer_page -= 1
            st.rerun()

    with middle:
        st.markdown(
            f"<p style='text-align:center;'><strong>Page {current_page + 1} of {total_pages}</strong></p>",
            unsafe_allow_html=True,
        )

    with right:
        if st.button(
            "Next →",
            disabled=current_page >= total_pages - 1,
            width="stretch",
            key=f"viewer_next_{position}",
        ):
            st.session_state.viewer_page += 1
            st.rerun()


# -----------------------------------------------------------------------------
# App
# -----------------------------------------------------------------------------
def main():
    st.title("Service Center Details")

    ids_raw = st.query_params.get("ids", "")
    object_ids = parse_object_ids(ids_raw)

    if not object_ids:
        st.warning(
            "No service centers were supplied. Please return to the map, "
            "apply your filters, and click **View service center details** again."
        )
        return

    try:
        with st.spinner("Loading service center details..."):
            records = query_records(tuple(object_ids))
    except Exception:
        st.error(
            "We couldn't load the service center information right now. "
            "Please try again or return to the map."
        )
        return

    if not records:
        st.info("No service centers match the current results.")
        return

    # Keep the same order as the IDs received from Experience Builder.
    order = {oid: i for i, oid in enumerate(object_ids)}
    records.sort(key=lambda r: order.get(r.get("OBJECTID"), len(order)))

    total_count = len(records)
    st.markdown(
        f"<div class='result-count'><strong>{total_count} service center(s) found.</strong></div>",
        unsafe_allow_html=True,
    )
    st.write("These are the service centers that match the filters you applied on the map.")

    # -------------------------------------------------------------------------
    # PDF options. The existing public_pdf.py app remains untouched.
    # This is a second copy inside the new viewer for review/testing.
    # -------------------------------------------------------------------------
    with st.expander("Download a PDF of these results"):
        st.caption(
            "The PDF includes Agency Name, Address, Address with suite/unit, "
            "Languages, and Website only."
        )

        df = pd.DataFrame(records)
        pdf_all = records_to_pdf(df)
        st.download_button(
            label=f"Download all {len(df)} service centers as PDF",
            data=pdf_all,
            file_name="service_centers_all.pdf",
            mime="application/pdf",
            key="viewer_pdf_download_all",
        )

        st.markdown("#### Or choose specific service centers")
        selection_df = pd.DataFrame(
            {
                "Select": [False] * len(df),
                "Service Center": [
                    safe(name) or "Service Center"
                    for name in df.get("Agency_Name", pd.Series([""] * len(df)))
                ],
            },
            index=df.index,
        )

        edited = st.data_editor(
            selection_df,
            hide_index=True,
            use_container_width=True,
            height=min(420, 42 * (len(selection_df) + 1)),
            column_config={
                "Select": st.column_config.CheckboxColumn(
                    "Select",
                    help="Choose the service centers to include in the PDF.",
                    default=False,
                ),
                "Service Center": st.column_config.TextColumn("Service Center"),
            },
            disabled=["Service Center"],
            key="viewer_pdf_selection",
        )

        selected_indices = edited.index[edited["Select"]].tolist()
        selected_df = df.loc[selected_indices] if selected_indices else df.iloc[0:0]

        if selected_df.empty:
            st.button(
                "Download selected service centers as PDF",
                disabled=True,
                help="Select at least one service center above.",
                key="viewer_pdf_selected_disabled",
            )
        else:
            pdf_selected = records_to_pdf(selected_df)
            st.download_button(
                label=f"Download selected {len(selected_df)} service center(s) as PDF",
                data=pdf_selected,
                file_name="service_centers_selected.pdf",
                mime="application/pdf",
                key="viewer_pdf_download_selected",
            )

    st.divider()

    search_text = st.text_input(
        "Search within these results",
        placeholder="Search by service center name, address, language, or available service",
        key="viewer_search_input",
    )

    visible_records = [
        record
        for record in records
        if record_matches_search(record, search_text)
    ]

    # Reset to page 1 whenever search changes.
    if "viewer_search" not in st.session_state:
        st.session_state.viewer_search = search_text
    if "viewer_page" not in st.session_state:
        st.session_state.viewer_page = 0

    if st.session_state.viewer_search != search_text:
        st.session_state.viewer_search = search_text
        st.session_state.viewer_page = 0

    if not visible_records:
        st.info("No service centers match that search. Try a different word or phrase.")
        return

    total_visible = len(visible_records)
    total_pages = max(1, ceil(total_visible / PAGE_SIZE))

    # Protect against stale page state.
    if st.session_state.viewer_page >= total_pages:
        st.session_state.viewer_page = total_pages - 1

    start = st.session_state.viewer_page * PAGE_SIZE
    end = min(start + PAGE_SIZE, total_visible)

    if search_text:
        st.write(f"Showing **{total_visible} of {total_count}** service centers.")

    st.markdown(f"### Showing {start + 1}-{end} of {total_visible}")
    render_pagination(total_visible, "top")

    for record in visible_records[start:end]:
        render_service_center(record)

    render_pagination(total_visible, "bottom")


if __name__ == "__main__":
    main()
