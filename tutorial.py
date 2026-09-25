from pathlib import Path
import base64
import streamlit as st

st.set_page_config(
    page_title="ASIAAN Map Tool Tutorial",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent
IMAGE_DIR = BASE_DIR / "images"

SECTIONS = [
    ("Start", "Start here"),
    ("A", "Map pins & overview"),
    ("B", "Map controls"),
    ("C", "Service filters"),
    ("D", "Keyword Search"),
    ("E", "Location tool"),
    ("F", "Transportation Service Area"),
    ("G", "Service center details"),
    ("H", "View filtered results"),
    ("I", "Map search"),
    ("Quick", "Quick workflow"),
]

st.markdown(
    """
    <style>
      .block-container {
        max-width: 1240px;
        padding-top: 1rem;
        padding-bottom: 4rem;
      }

      [data-testid="stSidebar"] {
        min-width: 290px;
        max-width: 290px;
      }

      [data-testid="stSidebar"] .block-container {
        padding-top: 1.5rem;
      }

      html, body, [class*="css"] {
        font-size: 18px;
      }

      h1 {
        font-size: 2rem !important;
        line-height: 1.2 !important;
      }

      h2 {
        font-size: 1.5rem !important;
        line-height: 1.25 !important;
        margin-top: 1.25rem !important;
      }

      h3 {
        font-size: 1.18rem !important;
        line-height: 1.3 !important;
      }

      p, li {
        line-height: 1.58 !important;
      }

      .tutorial-subtitle {
        font-size: 1rem;
        opacity: .76;
        margin-top: -.35rem;
        margin-bottom: .8rem;
      }

      .section-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-width: 40px;
        height: 40px;
        padding: 0 10px;
        border-radius: 999px;
        background: #0F4C81;
        color: white;
        font-weight: 800;
        margin-right: .6rem;
        vertical-align: middle;
      }

      .step-box {
        border: 1px solid rgba(128,128,128,.28);
        border-radius: 12px;
        padding: 1rem 1.1rem;
        margin: .7rem 0;
        background: rgba(128,128,128,.045);
      }

      .step-number {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: #0F4C81;
        color: white;
        font-weight: 800;
        margin-right: .65rem;
      }

      .callout {
        border-left: 5px solid #168A8B;
        background: rgba(22,138,139,.08);
        padding: .85rem 1rem;
        border-radius: 8px;
        margin: .9rem 0 1rem 0;
      }

      .quick-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 14px;
        margin-top: 1rem;
      }

      .quick-card {
        border: 1px solid rgba(128,128,128,.28);
        border-radius: 13px;
        padding: 1rem;
        min-height: 135px;
        background: rgba(128,128,128,.04);
      }

      .quick-card strong {
        display: block;
        color: #0F4C81;
        font-size: 1.05rem;
        margin-bottom: .35rem;
      }

      .sticky-overview {
        position: sticky;
        top: .35rem;
        z-index: 80;
        background: #0E1117;
        padding: .45rem .45rem .55rem .45rem;
        border-radius: 12px;
        border: 1px solid rgba(128,128,128,.28);
        margin: .55rem 0 1.1rem 0;
        box-shadow: 0 4px 14px rgba(0,0,0,.18);
      }

      .sticky-overview img {
        display: block;
        width: 100%;
        max-height: 360px;
        object-fit: contain;
        border-radius: 8px;
        background: white;
      }

      .overview-caption {
        font-size: .88rem;
        opacity: .72;
        margin-top: .35rem;
        text-align: center;
      }

      div[data-testid="stButton"] button,
      div[data-testid="stLinkButton"] a {
        min-height: 48px;
        font-size: 1rem;
        font-weight: 650;
      }

      @media (max-width: 1000px) {
        .sticky-overview { position: static; }
        .sticky-overview img { max-height: none; }
        .quick-grid { grid-template-columns: 1fr; }
      }
    </style>
    """,
    unsafe_allow_html=True,
)


def image(name: str, caption: str | None = None, width: int | None = None):
    path = IMAGE_DIR / name
    if not path.exists():
        st.warning(f"Tutorial image is missing: {name}")
        return

    if width:
        st.image(str(path), caption=caption, width=width)
    else:
        st.image(str(path), caption=caption, use_container_width=True)


def sticky_overview():
    path = IMAGE_DIR / "overview_annotated.png"
    if not path.exists():
        st.warning("Annotated overview image is missing.")
        return

    encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
    st.markdown(
        f"""
        <div class="sticky-overview">
          <img src="data:image/png;base64,{encoded}" alt="Annotated overview of the ASIAAN Map Tool. Letters A through I identify the main tutorial sections." />
          <div class="overview-caption">Use the letters on this overview to see where each tutorial section is located on the map.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_heading(letter: str, title: str):
    if letter in {"Start", "Quick"}:
        st.header(title)
    else:
        st.markdown(
            f'<h1><span class="section-badge">{letter}</span>{title}</h1>',
            unsafe_allow_html=True,
        )


def step(number: int, title: str, text: str):
    st.markdown(
        f"""
        <div class="step-box">
          <div><span class="step-number">{number}</span><strong>{title}</strong></div>
          <div style="margin-top:.55rem;">{text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with st.sidebar:
    st.markdown("## ASIAAN Tutorial")
    st.caption("Choose a section")

    labels = []
    for marker, title in SECTIONS:
        if marker == "Start":
            labels.append("Start here")
        elif marker == "Quick":
            labels.append("Quick workflow")
        else:
            labels.append(f"{marker}  {title}")

    selected_label = st.radio(
        "Tutorial sections",
        labels,
        label_visibility="collapsed",
    )

selected_index = labels.index(selected_label)
marker, title = SECTIONS[selected_index]

st.title("ASIAAN Map Tool Tutorial")
st.markdown(
    '<div class="tutorial-subtitle">Use the menu on the left to move directly to the part of the map you need help with.</div>',
    unsafe_allow_html=True,
)

# The annotated map stays visible at the top for every section.
sticky_overview()


# -----------------------------------------------------------------------------
# START HERE
# -----------------------------------------------------------------------------
if marker == "Start":
    section_heading(marker, "Start here")
    st.write(
        "The letters on the overview map match the sections in the menu on the left. "
        "Choose a section to see clear instructions and a larger image for that part of the map."
    )

    st.markdown("### What each letter means")
    st.markdown(
        """
        - **A — Service center pins:** service center locations on the map.
        - **B — Map controls:** zoom, Home, locate, compass, and selection controls.
        - **C — Service filters:** open the service and language filters.
        - **D — Keyword Search:** search using a service-center name or another searchable term.
        - **E — Location tool:** choose a location and distance radius.
        - **F — Transportation Service Area:** display Pace transportation areas or routes.
        - **G — Service center details:** review information for a center selected on the map.
        - **H — View filtered results:** open the filtered service centers on a separate page without the map.
        - **I — Map search:** search for an address or place on the map.
        """
    )


# -----------------------------------------------------------------------------
# A - MAP PINS
# -----------------------------------------------------------------------------
elif marker == "A":
    section_heading(marker, "Map pins & overview")
    st.write(
        "The main map shows service center locations across the region. Start here to understand the pins and the basic map view."
    )
    image("map_pins.png", "Main map with service-center pins visible.")

    st.markdown("### Service center pins")
    st.markdown(
        """
        - Each green pin represents a service center location.
        - Click a pin to open the details for that service center. The details appear in the panel on the right side of the map.
        - When several service centers are close together, a green marker may show a number. The number means multiple centers are grouped in that area at the current zoom level.
        - Zoom in to separate grouped locations and see individual service-center pins more clearly.
        """
    )


# -----------------------------------------------------------------------------
# B - MAP CONTROLS
# -----------------------------------------------------------------------------
elif marker == "B":
    section_heading(marker, "Map controls")
    st.write("The main map controls are located along the upper-left edge of the map.")
    image("map_controls.png", "Map controls and what each control does.")

    st.markdown("### Zoom, Home, Locate and Compass")
    st.markdown(
        """
        - Use **+** to zoom in and **−** to zoom out.
        - **Home** returns the map to its starting view.
        - The **target/location control** recenters the map when location access is available. This means it will zoom to your location.
        - The **compass** returns the map to its normal north-facing orientation.
        """
    )

    st.markdown("### Map selection controls")
    st.markdown(
        """
        - The pointer/selection control is near the upper-left corner.
        - Use its small drop-down arrow to open the available selection options.
        - The clear-selection control removes an active map selection when applicable.
        """
    )


# -----------------------------------------------------------------------------
# C - SERVICE FILTERS
# -----------------------------------------------------------------------------
elif marker == "C":
    section_heading(marker, "Service filters")
    st.write(
        "The blue button at the top center of the map opens and closes the service-filter panel."
    )
    image("service_filters.png", "Service and language filters shown above the map.")

    step(
        1,
        "Open the filters",
        "Click the blue drop-down button at the top center of the map. The service categories expand above the map.",
    )

    step(
        2,
        "Choose a service or language",
        "Find the service or service category you are interested in and turn on the switch button located next to it. "
        "Select the language you need and turn on the switch button located next to it. The map updates to reflect the selected filters. "
        "Now the green pins showing on the map represent the service centers offering the service you selected in the specific language you selected.",
    )

    image(
        "filter_info_switch.png",
        "The information icon explains the service. The switch turns the filter on or off.",
    )

    st.markdown("### What the information icon means")
    st.write(
        "An information icon appears beside the service filters. Use it when you want a short explanation for each service category before deciding whether to turn a filter on."
    )
    step(1, "Click the information icon beside a service", "Read the description of what that service or filter represents.")
    step(2, "Decide whether the filter matches what you need", "After reading the description, turn on the switch beside the service category if you want to include it in your search.")

    st.markdown(
        '<div class="callout"><strong>Easy way to remember:</strong> The information icon explains the service. The switch turns the filter on or off.</div>',
        unsafe_allow_html=True,
    )

    step(
        3,
        "Use more than one filter when needed",
        "You can turn on additional filters to narrow the results further. Give the map a moment to update after each selection. "
        "Remember, when you select multiple filters, the map will only show service centers that provide ALL selected services at the same location. "
        "If you want to find service centers that provide different services at different locations, filter for each service separately. "
        "For example, if you are looking for service centers that provide Senior Exercise Programs and Dementia Support at the same location, select both. "
        "If you are looking for service centers that provide either service, conduct two separate searches.",
    )

    image(
        "filter_one_vs_multiple.png",
        "Example showing the difference between using one filter and using multiple filters.",
    )

    step(
        4,
        "Close the filter panel",
        "Click the same blue button again when you want more space for the map. Closing the panel does not remove the filters you already selected.",
    )


# -----------------------------------------------------------------------------
# D - KEYWORD SEARCH
# -----------------------------------------------------------------------------
elif marker == "D":
    section_heading(marker, "Keyword Search")
    st.write(
        "Keyword Search is at the top-left of the page, above the service categories. Searching by keyword is another way to locate service centers."
    )
    image("keyword_search.png", 'Example: typing “icare” returns matching service-center suggestions.')

    step(1, "Click inside the Keyword Search box", "Start typing a word or service-center name.")
    step(2, "Review the suggestions", "Matching results appear directly below the search box as you type.")
    step(3, "Choose the matching result", "Click the result that best matches what you are looking for. The map moves to or highlights the selected result.")
    step(4, "Clear the search when you are finished", "Click the X at the right side of the Keyword Search box to remove the current text and start a new search.")

    st.markdown(
        '<div class="callout"><strong>What search words to use:</strong> Search words can include the center name of a service center, if known, and other searchable information such as address, languages, or words describing services.</div>',
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# E - LOCATION TOOL
# -----------------------------------------------------------------------------
elif marker == "E":
    section_heading(marker, "Location tool")
    st.write(
        "The Location tool is on the left side of the map. It lets you choose a place and display a distance radius around that place so you can focus on a specific area."
    )
    image("location_tool.png", "Location tool, distance control, and the shaded distance area.")

    step(1, "Choose how to define the location", "The three icons at the top let you use a point, a line, or an area. For a simple search around one address or place, use the point option.")
    step(2, "Set the distance", "Enter the distance in the number box and choose the unit, such as Miles. A smaller number restricts the search to a smaller area; a larger number allows you to search over a larger area.")
    step(3, "Choose the location on the map", "With the point option selected, choose the location you want to use. The selected place is listed under Input location, and a blue point appears on the map.")

    st.markdown("### Understanding the shaded distance area")
    st.write(
        "After a location is selected, the map draws a blue shaded circle around it. The circle shows the radius in miles around the selected location. Service-center pins within the circle are the locations inside that distance."
    )

    step(4, "Review the current distance", "The blue point marks the selected location. The shaded circle shows how far the selected distance extends from that location.")
    step(5, "Change the distance if needed", "You can change the distance without selecting the location again. The shaded circle updates around the same location.")

    st.markdown(
        '<div class="callout"><strong>Important:</strong> Service-center pins may still be visible outside the shaded circle depending on the current map settings. The shaded area helps you identify which centers are within the selected distance.</div>',
        unsafe_allow_html=True,
    )

    st.markdown("### Clear the selected location")
    image("location_clear.png", "Clear the selected location when you want to start over.")
    step(6, "Click Clear to start over", "Use the Clear control at the bottom of the Location panel. The selected location and shaded area are removed, and you can choose a new location.")


# -----------------------------------------------------------------------------
# F - TRANSPORTATION
# -----------------------------------------------------------------------------
elif marker == "F":
    section_heading(marker, "Transportation Service Area")
    st.write(
        "The Transportation Service Area widget is on the lower-left side of the map. It can display the geographical area covered by fixed-route transportation services such as Pace and current routes on top of the service-center map."
    )
    image(
        "transportation_service_area.png",
        "Pace current routes displayed as blue route lines while service-center pins remain visible.",
    )

    step(1, "Turn the transportation layer on", "Click the checkbox next to Transportation Service Area. A check mark means the transportation layer is turned on.")
    step(2, "Choose a transportation view", "Select the circle beside Pace On Demand, Pace dial a ride service, Pace current routes, or Pace Service Area.")
    step(3, "Review the map", "The selected transportation information appears on top of the service-center map. For example, Pace current routes are shown as blue route lines.")
    step(4, "Switch to another transportation view", "Click the circle beside a different transportation option. The newly selected view replaces the previous one.")
    step(5, "Open transportation details", "When a route or transportation feature can be selected, click it on the map. Its details open in the panel on the right side.")
    step(6, "Turn the transportation layer off", "Click the checked box next to Transportation Service Area again. The transportation overlay is removed from the map.")

    st.markdown(
        '<div class="callout"><strong>Helpful:</strong> The green service-center pins remain available while a transportation layer is displayed, so you can compare center locations with nearby routes or service areas.</div>',
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# G - SERVICE CENTER DETAILS
# -----------------------------------------------------------------------------
elif marker == "G":
    section_heading(marker, "Service center details")
    st.write(
        "Clicking a service-center pin opens a details panel on the right side of the map. This is the quickest way to view details about one center while staying on the map."
    )
    image("service_center_details.png", "Service-center details panel and the information available in it.")

    step(1, "Confirm the service-center name", "The center name appears near the top of the panel.")
    step(2, "Find directions to a service center", "Use Open in Google Maps or Open in Apple Maps under Directions.")
    step(3, "Review the basic information", "The panel shows the address, languages supported, website, and phone number when those details are available.")
    step(4, "Check the services", "The service list uses Yes and No. Yes means that service is listed as available at the center; No means it is not listed as available.")
    step(5, "Scroll for more information", "Use the scrollbar inside the right-side panel to continue through the list of services.")
    step(6, "Move between records", "Use the left and right arrows at the top of the panel when you want to move between the records currently available in the panel.")


# -----------------------------------------------------------------------------
# H - VIEW FILTERED RESULTS
# -----------------------------------------------------------------------------
elif marker == "H":
    section_heading(marker, "View filtered results")
    st.write(
        "Use View after you have applied the filters you want on the map to see the filtered results on a separate page. The View page uses the current filtered results, so apply the filters first and let the map finish updating before you click View."
    )
    image("view_button.png", "The View button is on the right side of the map.")

    step(1, "Apply the filters on the map", "Choose the service, language, location, or other filters you need. Wait for the service-center results to update.")
    step(2, "Click View", "Find the blue View button on the right side of the map and click it. A separate Service Center Details page opens.")
    step(3, "Check the number of results", "The page shows how many service centers matched the filters. If you change the filters on the map, click View again to open the updated results.")

    st.markdown("### Search, browse, and read the results")
    image(
        "view_results.png",
        "Service Center Details page showing search, page navigation, contact information, and Services provided.",
        width=720,
    )

    step(4, "Search within these results", "Enter a service-center name, address, language, or available service. This search only works within the centers that already matched the filters from the map.")
    step(5, "Move through the results", "Use Next to move to the next group of service centers. Use Previous to return to an earlier group. The page number appears between the buttons.")
    step(6, "Read each service-center card", "The card shows the center name, Location, directions, phone number, Languages, Website, and Services provided.")
    step(7, "Read Services provided", "Only services that the center provides are listed in this section. Services marked as unavailable are not shown here, which makes the list easier to scan.")

    st.markdown(
        '<div class="callout"><strong>Why this page can be easier to use:</strong> The View page keeps the center name, location, phone, languages, website, and available services in separate sections, so you do not need to open and scroll through individual map pop-ups.</div>',
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# I - MAP SEARCH
# -----------------------------------------------------------------------------
elif marker == "I":
    section_heading(marker, "Map search")
    st.write(
        "The magnifying-glass control is in the upper-right corner of the map and allows you to enter an address of interest."
    )
    image("map_search.png", "Map search and the Find address or place box.")

    step(1, "Open the map search", "Click the magnifying-glass control in the upper-right corner of the map.")
    step(2, "Enter an address or place", "Type an address or place in the Find address or place search bar.")
    step(3, "Choose a matching result", "Select the matching result to move the map to that location.")
    step(4, "Close the search box", "Click the X symbol when you are finished.")


# -----------------------------------------------------------------------------
# QUICK WORKFLOW
# -----------------------------------------------------------------------------
elif marker == "Quick":
    section_heading(marker, "Quick workflow")
    st.write("For most searches, the following sequence is the easiest way to use the site.")
    st.markdown(
        """
        <div class="quick-grid">
          <div class="quick-card"><strong>1. Open the map</strong>Use the pins and map controls to understand the area you are viewing.</div>
          <div class="quick-card"><strong>2. Apply the filters</strong>Open the filter panel and select the services or languages you need.</div>
          <div class="quick-card"><strong>3. Narrow the area if needed</strong>Use the Location tool or Transportation Service Area when those views are helpful.</div>
          <div class="quick-card"><strong>4. Review a center on the map</strong>Click a service-center pin if you only need to inspect one center.</div>
          <div class="quick-card"><strong>5. Use View for the filtered list</strong>After the map has updated, click View to open the matching centers without the map.</div>
          <div class="quick-card"><strong>6. Search or browse the results</strong>Use Search within these results or Next/Previous depending on what you need.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
