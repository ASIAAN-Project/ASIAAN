import streamlit as st
import pandas as pd
import re
import requests
import warnings
import json

# ──────────────────────────────────────────────────────────────────────────────
# App / Warnings
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Feature Layer Manager", layout="wide")
warnings.filterwarnings("ignore", category=SyntaxWarning)

# ──────────────────────────────────────────────────────────────────────────────
# Secrets / Config
#   Make sure your .streamlit/secrets.toml has:
#     ADMIN_CODE="..."
#     USER_CODE="..."
#     ARCGIS_FEATURE_LAYER="https://.../FeatureServer/0"
#     ARCGIS_KEYWORDS_TABLE="https://.../FeatureServer/0"   # <-- Table URL
#     GOOGLE_MAPS_API_KEY="..."
# ──────────────────────────────────────────────────────────────────────────────
ACCESS_CODE = st.secrets["ADMIN_CODE"]
GUEST_CODE = st.secrets["USER_CODE"]
FEATURE_LAYER_URL = st.secrets["ARCGIS_FEATURE_LAYER"]        # feature layer
KEYWORDS_TABLE_URL = st.secrets["ARCGIS_KEYWORDS_TABLE"]       # dictionary table
API_KEY = st.secrets["GOOGLE_MAPS_API_KEY"]

# ──────────────────────────────────────────────────────────────────────────────
# ArcGIS REST helpers
# ──────────────────────────────────────────────────────────────────────────────
def query_layer(where="1=1", out_fields="*", return_geometry=False,
                return_all_records=False, return_count_only=False):
    """Generic query against the main Feature Layer."""
    params = {
        "where": where,
        "outFields": out_fields,
        "returnGeometry": str(return_geometry).lower(),
        "f": "json"
    }
    if return_all_records:
        params["returnAllRecords"] = "true"
    if return_count_only:
        params["returnCountOnly"] = "true"

    resp = requests.get(f"{FEATURE_LAYER_URL}/query", params=params)
    resp.raise_for_status()
    return resp.json()

def apply_edits(adds=None, updates=None, deletes=None):
    """Apply edits to the main Feature Layer."""
    url = f"{FEATURE_LAYER_URL}/applyEdits"
    body = {"f": "json"}
    if adds:
        body["adds"] = json.dumps(adds)
    if updates:
        body["updates"] = json.dumps(updates)
    if deletes:
        body["deletes"] = deletes if isinstance(deletes, str) else ",".join(map(str, deletes))
    resp = requests.post(url, data=body)
    resp.raise_for_status()
    return resp.json()

@st.cache_data(ttl=3600, show_spinner=False)
def get_layer_schema():
    """Fetch the feature layer schema."""
    resp = requests.get(FEATURE_LAYER_URL, params={"f": "json"})
    resp.raise_for_status()
    return resp.json().get("fields", [])

# ──────────────────────────────────────────────────────────────────────────────
# Keyword dictionary (Service → Keywords)  ← NEW
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def load_service_keyword_dict():
    """
    Read the hosted keywords table and build:
      {
        "Home_Health_Services": ["term1", "term2", ...],
        "Assisted_Living":     ["..."],
        ...
      }
    The table should have at least fields: Service_Field, Keywords (comma-separated phrases).
    """
    params = {
        "f": "json",
        "where": "1=1",
        "outFields": "Service_Field,Keywords",
        "returnGeometry": "false",
        "returnAllRecords": "true"
    }
    resp = requests.get(f"{KEYWORDS_TABLE_URL}/query", params=params)
    resp.raise_for_status()
    data = resp.json()

    mapping = {}
    for feat in data.get("features", []):
        attrs = feat.get("attributes", {})
        svc  = attrs.get("Service_Field")
        keys = attrs.get("Keywords", "") or ""
        if not svc:
            continue
        # split by comma, normalize spacing; keep phrases as-is for search
        terms = [t.strip() for t in keys.split(",") if t.strip()]
        mapping[svc] = terms
    return mapping

