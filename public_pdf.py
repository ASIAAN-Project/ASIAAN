# public_pdf.py

import os
import re
import unicodedata

import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF

# ---------------------------------------------------------
# Streamlit + ArcGIS config
# ---------------------------------------------------------
st.set_page_config(page_title="Export Service Center to PDF", layout="wide")

FEATURE_LAYER_URL = st.secrets["ARCGIS_FEATURE_LAYER"]


# ---------------------------------------------------------
# ArcGIS helper
# ---------------------------------------------------------
def query_layer(where: str = "1=1", out_fields: str = "*"):
    """
    Query the ASIAAN feature layer with a WHERE clause and return attributes.
    """
    params = {
        "where": where,
        "outFields": out_fields,
        "returnGeometry": "false",
        "returnDistinctValues": "false",
        "f": "json",
    }
    resp = requests.get(f"{FEATURE_LAYER_URL}/query", params=params, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    features = data.get("features", [])
    return [f["attributes"] for f in features]


# ---------------------------------------------------------
# PDF helpers
# ---------------------------------------------------------
def safe(val) -> str:
    """Turn NaN / None into empty string, everything else into a clean str."""
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
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_for_core_font(text: str) -> str:
    """
    Make text safe for core PDF fonts like Helvetica.

    This is only used as a fallback when a Unicode font is not available.
    """
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
    """
    Prefer a Unicode-capable font so long result sets with non-Latin characters
    do not crash. Fall back to Helvetica if needed.
    """
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
    """
    Return text suitable for the currently configured PDF font.
    """
    text = safe(val)
    if unicode_font_enabled:
        return text
    return normalize_for_core_font(text)


def fit_to_width(pdf: FPDF, text: str, max_width: float) -> str:
    """
    Ensure text fits inside max_width.
    If it's too long, truncate and add '...'.
    """
    if not text:
        return ""

    while pdf.get_string_width(text) > max_width and len(text) > 3:
        text = text[:-4] + "..."
    return text


def records_to_pdf(df: pd.DataFrame) -> bytes:
    """
    Generate the PDF in portrait mode.

    Title (centered): "Service centre details" (bold + underline)

    For each service centre:

        Agency Name: <value>
        Address: <value>
        Address w/ suite #: <value>
        Languages: <value>
        Website: <blue underlined clickable link>

    Labels (before :) are bold + underlined.
    Values are normal.
    Service centres separated by a horizontal line.
    """
    # Portrait Letter page
    pdf = FPDF(orientation="P", unit="mm", format="Letter")
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.set_margins(left=15, top=20, right=15)

    font_family, unicode_font_enabled = configure_pdf_font(pdf)

    pdf.add_page()

    # Sizes
    line_h = 6
    label_size = 10
    value_size = 10

    usable_width = pdf.w - pdf.l_margin - pdf.r_margin

    # -------- Title --------
    pdf.set_font(font_family, style="BU", size=14)
    pdf.cell(0, 8, "Service centre details", ln=1, align="C")
    pdf.ln(4)

    for idx, row in df.iterrows():
        # Separator line between centres (not before the first)
        if idx > 0:
            pdf.ln(2)
            y = pdf.get_y()
            pdf.set_draw_color(180, 180, 180)
            pdf.set_line_width(0.3)
            pdf.line(pdf.l_margin, y, pdf.w - pdf.r_margin, y)
            pdf.ln(4)

        # Prepare fields
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

            # Draw label in bold + underline
            pdf.set_font(font_family, style="BU", size=label_size)
            label_width = pdf.get_string_width(label_text + " ")
            if label_width > usable_width * 0.5:
                label_width = usable_width * 0.5

            remaining_width = usable_width - label_width

            value_text = pdf_text(raw_value, unicode_font_enabled)
            display_value = fit_to_width(pdf, value_text, remaining_width)

            # --- label ---
            pdf.set_text_color(0, 0, 0)
            pdf.cell(label_width, line_h, txt=label_text, ln=0)

            # --- value ---
            if is_link and display_value:
                link_target = safe(raw_value)

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


# ---------------------------------------------------------
# Streamlit app
# ---------------------------------------------------------
def main():
    st.markdown(
        "<h1 style='font-size: 28px;'>Export Service Centres to PDF</h1>",
        unsafe_allow_html=True,
    )

    # Query params: ?ids=3,7,25
    qp = st.query_params
    ids_raw = qp.get("ids", None)

    if not ids_raw:
        st.info(
            "No service centre IDs supplied. "
            "Please return to the map and click **Save PDF** again."
        )
        return

    if isinstance(ids_raw, list):
        id_string = ids_raw[0]
    else:
        id_string = ids_raw

    where = f"OBJECTID in ({id_string})"

    # ---- Fetch records from ArcGIS ----
    with st.spinner("Loading service centre details..."):
        records = query_layer(where=where, out_fields="*")

    if not records:
        st.error("No records found for those OBJECTIDs.")
        return

    df = pd.DataFrame(records)
    st.write(f"**{len(df)} record(s) returned.**")

    # ---- Show table with checkboxes ----
    cols_for_view = ["Agency_Name", "Address", "Address_w_suit__", "Languages", "Website"]
    view_df = df[cols_for_view].copy()
    view_df.insert(0, "Select", True)

    st.markdown("### Select the service centres you want in the PDF")

    edited = st.data_editor(
        view_df,
        hide_index=True,
        use_container_width=True,
        height=420,
        column_config={
            "Select": st.column_config.CheckboxColumn(
                "Select",
                help="Tick the service centres to include",
                default=True,
            )
        },
        disabled=["Agency_Name", "Address", "Address_w_suit__", "Languages", "Website"],
    )

    selected_indices = edited.index[edited["Select"]].tolist()
    selected_df = df.loc[selected_indices] if selected_indices else df.iloc[0:0]

    st.write("")
    col_all, col_sel = st.columns(2)

    # ---- Download ALL ----
    with col_all:
        pdf_all = records_to_pdf(df)
        st.download_button(
            label=f"📄 Download all {len(df)} record(s)",
            data=pdf_all,
            file_name="service_centres_all.pdf",
            mime="application/pdf",
        )

    # ---- Download SELECTED ----
    with col_sel:
        if selected_df.empty:
            st.button(
                "📄 Download selected record(s)",
                disabled=True,
                help="Tick at least one row above to enable this.",
            )
        else:
            pdf_sel = records_to_pdf(selected_df)
            st.download_button(
                label=f"📄 Download selected {len(selected_df)} record(s)",
                data=pdf_sel,
                file_name="service_centres_selected.pdf",
                mime="application/pdf",
            )


if __name__ == "__main__":
    main()
