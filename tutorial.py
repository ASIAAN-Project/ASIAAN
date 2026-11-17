    step(
        5,
        "Or choose specific centers",
        "In the list below, check the Select box beside each service center you want to include.",
    )

    step(
        6,
        "Download the selected centers",
        "After at least one center is selected, click Download selected service centers as PDF. "
        "If no center is selected, this button remains disabled.",
    )

    st.markdown(
        '<div class="callout"><strong>If you do not need a PDF:</strong> '
        'Leave the PDF section collapsed and scroll down to read the service-center details on screen.</div>',
        unsafe_allow_html=True,
    )

    st.markdown("### 3. Search and move through the filtered results")
    image(
        "view_03_search_and_pagination.png",
        "Search, page navigation, and the start of a service-center card.",
        width=920,
    )

    step(
        7,
        "Search within the filtered results",
        "Click inside Search within these results. "
        "Enter a service-center name, address, language, or available service. "
        "This search only works within the centers that already matched the filters from the map.",
    )

    step(
        8,
        "Clear the search text to return to all filtered results",
        "Removing the text restores the full set of centers from the current View page.",
    )

    step(
        9,
        "Move through the results",
        "The page shows a small group at a time, such as Showing 1-5 of 41. "
        "Click Next to move to the next group of service centers. "
        "Click Previous to return to the earlier group. "
        "The page number appears between the buttons.",
    )

    st.markdown("### 4. Read each service-center card")
    image(
        "view_04_center_and_services.png",
        "Service-center card showing contact information and Services provided.",
        width=820,
    )

    step(
        10,
        "Start with the center name and Location",
        "The center name appears at the top. "
        "The Location box shows the address and suite/unit information when available.",
    )

    step(
        11,
        "Open directions",
        "Use Get directions with Google Maps or Get directions with Apple Maps.",
    )

    step(
        12,
        "Use the phone number",
        "The phone number appears in its own box and can be selected as a call link on supported devices.",
    )

    step(
        13,
        "Check the available languages",
        "The Languages box lists the languages recorded for that center.",
    )

    step(
        14,
        "Open the website",
        "Click Visit website when a website is available.",
    )

    step(
        15,
        "Read Services provided",
        "Only services that the center provides are listed in this section. "
        "Services marked as unavailable are not shown here, which makes the list easier to scan.",
    )

    st.markdown(
        '<div class="callout"><strong>Why this page can be easier to use:</strong> '
        'The View page keeps the center name, location, phone, languages, website, and available services in separate sections, '
        'so you do not need to open and scroll through individual map pop-ups.</div>',
        unsafe_allow_html=True,
    )

elif marker == "I":
    annotated_map_reference()
    section_heading(marker, "Map search")

    st.write(
        "The magnifying-glass control is in the upper-right corner of the map and allows you to enter an address of interest."
    )

    image(
        "map_search.png",
        "Map search and the Find address or place box.",
    )

    step(1, "Open the map search", "Click the magnifying-glass control in the upper-right corner of the map.")
    step(2, "Enter an address or place", 'Type an address or place in the "Find address or place" search bar.')
    step(3, "Choose a matching result", "Select the matching result to move the map to that location.")
    step(4, "Close the search box", "Click the X symbol when you are finished.")

elif marker == "Quick":
    annotated_map_reference()
    section_heading(marker, "Quick workflow")

    st.write(
        "For most searches, the following sequence is the easiest way to use the site."
    )

    st.markdown(
        """
        <div class="quick-grid">
          <div class="quick-card"><strong>1. Open the map</strong>Use the pins and map controls to understand the area you are viewing.</div>
          <div class="quick-card"><strong>2. Apply the filters</strong>Open the filter panel and select the services or languages you need.</div>
          <div class="quick-card"><strong>3. Narrow the area if needed</strong>Use the Location tool or Transportation Service Area when those views are helpful.</div>
          <div class="quick-card"><strong>4. Review a center on the map</strong>Click a service-center pin if you only need to inspect one center.</div>
          <div class="quick-card"><strong>5. Use View for the filtered list</strong>After the map has updated, click View to open the matching centers without the map.</div>
          <div class="quick-card"><strong>6. Search, browse, or download</strong>Use Search within these results, Next/Previous, or the PDF section depending on what you need.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