def build_search_terms(attributes: dict) -> str:
    """
    Compose Search_Terms for one row using:
      - Agency/Address (if present)
      - Keywords from dictionary for each service flag == 1

    Returns a single comma-separated string (≤ 2000 chars is fine in ArcGIS).
    """
    dictionary = load_service_keyword_dict()

    tokens = []

    # Add agency name + address so address/name searches still work in Experience
    for base in ("Agency_Name", "Address"):
        val = attributes.get(base)
        if val:
            tokens.append(str(val))

    # Include keywords for each service=1
    for svc in binary_fields_list():
        try:
            flag_val = attributes.get(svc)
            # ArcGIS can store 1/0 as number or string; treat truthy 1
            is_on = (str(flag_val) == "1" or flag_val == 1 or flag_val is True)
            if is_on and svc in dictionary:
                tokens.extend(dictionary[svc])
        except Exception:
            # If field missing or malformed, just skip
            pass

    # Remove dupes while preserving order
    seen = set()
    deduped = []
    for t in tokens:
        if t not in seen:
            seen.add(t)
            deduped.append(t)

    return ", ".join(deduped)

# ──────────────────────────────────────────────────────────────────────────────
# Editable fields / Binary service list (unchanged)
# ──────────────────────────────────────────────────────────────────────────────
def editable_field_names():
    """All editable non-system, non-custom field names based on schema."""
    fields = get_layer_schema()
    exclude = {
        "ObjectId", "OBJECTID", "GlobalID", "GlobalId", "Shape",
        "Shape_Area", "Shape_Length", "CreationDate", "Creator",
        "EditDate", "Editor"
    }
    # controls we already render via custom UI
    custom = {"Name", "Phone_number", "Address", "Address_w_suit__", "Latitude", "Longitude"}
    names = [f["name"] for f in fields]
    return [n for n in names if n not in exclude and n not in custom]

def binary_fields_list():
    return [
        'Home_Health_Services','Adult_Day_Services','Benefits_Counseling','Elder_Housing_Resources',
        'Assisted_Living','Elder_Abuse','Home_Repair','Immigration_Assistance',
        'Long_term_Care_Ombudsman','Long_term_Care_Nursing_Homes','Senior_Exercise_Programs',
        'Dementia_Support_Programs','Transportation','Senior_Centers','Caregiver_Support_Services',
        'Case_Management','Congregate_Meals','Financial_Counseling','Health_Education_Workshops',
        'Home_Delivered_Meals','Hospice_Care','Technology_Training','Cultural_Programming',
        'Mental_Health','Vaccinations_Screening','Outreach_and_Advocacy','Lending_Closet',
        'Independent_Living','Homemakers_Personal_Support','Independent_Housing'
    ]

# ──────────────────────────────────────────────────────────────────────────────
# Phone normalizer (unchanged)
# ──────────────────────────────────────────────────────────────────────────────
def normalize_phone(raw: str) -> tuple[str, str | None]:
    """Accept digits or formatted; return 123-456-7890 or error."""
    if not raw:
        return "", None
    digits = re.sub(r"\D", "", raw)
    if len(digits) == 10:
        return f"{digits[0:3]}-{digits[3:6]}-{digits[6:10]}", None
    return raw, "📞 Invalid phone number. Enter 10 digits."

# ──────────────────────────────────────────────────────────────────────────────
# Session setup (unchanged)
# ──────────────────────────────────────────────────────────────────────────────
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'login_mode' not in st.session_state:
    st.session_state.login_mode = "guest"
if 'selected_record' not in st.session_state:
    st.session_state.selected_record = {}
if "page" not in st.session_state:
    st.session_state.page = "view"

# fetch counts once
if "total_count" not in st.session_state:
    count_result = query_layer(return_count_only=True).get("count", 0)
    st.session_state.total_count = count_result

# Address suggestor state
st.session_state.setdefault("new_address", "")
st.session_state.setdefault("new_lat", "")
st.session_state.setdefault("new_lng", "")
st.session_state.setdefault("update_address", "")
st.session_state.setdefault("update_lat", "")
st.session_state.setdefault("update_lng", "")

# ──────────────────────────────────────────────────────────────────────────────
# Login (unchanged)
# ──────────────────────────────────────────────────────────────────────────────
def login_page():
    st.title("🔐 ArcGIS Data Entry App")
    st.write("Please enter the access code to continue.")
    code = st.text_input("Access Code", type="password")
    if st.button("Login"):
        if code == ACCESS_CODE:
            st.session_state.logged_in = True
            st.session_state.login_mode = "admin"
            st.rerun()
        elif code == GUEST_CODE:
            st.session_state.logged_in = True
            st.session_state.login_mode = "guest"
            st.rerun()
        else:
            st.error("Invalid access code. Please try again.")

