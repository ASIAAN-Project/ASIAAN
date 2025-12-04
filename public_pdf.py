import io
from typing import List

import pandas as pd
import requests
import streamlit as st
from fpdf import FPDF


# ------------------------ #
# Streamlit page settings  #
# ------------------------ #

st.set_page_config(
    page_title="Service Centre PDF Export",
    layout="wide",
)

# 🔒 Hard-code your feature layer URL here
FEATURE_LAYER_URL = (
    "https://services.arcgis.com/.../FeatureServer/0"  # <-- your real URL
)


# ------------------------ #
# Helpers                  #
# ------------------------ #

def sanitize_text(value) -> str:
    """
    Convert to string and strip characters FPDF cannot render (non latin-1).
    This avoids FPDFUnicodeEncodingException on Streamlit Cloud.
    """
    if value is None:
        return ""
    if not isinstance(value, str):
        value = str(value)

    # remove characters outside latin-1 range
    return value.encode("latin-1", "ignore").decode("latin-1")


def query_layer(object_ids: List[int]) -> List[dict]:
    """
    Fetch attribute records for the given OBJECTIDs from ArcGIS feature layer.
    """
    if not object_ids:
        return []

    where = f"OBJECTID IN ({','.join(map(str, object_ids))})"

    params = {
        "where": where,
        "outFields": "*",
        "f": "json",
    }

    resp = requests.get(f"{FEATURE_LAYER_URL}/query", params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    features = data.get("features", [])
    return [f["attributes"] for f in features]


def fit_to_width(pdf: FPDF, text: str, max_width: float) -> str:
    """
    Ensure 'text' fits in the given width, truncating with '...'
    if necessary. Works only with sanitized (latin-1 safe) text.
    """
    text = sanitize_text(text)

    # nothing to do if it already fits
    if pdf.get_string_width(text) <= max_width:
        return text

    # if very short and still too wide, just return it as-is
    if len(text) <= 3:
        return text

    # truncate and add "..."
    base = text
    while pdf.get_string_width(base + "...") > max_width and len(base) > 0:
        base = base[:-1]

    return base + "..."


def records_to_pdf(df: pd.DataFrame) -> bytes:
    """
    Render the selected service centres into a nicely formatted PDF.

    Layout:
        Service centre details               (title)
        ----------------------------------------------
        Agency Name: ...
        Address: ...
        Address w/ suite #: ...
        Languages: ...
        Website: clickable blue underlined
    """
    # sanitize dataframe text once up front
    df = df.copy()
    for col in df.columns:
        df[col] = df[col].map(sanitize_text)

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_margins(15, 15, 15)
    pdf.add_page()

    # title
    pdf.set_font("helvetica", "BU", 16)
    title = "Service centre details"
    title_w = pdf.get_string_width(title)
    pdf.set_x((pdf.w - title_w) / 2)
    pdf.cell(title_w, 10, title, ln=1)
    pdf.ln(5)

    usable_width = pdf.w - pdf.l_margin - pdf.r_margin
    label_width = 55  # width for "Agency Name:", etc.
    value_width = usable_width - label_width

    def write_field(label: str, value: str):
        label = sanitize_text(label)
        value = sanitize_text(value)

        # label: bold + underline
        pdf.set_font("helvetica", "BU", 11)
        pdf.cell(label_width, 6, label, ln=0)

        # value: normal, truncated to width
        pdf.set_font("helvetica", "", 11)
        display = fit_to_width(pdf, value, value_width)
        pdf.cell(value_width, 6, display, ln=1)

    for idx, row in df.iterrows():
        agency = row.get("Agency_Name", "")
        addr1 = row.get("Address", "")
        addr2 = row.get("Address_w_suit_", "")
        langs = row.get("Languages", "")
        website = row.get("Website", "")

        # Each service centre block
        write_field("Agency Name:", agency)
        write_field("Address:", addr1)
        write_field("Address w/ suite #:", addr2)
        write_field("Languages:", langs)

        # Website: clickable blue underlined
        pdf.set_font("helvetica", "BU", 11)
        pdf.set_text_color(0, 0, 255)
        label = "Website:"
        pdf.cell(label_width, 6, label, ln=0)

        pdf.set_font("helvetica", "U", 11)
        pdf.set_text_color(0, 0, 255)
        website_sanitized = sanitize_text(website)
        website_display = fit_to_width(pdf, website_sanitized, value_width)

        # link() uses the full, untruncated URL, but display the truncated one
        link_url = website_sanitized if website_sanitized else ""
        pdf.cell(value_width, 6, website_display, ln=1, link=link_url)

        # reset text color to black for next fields
        pdf.set_text_color(0, 0, 0)

        # separator line between centres
        pdf.ln(2)
        y = pdf.get_y()
        pdf.set_draw_color(0, 0, 0)
        pdf.set_line_width(0.3)
        pdf.line(pdf.l_margin, y, pdf.w - pdf.r_margin, y)
        pdf.ln(4)

    # return as bytes
    return pdf.output(dest="S").encode("latin-1")


# ------------------------ #
# Streamlit UI             #
# ------------------------ #

def main():
    st.title("Export Service Centres to PDF")

    params = st.query_params
    ids_param = params.get("ids", [])

    if not ids_param:
        st.info("No service centre IDs supplied. Please return to the map and click Save PDF.")
        return

    # ids are passed as a single comma-separated string
    id_string = ids_param[0]
    try:
        id_list = [int(x) for x in id_string.split(",") if x.strip()]
    except ValueError:
        st.error("Invalid OBJECTID list.")
        return

    records = query_layer(id_list)
    if not records:
        st.error("No records found for those OBJECTIDs.")
        return

    df = pd.DataFrame(records)

    # show preview table with checkboxes
    st.write(f"{len(df)} record(s) returned.")
    df_preview = df[["Agency_Name", "Address", "Address_w_suit_", "Languages", "Website"]].copy()
    df_preview.insert(0, "Select", True)

    edited = st.data_editor(
        df_preview,
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
        column_config={
            "Select": st.column_config.CheckboxColumn(
                "Select",
                default=True,
                help="Uncheck to exclude from PDF",
            )
        },
        key="service_table",
    )

    selected_df = df[df.index.isin(edited.index[edited["Select"]])]
    if selected_df.empty:
        st.warning("No records selected.")
        return

    col_all, col_sel = st.columns(2)

    with col_all:
        if st.download_button(
            label=f"⬇️ Download all {len(df)} record(s)",
            data=records_to_pdf(df),
            file_name="service_centres.pdf",
            mime="application/pdf",
        ):
            st.success("PDF generated for all records.")

    with col_sel:
        if st.download_button(
            label=f"⬇️ Download selected {len(selected_df)} record(s)",
            data=records_to_pdf(selected_df),
            file_name="service_centres_selected.pdf",
            mime="application/pdf",
        ):
            st.success("PDF generated for selected records.")


if __name__ == "__main__":
    main()
