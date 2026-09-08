
import streamlit as st

st.set_page_config(
    page_title="ASIAAN Map Tool Tutorial",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

OVERVIEW_IMAGE = "asiaan_tutorial_overview_annotated.png"

SECTIONS = [
    ("A", "Map Pins & Overview"),
    ("B", "Map Controls"),
    ("C", "Service Filters"),
    ("D", "Keyword Search"),
    ("E", "Location Tool"),
    ("F", "Transportation Service Area"),
    ("G", "Service Center Details"),
    ("H", "View Service Center Details"),
    ("I", "Download PDF"),
    ("J", "Map Search"),
    ("", "Accessibility"),
]

st.markdown(
    """
    <style>
      .block-container {
        max-width: 1180px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
      }

      [data-testid="stSidebar"] {
        min-width: 280px;
        max-width: 280px;
      }

      [data-testid="stSidebar"] .block-container {
        padding-top: 1.5rem;
      }

      .tutorial-title {
        font-size: 2rem;
        font-weight: 750;
        margin-bottom: 0.25rem;
      }

      .tutorial-subtitle {
        font-size: 1rem;
        opacity: 0.75;
        margin-bottom: 1.3rem;
      }

      .section-card {
        border: 1px solid rgba(128,128,128,.28);
        border-radius: 14px;
        padding: 1.2rem 1.3rem;
        margin-top: 1rem;
      }

      .section-marker {
        display: inline-block;
        min-width: 34px;
        height: 34px;
        line-height: 34px;
        text-align: center;
        border-radius: 50%;
        background: #0F4C81;
        color: white;
        font-weight: 800;
        margin-right: .6rem;
      }

      .placeholder {
        border: 1px dashed rgba(128,128,128,.45);
        border-radius: 12px;
        padding: 2rem 1.2rem;
        text-align: center;
        opacity: .72;
        margin-top: 1rem;
      }

      .overview-caption {
        font-size: .92rem;
        opacity: .72;
        margin-top: .35rem;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("## ASIAAN Tutorial")
    st.caption("Choose a section")

    labels = [
        f"{letter}  {title}" if letter else title
        for letter, title in SECTIONS
    ]

    selected_label = st.radio(
        "Tutorial sections",
        labels,
        label_visibility="collapsed",
    )

selected_index = labels.index(selected_label)
marker, section_title = SECTIONS[selected_index]

st.markdown(
    '<div class="tutorial-title">ASIAAN Map Tool Tutorial</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="tutorial-subtitle">'
    'Interactive tutorial layout preview'
    '</div>',
    unsafe_allow_html=True,
)

st.image(OVERVIEW_IMAGE, use_container_width=True)
st.markdown(
    "The letters on the overview image identify where each tutorial section is located on the map.",
    unsafe_allow_html=True,
)

if marker:
    heading = f'<span class="section-marker">{marker}</span>{section_title}'
else:
    heading = section_title

st.markdown(
    f"""
    <div class="section-card">
      <h2 style="margin-top:0;">{heading}</h2>
      <div class="placeholder">
        Section content, screenshots, and step-by-step instructions will appear here.
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if section_title == "Accessibility":
    st.markdown("### Accessibility review")
    left, right = st.columns(2)
    with left:
        st.markdown(
            """
            <div class="section-card">
              <h3>WAVE Review</h3>
              <div class="placeholder">WAVE observations will appear here.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(
            """
            <div class="section-card">
              <h3>NVDA Screen Reader</h3>
              <div class="placeholder">NVDA test results will appear here.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