# ──────────────────────────────────────────────────────────────────────────────
# Table view (unchanged)
# ──────────────────────────────────────────────────────────────────────────────
def feature_layers_viewer():
    st.title("✅ Welcome to the Feature Layer Editor")
    st.success("You're logged in!")

    with st.spinner("Fetching data from ArcGIS..."):
        j = query_layer(where="1=1", out_fields="*", return_geometry=False, return_all_records=True)
        raw_data = [feat["attributes"] for feat in j.get("features", [])]
        df = pd.DataFrame(raw_data)

    st.subheader("Service Centers")
    st.dataframe(df, height=500, use_container_width=True)

    if not df.empty:
        selected_index = st.number_input("🔍 Enter row number to edit or delete:",
                                         min_value=0, max_value=len(df) - 1, step=1)
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("✏️ Edit Selected Entry",
                         disabled=(st.session_state.login_mode != "admin")):
                # Reset address state for fresh edit
                st.session_state.update_address = ""
                st.session_state.update_lat = ""
                st.session_state.update_lng = ""

                st.session_state.selected_record = df.loc[selected_index].to_dict()
                st.session_state.object_id = (
                    df.loc[selected_index].get('ObjectId') or df.loc[selected_index].get('OBJECTID')
                )
                st.session_state.page = 'edit'
                st.rerun()

        with col2:
            if st.button("🗑️ Delete Selected Entry",
                         disabled=(st.session_state.login_mode != "admin")):
                object_id_to_delete = (
                    df.loc[selected_index].get('ObjectId') or df.loc[selected_index].get('OBJECTID')
                )
                try:
                    result = apply_edits(deletes=str(object_id_to_delete))
                    success = result.get("deleteResults", [{}])[0].get("success", False)
                    if success:
                        st.success(f"✅ Entry with ObjectId {object_id_to_delete} deleted successfully!")
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to delete entry with ObjectId {object_id_to_delete}.")
                except Exception as e:
                    st.error(f"❌ Error during deletion: {e}")

        with col3:
            if st.button("➕ Create New Entry",
                         disabled=(st.session_state.login_mode != "admin")):
                # Reset address state for fresh create
                st.session_state.new_address = ""
                st.session_state.new_lat = ""
                st.session_state.new_lng = ""

                st.session_state.selected_record = {}
                st.session_state.page = "create"
                st.rerun()

# ──────────────────────────────────────────────────────────────────────────────
# Google helpers (unchanged)
# ──────────────────────────────────────────────────────────────────────────────
def get_lat_lng_from_address(address: str):
    endpoint = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": API_KEY}
    response = requests.get(endpoint, params=params)
    data = response.json()
    if data.get("status") == "OK" and data.get("results"):
        location = data["results"][0]["geometry"]["location"]
        return location["lat"], location["lng"]
    else:
        raise Exception(f"Geocoding failed: {data.get('status')} - {data.get('error_message', '')}")

def get_place_suggestions(input_text):
    url = "https://maps.googleapis.com/maps/api/place/autocomplete/json"
    params = {"input": input_text, "key": API_KEY, "types": "address"}
    response = requests.get(url, params=params)
    suggestions = response.json().get("predictions", [])
    return [s['description'] for s in suggestions]

# ──────────────────────────────────────────────────────────────────────────────
# Create page  (adds Search_Terms before submit)
# ──────────────────────────────────────────────────────────────────────────────
def show_create_page():
    st.title("➕ Create New Feature Entry")

    # address search
    address_input = st.text_input("🔍 Search Address",
                                  value=st.session_state.new_address,
                                  key="new_address_input")
    suggestions = get_place_suggestions(address_input) if len(address_input.strip()) >= 3 else []
    if suggestions:
        choices = ["-- Select an address --"] + suggestions
        pick = st.selectbox("📍 Suggestions", choices, index=0, key="create_address_suggestion")
        if pick != "-- Select an address --" and pick != st.session_state.new_address:
            st.session_state.new_address = pick
            lat, lng = get_lat_lng_from_address(pick)
            st.session_state.new_lat = str(lat)
            st.session_state.new_lng = str(lng)
            st.rerun()

    binary_fields = set(binary_fields_list())
    other_schema_fields = [f for f in editable_field_names() if f not in binary_fields]

    new_entry = {}
    errors = []

    with st.form("create_form"):
        # Core identity/contact
        new_entry["Agency_Name"] = st.text_input("Name / Agency_Name")
        phone_raw = st.text_input("Phone Number (any format with 10 digits)")
        phone_fmt, phone_err = normalize_phone(phone_raw)
        new_entry["Phone_number"] = phone_fmt
        if phone_err:
            errors.append(phone_err)

        new_entry["Address"] = st.text_input("Address", value=st.session_state.new_address, disabled=True)
        new_entry["Address_w_suit__"] = st.text_input("Address with Suite")

        col1, col2 = st.columns(2)
        with col1:
            new_entry["Latitude"] = st.text_input("Latitude", value=st.session_state.new_lat, disabled=True)
        with col2:
            new_entry["Longitude"] = st.text_input("Longitude", value=st.session_state.new_lng, disabled=True)

        # Additional schema-driven fields (e.g., Website, Contact_name, etc.)
        st.markdown("### Additional Details")
        for fname in other_schema_fields:
            new_entry[fname] = st.text_input(fname, key=f"create_{fname}")

        # Binary/coded fields
        st.markdown("### 🧩 Service Availability Fields")
        bin_list = list(binary_fields)
        for i in range(0, len(bin_list), 5):
            cols = st.columns(5)
            for j in range(5):
                if i + j < len(bin_list):
                    field = bin_list[i + j]
                    with cols[j]:
                        new_entry[field] = st.selectbox(field, [0, 1], index=0, key=f"new_{field}")

        submitted = st.form_submit_button("✅ Submit New Entry")

    if submitted:
        if errors:
            for err in errors:
                st.error(err)
            return
        try:
            # geometry
            lat = float(st.session_state.new_lat) if st.session_state.new_lat else None
            lon = float(st.session_state.new_lng) if st.session_state.new_lng else None

            # Clean empty strings -> None
            attributes = {k: (v if v != "" else None) for k, v in new_entry.items()}

            # ►► Keyword Search: compute Search_Terms from dictionary and service flags
            attributes["Search_Terms"] = build_search_terms(attributes)

            feature = {"attributes": attributes}
            if lat is not None and lon is not None:
                feature["geometry"] = {"x": lon, "y": lat, "spatialReference": {"wkid": 4326}}

            response = apply_edits(adds=[feature])
            if response.get('addResults', [{}])[0].get("success"):
                st.success("✅ New entry added successfully!")
                # Reset address state
                st.session_state.new_address = ""
                st.session_state.new_lat = ""
                st.session_state.new_lng = ""
                st.session_state.page = "view"
                st.rerun()
            else:
                st.error("❌ Failed to add new entry.")
        except Exception as e:
            st.error(f"❌ Error: {e}")

    if st.button("⬅️ Back to Table"):
        # Reset address state when going back
        st.session_state.new_address = ""
        st.session_state.new_lat = ""
        st.session_state.new_lng = ""
        st.session_state.page = 'view'
        st.rerun()

# ──────────────────────────────────────────────────────────────────────────────
# Edit page  (adds Search_Terms before update)
# ──────────────────────────────────────────────────────────────────────────────
def show_edit_page():
    st.title("✏️ Edit Feature Entry")

    binary_fields = set(binary_fields_list())
    other_schema_fields = [f for f in editable_field_names() if f not in binary_fields]

    # Initialize update address from selected record if empty
    if not st.session_state.update_address:
        st.session_state.update_address = st.session_state.selected_record.get("Address", "")
    if not st.session_state.update_lat:
        st.session_state.update_lat = str(st.session_state.selected_record.get("Latitude", ""))
    if not st.session_state.update_lng:
        st.session_state.update_lng = str(st.session_state.selected_record.get("Longitude", ""))

    # Address suggestor
    user_input = st.text_input("🔍 Search Address", value=st.session_state.update_address, key="edit_address_input")
    suggestions = get_place_suggestions(user_input) if len(user_input.strip()) >= 3 else []
    if suggestions:
        choices = ["-- Select an address --"] + suggestions
        pick = st.selectbox("📍 Suggestions", choices, index=0, key="edit_address_suggestion")
        if pick != "-- Select an address --" and pick != st.session_state.update_address:
            st.session_state.update_address = pick
            lat, lng = get_lat_lng_from_address(pick)
            st.session_state.update_lat = str(lat)
            st.session_state.update_lng = str(lng)
            st.rerun()

    edited = {}
    errors = []

    with st.form("edit_form"):
        # collect existing fields
        binary_inputs = {}
        for key, value in st.session_state.selected_record.items():
            if key in ['ObjectId', 'OBJECTID', 'GlobalID', 'GlobalId']:
                st.text_input(f"{key} (read-only)", str(value), disabled=True)
                edited[key] = value

            elif key == 'Phone_number':
                phone_raw = st.text_input("Phone Number (any format with 10 digits)", str(value or ""))
                phone_fmt, phone_err = normalize_phone(phone_raw)
                edited[key] = phone_fmt
                if phone_err:
                    errors.append(phone_err)

            elif key in binary_fields:
                binary_inputs[key] = value  # delay render for grouped layout

            elif key == "Address":
                edited[key] = st.text_input("Address", value=st.session_state.update_address, disabled=True)

            elif key == "Address_w_suit__":
                edited[key] = st.text_input("Address w/ Suite", str(value or ""))

            elif key == "Latitude":
                edited[key] = st.text_input("Latitude", value=st.session_state.update_lat, disabled=True)

            elif key == "Longitude":
                edited[key] = st.text_input("Longitude", value=st.session_state.update_lng, disabled=True)

            else:
                edited[key] = st.text_input(key, str(value if value is not None else ""))

        # render any schema fields that weren't on this record yet
        missing = [n for n in other_schema_fields if n not in edited]
        if missing:
            st.markdown("### Additional Details")
            for fname in missing:
                edited[fname] = st.text_input(fname, key=f"edit_{fname}", value="")

        # binary fields in grid
        st.markdown("### 🧩 Service Availability Fields")
        bin_keys = sorted(list(binary_fields))
        for i in range(0, len(bin_keys), 5):
            cols = st.columns(5)
            for j in range(5):
                if i + j < len(bin_keys):
                    key = bin_keys[i + j]
                    with cols[j]:
                        raw = binary_inputs.get(key, 0)
                        default = int(raw) if raw not in (None, "") else 0
                        edited[key] = st.selectbox(key, [0, 1], index=default)

        submitted = st.form_submit_button("✅ Push Update")

    if submitted:
        if errors:
            for err in errors:
                st.error(err)
        else:
            try:
                lat_str = st.session_state.update_lat.strip() if st.session_state.update_lat else ""
                lng_str = st.session_state.update_lng.strip() if st.session_state.update_lng else ""

                # clean empty strings -> None
                attrs = {k: (v if v != "" else None) for k, v in edited.items()}

                # ►► Keyword Search: recompute Search_Terms for this row
                attrs["Search_Terms"] = build_search_terms(attrs)

                feature = {"attributes": attrs}
                if lat_str and lng_str:
                    feature["geometry"] = {
                        "x": float(lng_str),
                        "y": float(lat_str),
                        "spatialReference": {"wkid": 4326},
                    }

                response = apply_edits(updates=[feature])
                if response.get('updateResults', [{}])[0].get('success'):
                    st.success("✅ Entry successfully updated!")
                    # Reset address state after successful update
                    st.session_state.update_address = ""
                    st.session_state.update_lat = ""
                    st.session_state.update_lng = ""
                else:
                    st.error("❌ Update failed. Please check your inputs or field types.")
            except Exception as e:
                st.error(f"❌ An error occurred: {e}")

    if st.button("⬅️ Back to Table"):
        # Reset address state when going back
        st.session_state.update_address = ""
        st.session_state.update_lat = ""
        st.session_state.update_lng = ""
        st.session_state.page = 'view'
        st.rerun()

# ──────────────────────────────────────────────────────────────────────────────
# App flow (unchanged)
# ──────────────────────────────────────────────────────────────────────────────
if st.session_state.logged_in:
    if st.session_state.page == 'view':
        feature_layers_viewer()
    elif st.session_state.page == 'edit':
        show_edit_page()
    elif st.session_state.page == 'create':
        show_create_page()
else:
    login_page()
