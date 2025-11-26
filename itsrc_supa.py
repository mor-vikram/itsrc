# streamlit_app_supabase.py
from time import time
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from io import BytesIO
from fpdf import FPDF
from textwrap import wrap
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from PIL import Image
import re, random, os, json
from dotenv import load_dotenv
from pdf_gen import generate_participant_pdf
from streamlit.components.v1 import html
import base64
from pathlib import Path
from reportlab.lib.pagesizes import A5
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from streamlit.components.v1 import html

st.set_page_config(
    page_title="Sports Meet Registration",
    page_icon="🏆",
    layout="wide",  # or "wide"
    initial_sidebar_state="collapsed"
)

if "active_page" not in st.session_state:
    st.session_state.active_page = "Participant Registration"

# --- Safely load and encode logo.jpg ---
logo_path = Path("its.gif")
if logo_path.exists():
    with open(logo_path, "rb") as f:
        logo_base64 = base64.b64encode(f.read()).decode()
    logo_img_html = f'<img src="data:image/png;base64,{logo_base64}" alt="ITSRC Logo" class="nav-logo">'
else:
    logo_img_html = '<div style="font-weight:bold;font-size:18px;color:#00695c;">ITSRC</div>'

# --- Define menu options ---
menu_items = [
    "Admin Login",
    "Admin Dashboard",
    "Participant Registration",
    "Already Registered (Re-print/Modify)",    
    "Insight",
    "Events Schedule",
    "Doubles Partner Selection",
    "Leadership Board"
]
##Header 3 style
st.markdown("""
    <style>
    /* Change the font style for all subheaders */
    h3 {
        font-family: 'Poppins', sans-serif;
        color: #008080; /* teal */
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Style ---
# --- Global header + menu style ---
st.markdown("""
<style>

    /* Header logos (left & right) */
    .nav-logo {
        height: 150px;
        width: 150px;
        border-radius: 8px;
        object-fit: contain;
    }

    /* Big centered title */
    .navbar-title {
        font-family: 'Poppins', sans-serif;
        font-size: 40px;
        font-weight: 700;
        color: #004d40;
        text-align: center;
        margin-top: 16px;
        margin-bottom: 4px;
    }

    /* Teal strip under the title */
    .navbar {
        width: 100%;
        height: 10px;
        background-color: #00bfa6;
        margin-top: 4px;
        margin-bottom: 24px;
    }

    /* Center contents of st.columns used for the menu row */
    div[data-testid="stHorizontalBlock"] > div {
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* Uniform menu buttons */
    .stButton button {
        background-color: #D3AF37 !important;
        color: #004d40 !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        border-radius: 10px !important;
        border: 2px solid #00bfa6 !important;
        box-shadow: 0 0 10px #00bfa6;
        transition: box-shadow 0.3s ease-in-out;
        /* same size for all buttons */
        width: 170px !important;
        height: 55px !important;

        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;

        line-height: 1.2 !important;
        white-space: normal !important;   /* allow 2-line labels cleanly */
        overflow-wrap: break-word;
        border: none !important;
        margin-top: 8px !important;
    }

    .stButton button:hover {
        background-color: #ffe082 !important;
        color: black !important;
    }

    /* Hover effect for normal (non-active) menu buttons */
    .stButton button:hover {
        background-color: #e8d175 !important;   /* lighter gold */
        border: 2px solid #00bfa6 !important;
        transform: scale(1.02);
        transition: 0.2s ease;
    }
        

    /* 🔹 Active (selected) menu button styling */
    .active-btn button {
        background-color: #004d40 !important;
        color: #ffffff !important;
        border: 2px solid #00c9a7 !important;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.15);
        transform: scale(1.03);
        transition: all 0.2s ease-in-out;
    }


</style>
""", unsafe_allow_html=True)

# --- Style --- Tabs as Buttons ---
st.markdown("""
<style>

/* 🔹 Make all st.tabs look like buttons (Admin Dashboard, Insight, etc.) */

.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;                      /* space between "buttons" */
    border-bottom: none;              /* hide default underline */
}

.stTabs [data-baseweb="tab"] {
    background-color: #D3AF37;        /* same gold as your menu buttons */
    color: #004d40;
    border-radius: 999px;             /* pill / button shape */
    padding: 0.4rem 1.1rem;
    font-weight: 600;
    font-size: 14px;
    border: 2px solid #00bfa6;        /* teal border */
    box-shadow: 0 2px 4px rgba(0,0,0,0.08);
    cursor: pointer;
}

/* Active tab = filled teal button */
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background-color: #004d40;
    color: #ffffff;
    border-color: #00c9a7;
    box-shadow: 0 3px 6px rgba(0,0,0,0.15);
}

/* Hover effect */
.stTabs [data-baseweb="tab"]:hover {
    filter: brightness(1.05);
}

</style>
""", unsafe_allow_html=True)

st.markdown("""<div class='navbar'></div>""", unsafe_allow_html=True)
# --- Navbar layout ---
col1, col2, col3 = st.columns([1.5, 6, 1.5])
with col1:
    st.markdown(logo_img_html, unsafe_allow_html=True)
with col2:
    st.markdown('<div class="navbar-title" style="text-align:center;">Income Tax Sports & Recreation Club, Vadodara</div>', unsafe_allow_html=True)
    st.markdown('<div class="navbar-title" style="text-align:center;">(Sports Events @2025-26)</div>', unsafe_allow_html=True)
with col3:
    st.markdown(logo_img_html, unsafe_allow_html=True)

st.markdown("""<div class='navbar'></div>""", unsafe_allow_html=True)


# --- Horizontal menu buttons (Streamlit native) ---

menu_cols = st.columns(len(menu_items))

# Decide which page is active
selected_page = (
    st.session_state.get("active_page")
    or st.query_params.get("page", "Participant Registration")
)

for i, item in enumerate(menu_items):
    is_active = (item == selected_page)

    with menu_cols[i]:
        # Wrap active button in a div so CSS .active-btn button applies
        if is_active:
            st.markdown("<div class='active-btn'>", unsafe_allow_html=True)

        clicked = st.button(item, key=f"menu_{i}", use_container_width=True)

        if is_active:
            st.markdown("</div>", unsafe_allow_html=True)

        if clicked:
            st.session_state.active_page = item
            st.query_params["page"] = item
            st.rerun()


# --- Use selected page as the active menu variable ---
#menu = selected_page
#menu = st.session_state.get("active_page", "Participant Registration")

# --- Card container for main content (visual only) ---
st.markdown("""
    <style>
        .main-card {
            background-color: lightgray;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.05);
            padding: 2rem;
            margin: 2rem auto;
            max-width: 1100px;
        }
    </style>
""", unsafe_allow_html=True)

# keep this as the *only* source of truth for current tab:
menu = st.session_state.get("active_page", "Participant Registration")





# Supabase client
from supabase import create_client, client



# Load env if present
load_dotenv()

# Get keys from Streamlit secrets first, then environment
SUPABASE_URL = st.secrets.get("SUPABASE_URL", None) or os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = st.secrets.get("SUPABASE_ANON_KEY", None) or os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = st.secrets.get("SUPABASE_SERVICE_ROLE_KEY", None) or os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_ANON_KEY or not SUPABASE_SERVICE_ROLE_KEY:
    st.warning("Supabase keys not set. Please add SUPABASE_URL, SUPABASE_ANON_KEY and SUPABASE_SERVICE_ROLE_KEY to secrets or environment.")
    # Continue but many features will error until keys provided.

# Create two clients:
#  - anon_client for auth flows (uses anon key)
#  - svc_client for server-side DB operations (uses service role key)
anon_client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY) if SUPABASE_URL and SUPABASE_ANON_KEY else None
svc_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY) if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY else None



# ---------------------
# App config / state
# ---------------------
#st.set_page_config(page_title="ITSRC Sports Registration (Supabase)", page_icon="🏅", layout="wide")

if "user" not in st.session_state:
    st.session_state["user"] = None  # store logged-in user info (email, id, etc.)

# Houses list etc.
houses = ["CC Challengers", "JAO Giants", "Faceless Fighters", "Investigation Warriors"]
tshirt_sizes = ["S", "M", "L", "XL", "XXL", "XXXL"]

event_details = {
    "Cricket": ["Cricket"],
    "Badminton": ["Badminton Singles", "Badminton Doubles", "Badminton Mixed Doubles"],
    "Badminton (Veteran)": ["Badminton Singles (Veteran)", "Badminton Doubles (Veteran)", "Badminton Mixed Doubles (Veteran)"],
    "Table Tennis": ["Table Tennis Singles", "Table Tennis Doubles", "Table Tennis Mixed Doubles"],
    "Table Tennis (Veteran)": ["Table Tennis Singles (Veteran)", "Table Tennis Doubles (Veteran)", "Table Tennis Mixed Doubles (Veteran)"],
    "Carom": ["Carom Singles", "Carom Doubles"],
    "Volleyball": ["Volleyball"],
    "Chess": ["Chess"],
    "Pickle ball": ["Pickle ball Doubles"],
    "Cycling": ["Slow Cycling"],
    "Walkathon": ["2.2 Km Walk"],
    "Races": ["100 meter", "200 meter", "400 meter", "400 Meter Relay"],
    "Races (Veteran)": ["100 meter (Veteran)", "200 meter (Veteran)", "400 meter (Veteran)", "400 Meter Relay (Veteran)"],
    "Tug of War": ["Tug of War"]
}


# ---------------------
# Helper: Supabase CRUD wrappers
# ---------------------
def insert_participant(reg):
    """Insert registration dict into participants table (uses service role client)."""
    try:
        payload = {
            "name": reg["Name"],
            "age": reg["Age"],
            "gender": reg["Gender"],
            "house": reg["House"],
            "designation": reg["Designation"],
            "posting_details": reg["Posting Details"],
            "contact": reg["Contact"],
            "tshirt_size": reg["T-shirt Size"],
            "all_selected_events": reg["All Selected Events"],
            "selected_events": json.dumps(reg["Selected Events"]),
            "fee": reg["Fee"],
            "date_of_reg": reg["Date of Reg."],
            # NEW: workflow fields
            "status": "Pending",          # initial status
            "fee_collected": False,       # will be True after house in-charge approves
        }
        resp = svc_client.table("participants").insert(payload).execute()
        return resp
    except Exception as e:
        st.error(f"Error saving participant to Supabase: {e}")
        return None

def load_all_participants_df():
    """Load participants into a pandas DataFrame."""
    try:
        resp = svc_client.table("participants").select("*").order("date_of_reg", desc=False).execute()
        data = resp.data or []
        if data:
            df = pd.DataFrame(data)
            # If selected_events is JSON string, parse it
            if "selected_events" in df.columns:
                df["Selected Events"] = df["selected_events"].apply(lambda x: json.loads(x) if x and isinstance(x, str) else x)
            # Keep compatibility with legacy 'All Selected Events'
            if "all_selected_events" in df.columns:
                df["All Selected Events"] = df["all_selected_events"]
            # Normalize contact
            if "contact" in df.columns:
                df["Contact"] = df["contact"].astype(str).str.strip()
            return df
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading participants: {e}")
        return pd.DataFrame()

def get_participant_by_contact(contact):
    try:
        resp = svc_client.table("participants").select("*").eq("contact", contact).execute()
        data = resp.data or []
        if data:
            df = pd.DataFrame(data)
            if "selected_events" in df.columns:
                df["Selected Events"] = df["selected_events"].apply(lambda x: json.loads(x) if x and isinstance(x, str) else x)
            if "all_selected_events" in df.columns:
                df["All Selected Events"] = df["all_selected_events"]
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching participant: {e}")
        return pd.DataFrame()

# ---------------------
# Supabase helper: Get participant by record ID
# ---------------------
def get_participant_by_id(record_id):
    try:
        if not svc_client:
            st.error("Supabase service client not configured.")
            return pd.DataFrame()
        resp = svc_client.table("participants").select("*").eq("id", record_id).execute()
        data = resp.data or []
        if data:
            # Return a DataFrame for consistency with get_participant_by_contact()
            return pd.DataFrame(data)
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching participant by ID: {e}")
        return pd.DataFrame()

# ---------------------

def update_participant_status(participant_id, status, approved_by=None, fee_collected=None):
    """
    Update participant workflow status (Pending/Approved/Rejected),
    and optionally set fee_collected + approved_by.
    """
    try:
        update_fields = {
            "status": status
        }
        if approved_by is not None:
            update_fields["approved_by"] = approved_by
            update_fields["approved_at"] = datetime.utcnow().isoformat()
        if fee_collected is not None:
            update_fields["fee_collected"] = fee_collected

        resp = svc_client.table("participants")\
                         .update(update_fields)\
                         .eq("id", participant_id)\
                         .execute()
        return resp
    except Exception as e:
        st.error(f"Error updating participant status: {e}")
        return None
# ---------------------
# Winners
def load_winners_df():
    try:
        resp = svc_client.table("winners").select("*").order("created_at", desc=False).execute()
        data = resp.data or []
        return pd.DataFrame(data) if data else []
    except Exception as e:
        st.error(f"Error loading winners: {e}")
        return []

def upsert_winner(event_name, category, positions_dict):
    """
    positions_dict: e.g. {"1st": ("Name", "House"), "2nd": ... , "3rd": ...}
    We'll insert rows into winners table (one per position).
    """
    try:
        # Remove existing winners for same event+category first
        svc_client.table("winners").delete().eq("event_name", event_name).eq("category", category).execute()
        # Insert new ones
        inserts = []
        for pos, (name, house) in positions_dict.items():
            if name:
                inserts.append({
                    "event_name": event_name,
                    "category": category,
                    "position": pos,
                    "winner_name": name,
                    "house": house
                })
        if inserts:
            svc_client.table("winners").insert(inserts).execute()
        return True
    except Exception as e:
        st.error(f"Error saving winners: {e}")
        return False

# Draws
def save_match_draw(event_name, gender, df_pairs):
    """
    df_pairs: list of (team1, team2) tuples or DataFrame rows
    """
    try:
        # delete existing for event+gender to avoid duplicates if re-generating
        svc_client.table("match_draws").delete().eq("event_name", event_name).eq("gender", gender).execute()
        to_insert = []
        for i, row in enumerate(df_pairs):
            team1, team2 = row[0], row[1]
            to_insert.append({
                "event_name": event_name,
                "gender": gender,
                "round": i+1,
                "team1": team1,
                "team2": team2
            })
        if to_insert:
            svc_client.table("match_draws").insert(to_insert).execute()
        return True
    except Exception as e:
        st.error(f"Error saving match draw: {e}")
        return False

def load_draws_for_event(event_name):
    try:
        resp = svc_client.table("match_draws").select("*").eq("event_name", event_name).order("round", desc=False).execute()
        data = resp.data or []
        return pd.DataFrame(data) if data else pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading draws: {e}")
        return pd.DataFrame()

# Doubles partners
def save_partner_pair(part):
    try:
        svc_client.table("doubles_partners").insert(part).execute()
        return True
    except Exception as e:
        st.error(f"Error saving partner pair: {e}")
        return False

def load_pairs_for_event(event_name):
    try:
        resp = svc_client.table("doubles_partners").select("*").eq("event_name", event_name).execute()
        data = resp.data or []
        return pd.DataFrame(data) if data else pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading pairs: {e}")
        return pd.DataFrame()

# ---------- Doubles helpers ----------

def load_all_pairs():
    """Load all doubles pairs from the doubles_partners table."""
    try:
        # If your table doesn't have created_at, order by id instead
        resp = (
            svc_client
            .table("doubles_partners")
            .select("*")
            .order("id", desc=False)   # <-- changed from created_at to id
            .execute()
        )
        data = resp.data or []
        return pd.DataFrame(data) if data else pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading doubles pairs: {e}")
        return pd.DataFrame()



def delete_partner_pair(pair_id):
    """Delete a doubles pair by ID."""
    try:
        svc_client.table("doubles_partners").delete().eq("id", pair_id).execute()
        return True
    except Exception as e:
        st.error(f"Error deleting pair: {e}")
        return False


# ---------- Pair Slip PDF ----------



def generate_pair_slip_pdf(pair_data, logo_path="logo.jpg", output_path="pair_slip.pdf"):
    """
    Generate a simple A5 slip for a doubles pair.
    pair_data expects:
      - event_name, house
      - player1_name, player1_contact
      - player2_name, player2_contact
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A5, rightMargin=30, leftMargin=30, topMargin=40, bottomMargin=30)
    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph("<b>ITSRC Annual Sports 2025</b>", styles["Title"]))
    story.append(Paragraph("Doubles Pair Slip", styles["Heading2"]))
    story.append(Spacer(1, 8))

    # Basic info table
    table_data = [
        ["Event", pair_data.get("event_name", "")],
        ["House", pair_data.get("house", "")],
        ["Player 1", f"{pair_data.get('player1_name','')} ({pair_data.get('player1_contact','')})"],
        ["Player 2", f"{pair_data.get('player2_name','')} ({pair_data.get('player2_contact','')})"],
        ["Date", datetime.now().strftime("%d-%m-%Y")],
    ]
    table = Table(table_data, colWidths=[80, 200])
    table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("BACKGROUND", (0,0), (-1,0), colors.whitesmoke),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(table)
    story.append(Spacer(1, 12))
    story.append(Paragraph("<i>Organized by ITSRC Sports Committee</i>", styles["Normal"]))

    doc.build(story)
    buffer.seek(0)
    with open(output_path, "wb") as f:
        f.write(buffer.getvalue())
    return output_path

# Admin mapping loader
def get_admin_role_for_email(email):
    """
    Returns dict like:
        { "role": "Super Admin", "house": None }
        or
        { "role": "House Admin", "house": "CC Challengers" }
    """
    try:
        resp = svc_client.table("admins").select("role, house").eq("email", email).execute()
        data = resp.data or []
        if data:
            return data[0]
        return None
    except Exception as e:
        st.error(f"Error loading admin info: {e}")
        return None


# Leaderboard compute: compute from winners table
# Leaderboard compute: compute from winners table
def compute_leaderboard_from_winners():
    """
    Scoring Rules:
      • Individual Events → 1st = 5, 2nd = 3, 3rd = 1
      • Team Events (Cricket, Volleyball, Tug of War)
                         → 1st = 10, 2nd = 6, 3rd = 1
    """
    winners_raw = load_winners_df()   # may return DataFrame or []

    # Normalise to DataFrame
    if isinstance(winners_raw, pd.DataFrame):
        df = winners_raw.copy()
    elif winners_raw:
        df = pd.DataFrame(winners_raw)
    else:
        df = pd.DataFrame()

    if df.empty:
        # return zero-points table but still with ranks for all houses
        base = pd.DataFrame([{"House": h, "Points": 0} for h in houses])
        base["Rank"] = base["Points"].rank(method="min", ascending=False).astype(int)
        return base[["Rank", "House", "Points"]]

    required_cols = {"house", "event_name", "position"}
    if not required_cols.issubset(df.columns):
        missing = ", ".join(required_cols - set(df.columns))
        st.error(f"⚠️ Winners table format mismatch. Missing columns: {missing}")
        base = pd.DataFrame([{"House": h, "Points": 0} for h in houses])
        base["Rank"] = base["Points"].rank(method="min", ascending=False).astype(int)
        return base[["Rank", "House", "Points"]]

    # Points mapping
    individual_points = {"1st": 5, "2nd": 3, "3rd": 1}
    team_points       = {"1st": 10, "2nd": 6, "3rd": 1}

    # Team events list (exactly as stored in winners.event_name)
    team_events = {"Cricket", "Volleyball", "Tug of War"}

    def calculate_points(row):
        event = str(row["event_name"]).strip()
        position = str(row["position"]).strip()
        if event in team_events:
            return team_points.get(position, 0)
        return individual_points.get(position, 0)

    df["Points"] = df.apply(calculate_points, axis=1)

    # Aggregate by house
    leaderboard = (
        df.groupby("house")["Points"]
          .sum()
          .reset_index()
          .rename(columns={"house": "House"})
    )

    # Ensure all houses exist
    for h in houses:
        if h not in leaderboard["House"].values:
            leaderboard.loc[len(leaderboard)] = [h, 0]

    leaderboard = leaderboard.sort_values("Points", ascending=False).reset_index(drop=True)
    leaderboard["Rank"] = leaderboard["Points"].rank(method="min", ascending=False).astype(int)

    return leaderboard[["Rank", "House", "Points"]]


def make_status_chip_html(status_value):
    """Return a small colored status chip as HTML."""
    if not status_value:
        status_value = "Pending"
    status_str = str(status_value).strip().capitalize()

    if status_str == "Approved":
        bg = "#C8E6C9"   # light green
        fg = "#256029"
    elif status_str == "Rejected":
        bg = "#FFCDD2"   # light red
        fg = "#B71C1C"
    else:  # Pending or anything else
        status_str = "Pending"
        bg = "#FFF9C4"   # light yellow
        fg = "#827717"

    return f"""
        <span style="
            background-color:{bg};
            color:{fg};
            padding:2px 10px;
            border-radius:999px;
            font-size:12px;
            font-weight:600;
            white-space:nowrap;
            ">
            {status_str}
        </span>
    """

def add_status_chip_column(df):
    """
    Return a copy of df with a 'Status' chip column
    (HTML, to be rendered via df.to_html(escape=False)).
    """
    if df is None or df.empty:
        return df

    df_disp = df.copy()

    # ensure we have a 'status' column
    if "status" not in df_disp.columns:
        df_disp["status"] = "Pending"

    df_disp["Status"] = df_disp["status"].fillna("Pending")
    df_disp["Status Chip"] = df_disp["Status"].apply(make_status_chip_html)

    # Optional: move 'Status Chip' near the front
    cols = list(df_disp.columns)
    # make sure 'Status Chip' comes right after 'house' or 'name' if present
    for anchor in ["house", "name"]:
        if anchor in cols:
            cols.insert(cols.index(anchor) + 1, cols.pop(cols.index("Status Chip")))
            break

    # you can drop the raw 'status' column if you like:
    # if "status" in cols: cols.remove("status")
    # but I suggest keep it for filters/sorting:
    return df_disp[cols]


def render_status_summary(df, scope_label="All Houses"):
    """Show Total / Approved / Pending summary metrics for a given DataFrame."""
    if df is None or df.empty:
        st.info(f"No registration data available for {scope_label}.")
        return

    total = len(df)

    if "status" in df.columns:
        approved = (df["status"] == "Approved").sum()
        pending = (df["status"].fillna("Pending") == "Pending").sum()
    else:
        approved = 0
        pending = total

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("Total Registered", total)
    with col_b:
        st.metric("Approved", approved)
    with col_c:
        st.metric("Pending", pending)


# ---- status colouring + compact admin table helpers ----

def style_status_df(df):
    """
    Return a pandas Styler that colours the 'status' column:
    Green = Approved, Yellow = Pending, Red = Rejected.
    Works with st.dataframe(styled_df).
    """
    if df is None or df.empty:
        return df

    def color_status(val):
        if val is None:
            return ""
        s = str(val).strip().capitalize()
        if s == "Approved":
            return "background-color:#C8E6C9;color:#1B5E20;font-weight:600;"
        elif s == "Rejected":
            return "background-color:#FFCDD2;color:#B71C1C;font-weight:600;"
        elif s == "Pending":
            return "background-color:#FFF9C4;color:#827717;font-weight:600;"
        return ""

    styler = df.style
    if "status" in df.columns:
        styler = styler.applymap(color_status, subset=["status"])
    return styler


def make_admin_display_df(df):
    """
    Create a compact view for admin tables:
    - choose a sensible subset & order of columns
    - drop very wide JSON fields
    """
    if df is None or df.empty:
        return df

    base_cols = [
        "id",
        "name",
        "age",
        "gender",
        "house",
        "designation",
        "posting_details",
        "contact",
        "all_selected_events",
        "date_of_reg",
        "status",
        "fee_collected",
        "approved_by",
        "approved_at",
    ]
    cols = [c for c in base_cols if c in df.columns]
    compact = df[cols].copy()
    return compact



# ---------------------
# PDF helpers (kept from original)
# ---------------------
def create_pdf_receipt(registration):
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=letter)

    margin_left = 50
    margin_top = 750

    logo_path = "logo.jpg"
    termc_path = "terms.jpg"

    # draw logo if exists
    
    try:
        if os.path.exists(logo_path):
            c.drawImage(logo_path, (letter[0] - 120) / 2, 700, width=120, height=100, mask='auto')
    except Exception:
        pass

    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(letter[0] / 2, 680, "Participation Form")
    c.line(50, 675, 550, 675)

    table_data = [
        ["Field", "Details"],
        ["House", registration["House"]],
        ["Name", registration["Name"]],
        ["Gender", registration["Gender"]],
        ["Age (as on 30.11.2024)", str(registration["Age"])],
        ["Designation", registration["Designation"]],
        ["Posting Details", registration["Posting Details"]],
        ["Contact", registration["Contact"]],
        ["T-shirt Size", registration["T-shirt Size"]],
    ]

    table = Table(table_data, colWidths=[150, 350])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 12),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
    ]))

    table.wrapOn(c, margin_left, margin_top)
    table.drawOn(c, margin_left, margin_top - 245)

    event_y_position = margin_top - 270
    c.drawString(margin_left, event_y_position, "Registered for Events:")
    event_y_position -= 20
    c.setFont("Helvetica", 8)

    for category, events in registration["Selected Events"].items():
        if events:
            events_text = f"{category}: {', '.join(events)}"
            wrapped_text = wrap(events_text, width=150)
            for line in wrapped_text:
                c.drawString(margin_left, event_y_position, line)
                event_y_position -= 15

    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin_left, event_y_position - 10, f"Total Fee: Rs.{registration['Fee']}")
    c.drawString(margin_left, event_y_position - 20, f"Date of Reg.: {registration['Date of Reg.']}")

    try:
        if os.path.exists(termc_path):
            c.drawImage(termc_path, margin_left, 50, width=500, height=200, mask='auto')
    except Exception:
        pass

    c.save()
    packet.seek(0)
    pdf_file = BytesIO(packet.read())
    return pdf_file

# --- Helper: add medal column + HTML styling ---
def styled_leaderboard_html(board_df: pd.DataFrame) -> str:
    df = board_df.copy()

    medal_map = {
        1: "🥇 Gold",
        2: "🥈 Silver",
        3: "🥉 Bronze",
    }
    df["Medal"] = df["Rank"].map(medal_map).fillna("")

    # Reorder columns
    df = df[["Rank", "Medal", "House", "Points"]]

    # Build HTML table
    html_table = df.to_html(
        escape=False,
        index=False,
        classes="leaderboard-table"
    )

    # Full HTML document for the component
    full_html = f"""
    <html>
    <head>
      <style>
        table.leaderboard-table {{
          border-collapse: collapse;
          width: 100%;
          font-family: "Poppins", sans-serif;
        }}
        table.leaderboard-table th, table.leaderboard-table td {{
          border: 1px solid #e0e0e0;
          padding: 6px 10px;
          text-align: center;
        }}
        table.leaderboard-table th {{
          background-color: #004d40;
          color: #ffffff;
        }}
        table.leaderboard-table tr:nth-child(even) {{
          background-color: #f9f9f9;
        }}
        table.leaderboard-table tr:nth-child(1) {{
          background-color: #fff9c4;   /* light gold */
        }}
        table.leaderboard-table tr:nth-child(2) {{
          background-color: #e3f2fd;   /* light blue */
        }}
        table.leaderboard-table tr:nth-child(3) {{
          background-color: #fce4ec;   /* light pink */
        }}
      </style>
    </head>
    <body>
      {html_table}
    </body>
    </html>
    """
    return full_html


# --- Helper: PDF export for leaderboard + winners ---
def generate_leadership_board_pdf(board_df: pd.DataFrame, winners_df: pd.DataFrame):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph("Leadership Board", styles["Title"]))
    elements.append(Paragraph("(ITSRC, Vadodara - Sports Events 2025-26)", styles["Heading2"]))
    elements.append(Spacer(1, 12))

    # Top house line
    if not board_df.empty:
        top_row = board_df.sort_values("Rank").iloc[0]
        top_text = f"🏆 Top House: <b>{top_row['House']}</b> with <b>{int(top_row['Points'])}</b> points"
        elements.append(Paragraph(top_text, styles["Heading3"]))
        elements.append(Spacer(1, 12))

    # Scoring rules
    rule_text = (
        "Scoring Rules: "
        "Individual Events → 1st = 5, 2nd = 3, 3rd = 1. "
        "Team Events (Cricket, Volleyball, Tug of War) → 1st = 10, 2nd = 6"
    )
    elements.append(Paragraph(rule_text, styles["Normal"]))
    elements.append(Spacer(1, 12))

    # Leaderboard table (with medals)
    medal_map = {1: "Gold", 2: "Silver", 3: "Bronze"}
    pdf_df = board_df.copy()
    pdf_df["Medal"] = pdf_df["Rank"].map(medal_map).fillna("")
    pdf_df = pdf_df[["Rank", "Medal", "House", "Points"]]

    data = [pdf_df.columns.tolist()] + pdf_df.values.tolist()
    table = Table(data)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 18))

    # Winners list
    elements.append(Paragraph("Event-wise Winners", styles["Heading2"]))
    if isinstance(winners_df, pd.DataFrame) and not winners_df.empty:
        winners_records = winners_df.to_dict("records")
        for w in winners_records:
            line = (
                f"{w.get('event_name','')} ({w.get('category','')}) – "
                f"{w.get('position','')}: {w.get('winner_name','')} "
                f"({w.get('house','')})"
            )
            elements.append(Paragraph(line, styles["Normal"]))
            elements.append(Spacer(1, 4))
    else:
        elements.append(Paragraph("No winners recorded yet.", styles["Normal"]))

    doc.build(elements)
    buffer.seek(0)
    return buffer

# ---------------------
# ✅ QR Verification Handler
# -------------------------------------------------------
# QR Verification Handler — opens when scanning QR code
# -------------------------------------------------------
params = st.query_params

# In new Streamlit, this is usually a str, but we guard for list too
verify_id = params.get("verify_id", None)
if isinstance(verify_id, list):
    verify_id = verify_id[0]

if verify_id:
    st.title("✅ Registration Verification")

    try:
        # Do NOT cast to int; let Supabase handle it
        df_verify = get_participant_by_id(verify_id)
    except Exception as e:
        st.error(f"Error verifying participant: {e}")
        st.stop()

    if not df_verify.empty:
        reg = df_verify.iloc[0].to_dict()

        st.success("✅ Verified: Registration Record Found")

        st.markdown(f"""
        **Name:** {reg.get('name','')}  
        **House:** {reg.get('house','')}  
        **Designation:** {reg.get('designation','')}  
        **Events:** {reg.get('all_selected_events','')}  
        **Contact:** {reg.get('contact','')}  
        **Status:** {reg.get('status','Pending')}  
        **Date of Registration:** {reg.get('date_of_reg','')}
        """)

        st.info("This record is verified from the official registration database.")
    else:
        st.error("❌ Invalid or deleted Registration ID")

    # Stop further execution to prevent showing full app UI
    st.stop()



# ---------------------
# Auth: Login / Signup (using Supabase Auth via anon_client)
# ---------------------
def do_login():
    st.subheader("🔐 Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    # flag outside try/except so rerun isn't caught
    login_success = False

    if st.button("Login"):
        if not anon_client:
            st.error("Supabase anon client not configured.")
            return

        try:
            auth_resp = anon_client.auth.sign_in_with_password(
                {"email": email, "password": password}
            )
            user = auth_resp.user if hasattr(auth_resp, "user") else auth_resp

            # store session
            st.session_state["user"] = {"email": email}
            st.success("Login successful! Redirecting...")

            login_success = True   # mark success

        except Exception as e:
            st.error(f"Login failed: {e}")

    # 🔥 do the redirect *after* the try/except so rerun is not treated as error
    if login_success:
        st.session_state["active_page"] = "Admin Dashboard"
        st.query_params["page"] = "Admin Dashboard"
        st.rerun()


def do_logout():
    st.session_state["user"] = None
    st.success("Logged out.")
    # Optional: redirect back to login tab
    st.session_state["active_page"] = "Admin Login"
    st.query_params["page"] = "Admin Login"
    st.rerun()

if menu == "Admin Login":
    if st.session_state.get("user"):
        st.write(f"Logged in as: {st.session_state['user']['email']}")
        if st.button("Logout"):
            do_logout()
    else:
        do_login()


# ---------------------
# Participant Registration
# ---------------------
if menu == "Participant Registration":
    st.title("🏅 Sports Event Registration")
    st.subheader("Organized by Income Tax Sports & Recreation Club, Vadodara")
    st.write("Welcome! You can register for events")

    # ---- Global last date for normal registration ----
    LAST_REG_DATE = datetime(2025, 12, 10).date()   # <-- change date here if needed

    # Optional message
    st.markdown(
        f"<span style='color: red; font-weight: bold;'>"
        f"Last date for registration without late fee is {LAST_REG_DATE.strftime('%d-%m-%Y')} and with late fee is 20-12-2025."
        f"</span>",
        unsafe_allow_html=True
    )

    # font styling
    st.markdown("""
    <style>
    h3 {
        font-family: 'Poppins', sans-serif;
        color: #008080;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap" rel="stylesheet">
    <style>
    h3 {
        font-family: 'Poppins', sans-serif;
        color: #00796b;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

    st.subheader("Basic Details")

    # ---- AGE outside the form so event-listing updates immediately ----
    age = st.number_input("Age as on 30.11.2025", min_value=18, max_value=100, step=1, value=18)

    # Now the rest of inputs inside the form (except age)
    with st.form("registration_form"):
        house = st.selectbox("Select House", houses)
        name = st.text_input("Name")
        designation = st.selectbox("Post Held", [
            "CCIT", "PCIT", "CIT", "Addl.CIT", "Jt.CIT", "DCIT", "ACIT", "ITO",
            "Sr.PS", "PS", "AO-Gr III", "AO-Gr. II", "AO Gr. I", "ITI", "OS",
            "Steno-II", "TA", "Steno-I", "NS", "MTS", "Other"
        ])
        posting_details = st.text_input("Posting Details (e.g., unit or office)")
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        contact = st.text_input("Contact Number (10 digits)")
        tshirt_size = st.selectbox("T-shirt Size", tshirt_sizes)

        st.subheader("Select the Events you want to participate in.")

        # informational note for users <45
        if age < 45:
            st.info("Note: Veteran categories (45 years and above) are hidden because your age is under 45.")

        selected_events = {}
        total_fee = 250  # base fee
        selected_categories = set()

        # show categories — skip categories whose name contains 'veteran' when age < 45
        for category, events in event_details.items():
            is_veteran_category = "veteran" in category.lower()
            if age < 45 and is_veteran_category:
                continue

            selected_events[category] = st.multiselect(f"{category}", options=events)

        # ---- Fee calculations ----
       
        # Late fee logic
        today = datetime.now().date()
        is_late = today > LAST_REG_DATE
        late_fee = 150 if is_late else 0
        final_fee = total_fee + late_fee

        st.write(f"**Event Fee (capped): Rs.{total_fee}**")
        if is_late:
            st.warning(
                f"Late registration: additional Rs.150 will be charged "
                f"(Last date was {LAST_REG_DATE.strftime('%d-%m-%Y')})."
            )
        st.write(f"**Total Payable Fee: Rs.{final_fee}**")

        submitted = st.form_submit_button("Register")

    # -----------------------------
    # Validation and saving
    # -----------------------------
    if submitted:
        if not name.strip():
            st.error("Name cannot be empty!")
        elif not posting_details.strip():
            st.error("Posting details cannot be empty!")
        elif not contact.isdigit() or len(contact) != 10:
            st.error("Invalid contact number! Please enter a 10-digit number.")
        else:
            # flatten selected events (only categories shown were included)
            flattened_events = [event for sub_events in selected_events.values() for event in sub_events]

            registration = {
                "Name": name,
                "Age": age,
                "Gender": gender,
                "House": house,
                "Designation": designation,
                "Posting Details": posting_details,
                "Contact": contact,
                "T-shirt Size": tshirt_size,
                "Selected Events": selected_events,
                "All Selected Events": ", ".join(flattened_events),
                "Fee": final_fee,            # ✅ includes late fee
                "Date of Reg.": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Is Late": is_late,          # optional metadata
                "Late Fee": late_fee         # optional metadata
            }

            # Insert into Supabase
            resp = insert_participant(registration)

            if resp and resp.data:
                inserted_id = resp.data[0].get("id", "")
                # Keep on the same page after registration
                st.session_state.active_page = "Participant Registration"
                st.query_params["page"] = "Participant Registration"

                st.success("Registration successful!")
                st.balloons()

                participant_data = {
                    "id": inserted_id,
                    "name": name,
                    "post": designation,
                    "house": house,
                    "event": ", ".join(flattened_events),
                    "contact": contact,
                    "posting": posting_details,
                    "category": "Veterans" if age >= 45 else "Normal",
                    "gender": gender,
                    "age": age,
                    "fee": final_fee,          # ✅ final amount incl. late fee
                    "late_fee": late_fee,
                    "registration_date": datetime.now().strftime("%d-%m-%Y"),
                }

                base_url = st.secrets.get("APP_BASE_URL", "http://localhost:8501")
                participant_data["verification_url"] = f"{base_url}/?verify_id={inserted_id}"

                pdf_path = generate_participant_pdf(
                    participant_data,
                    logo_path = Path("its.gif"),
                    output_path=f"{name}_form.pdf"
                )

                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label="📄 Download Participant Form cum Receipt (PDF)",
                        data=f,
                        file_name=f"{name}_participation_form.pdf",
                        mime="application/pdf"
                    )

# ---------------------
# Already Registered (Search + Modify)
# ---------------------
if menu == "Already Registered (Re-print/Modify)":
    st.title("🔎 Check / Modify Your Registration Details")

    # --- Search Section ---
    search_contact = st.text_input("Enter your contact number:", key="search_contact")
    status = "Pending"  # default
    if "searched_record" not in st.session_state:
        st.session_state["searched_record"] = None

    if st.button("Search", key="search_button"):
        search_contact = search_contact.strip()
        df = get_participant_by_contact(search_contact)

        if not df.empty:
            st.success("✅ Participant found!")
            reg = df.iloc[0].to_dict()
            # --- Show current approval status to participant ---
            status = reg.get("status", "Pending")
            if status == "Pending":
                st.info("⏳ Status: Pending for approval from your House In-charge after fee collection.")
            elif status == "Approved":
                st.success("✅ Status: Approved. Your registration is confirmed.")
            elif status == "Rejected":
                st.error("❌ Status: Rejected. Please contact your House In-charge / Organising team.")
            else:
                st.info(f"Status: {status}")
            st.session_state["searched_record"] = reg
        else:
            st.warning("❌ No registration found for this contact number.")
            st.session_state["searched_record"] = None

    # ----------------------------------
    # Display + Modify if Record Found
    # ----------------------------------
    

    if st.session_state["searched_record"]:
        reg = st.session_state["searched_record"]

        # Parse stored event data safely
        if isinstance(reg.get("selected_events"), str):
            try:
                reg["Selected Events"] = json.loads(reg["selected_events"])
            except Exception:
                reg["Selected Events"] = {}
        elif isinstance(reg.get("selected_events"), dict):
            reg["Selected Events"] = reg["selected_events"]
        else:
            reg["Selected Events"] = {}

        st.markdown("### 🧾 Participant Details")

        # Summary display before modification
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Name:** {reg.get('name', '')}")
            st.write(f"**Age:** {reg.get('age', '')}")
            st.write(f"**House:** {reg.get('house', '')}")
            st.write(f"**Gender:** {reg.get('gender', '')}")
        with col2:
            st.write(f"**Designation:** {reg.get('designation', '')}")
            st.write(f"**Posting:** {reg.get('posting_details', '')}")
            st.write(f"**Contact:** {reg.get('contact', '')}")
            st.write(f"**Fee:** Rs.{reg.get('fee', '')}")

        # -------------------
        # Generate current PDF
        # -------------------
        base_url = st.secrets.get("APP_BASE_URL", "http://localhost:8501")
        participant_data = {
            "id": reg.get("id", ""),
            "name": reg.get("name", ""),
            "post": reg.get("designation", ""),
            "house": reg.get("house", ""),
            "event": reg.get("all_selected_events", ""),
            "contact": reg.get("contact", ""),
            "posting": reg.get("posting_details", ""),
            "category": "Veterans" if int(reg.get("age", 0)) >= 45 else "Normal",
            "gender": reg.get("gender", ""),
            "age": reg.get("age", 0),
            "fee": reg.get("fee", 0),
            "registration_date": reg.get("date_of_reg", ""),
            "verification_url": f"{base_url}/?verify_id={reg.get('id', '')}"
        }

        pdf_path = generate_participant_pdf(
            participant_data,
            logo_path=Path("its.gif"),
            output_path=f"{reg.get('name', '')}_form.pdf"
        )

        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
            st.download_button(
                label="📄 Download Existing Registration Form",
                data=pdf_bytes,
                file_name=f"{reg.get('name', '')}_form.pdf",
                mime="application/pdf",
                key="download_existing_form"
            )

        st.markdown("---")
        st.subheader("✏️ Modify Registration Details (Optional)")
        save_changes = False
        # ------------------
        # Edit Form
        # ------------------
        if status == "Pending":
            
            # show modify form
            with st.form("edit_registration_form", clear_on_submit=False):
                name = st.text_input("Name", reg.get("name", ""))
                house = st.selectbox(
                    "Select House",
                    houses,
                    index=houses.index(reg.get("house", houses[0])) if reg.get("house") in houses else 0,
                )
                designation = st.text_input("Designation", reg.get("designation", ""))
                posting_details = st.text_input("Posting Details", reg.get("posting_details", ""))
                age = st.number_input("Age", min_value=18, max_value=100, value=int(reg.get("age", 18)))
                gender = st.selectbox(
                    "Gender",
                    ["Male", "Female", "Other"],
                    index=["Male", "Female", "Other"].index(reg.get("gender", "Male")),
                )
                contact = st.text_input("Contact Number (10 digits)", reg.get("contact", ""))
                tshirt_size = st.selectbox(
                    "T-shirt Size",
                    tshirt_sizes,
                    index=tshirt_sizes.index(reg.get("tshirt_size", tshirt_sizes[0])) if reg.get("tshirt_size") in tshirt_sizes else 0,
                )

                st.markdown("---")
                st.subheader("Select Events")

                if age < 45:
                    st.info("Note: Veteran categories (45 years and above) are hidden because your age is under 45.")

                selected_events = {}
                total_fee = 250  # base fee
                selected_categories = set()

                for category, events in event_details.items():
                    is_veteran_category = "veteran" in category.lower()
                    if age < 45 and is_veteran_category:
                        continue

                    prev_sel = reg["Selected Events"].get(category, [])
                    selected_events[category] = st.multiselect(
                        f"{category}",
                        options=events,
                        default=prev_sel,
                        key=f"edit_event_{category.replace(' ', '_')}"
                    )

                    if selected_events[category] and category not in selected_categories:
                        selected_categories.add(category)

                
                st.write(f"**Total Fee:** Rs.{total_fee}")

                save_changes = st.form_submit_button("💾 Save Changes")

        else:
            st.info("Your registration has already been approved. For any changes, please contact your House In-charge.")
        
        # ------------------
        # Handle Update
        # ------------------
        if save_changes:
            st.toast("Saving changes...", icon="💾")

            flattened_events = [e for sub in selected_events.values() for e in sub]
            updated_data = {
                "name": name,
                "house": house,
                "designation": designation,
                "posting_details": posting_details,
                "age": age,
                "gender": gender,
                "contact": contact,
                "tshirt_size": tshirt_size,
                "selected_events": selected_events,
                "all_selected_events": ", ".join(flattened_events),
                "fee": total_fee,
                "date_of_reg": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            try:
                if not reg.get("id"):
                    st.error("⚠️ Missing participant ID — cannot update record.")
                else:
                    response = svc_client.table("participants").update(updated_data).eq("id", reg["id"]).execute()

                    if hasattr(response, "data") and response.data:
                        st.success("✅ Record updated successfully!")

                        # regenerate new PDF
                        participant_data["name"] = name
                        participant_data["post"] = designation
                        participant_data["house"] = house
                        participant_data["event"] = ", ".join(flattened_events)
                        participant_data["contact"] = contact
                        participant_data["posting"] = posting_details
                        participant_data["category"] = "Veterans" if age >= 45 else "Normal"
                        participant_data["gender"] = gender
                        participant_data["age"] = age
                        participant_data["fee"] = total_fee
                        participant_data["registration_date"] = datetime.now().strftime("%d-%m-%Y")

                        new_pdf = generate_participant_pdf(
                            participant_data,
                            logo_path=Path("its.gif"),
                            output_path=f"{name}_updated_form.pdf"
                        )

                        with open(new_pdf, "rb") as f:
                            st.download_button(
                                label="📄 Download Updated Participant Form",
                                data=f.read(),
                                file_name=f"{name}_updated_form.pdf",
                                mime="application/pdf",
                                key="download_updated_form"
                            )

                        # auto-refresh after short delay
                        st.toast("Refreshing...", icon="🔄")
                        time.sleep(3)
                        st.session_state["searched_record"] = None
                        st.rerun()
                    else:
                        st.error(f"❌ Update failed: {getattr(response, 'error', response)}")
            except Exception as e:
                st.error(f"⚠️ Exception while updating: {e}")
                
# Admin Dashboard (protected) -- requires login
# ---------------------
if menu == "Admin Dashboard":
    st.title("🔒 Admin Dashboard")
    if not st.session_state.get("user"):
        st.warning("You must be logged in to access Admin Dashboard. Go to Login and sign in.")
    else:
        user_email = st.session_state["user"]["email"]
        role_info = get_admin_role_for_email(user_email)
        if not role_info:
            st.error("Your account is not registered as an admin. Contact the system administrator.")
        else:
            role = role_info.get("role", "House Admin")
            admin_house = role_info.get("house")  # None for Super Admin
            st.success(f"Welcome, {role} ({user_email})!")

            # 🔹 colourful legend bar for admin dashboard
            st.markdown("""
            <div style="
                padding:0.6rem 1rem;
                border-radius:0.6rem;
                margin:0.5rem 0 1rem 0;
                background:linear-gradient(90deg,#E3F2FD,#E8F5E9,#FFFDE7,#FFEBEE);
                border:1px solid #ddd;
                font-size:0.85rem;">
                <b>Legend:</b>
                <span style="color:#1565C0;margin-left:8px;">Blue = Total</span> •
                <span style="color:#2E7D32;margin-left:8px;">Green = Approved</span> •
                <span style="color:#F9A825;margin-left:8px;">Yellow = Pending</span> •
                <span style="color:#B71C1C;margin-left:8px;">Red = Rejected</span>
            </div>
            """, unsafe_allow_html=True)
            # Tabs vary by Super Admin or house admin
            
            if role == "Super Admin":
                tabs = ["Combined Data", "Winners Entry", *houses, "Event-wise List", "Doubles Pairs"]
            else:
                tabs = ["House Data", "Event-wise List", "Doubles Pairs"]

            tab_objs = st.tabs(tabs)
            # Load all participants once
            all_participants_df = load_all_participants_df()

            # Combined Data tab
            if role == "Super Admin":
                if role == "Super Admin":
                    # ----- Tab 0: Combined Data -----
                    with tab_objs[0]:
                        st.subheader("📋 Combined Participants Data")

                        if all_participants_df.empty:
                            st.warning("No data available.")
                        else:
                            # 🔍 filters (like your Event-wise tab UX)
                            fcols = st.columns([2, 2, 3])
                            with fcols[0]:
                                search_contact = st.text_input(
                                    "Search by Contact Number",
                                    key="admin_combined_search_contact"
                                )
                            with fcols[1]:
                                status_filter = st.selectbox(
                                    "Filter by Status",
                                    ["All", "Approved", "Pending", "Rejected"],
                                    key="admin_combined_status_filter"
                                )

                            df_filtered = all_participants_df.copy()

                            if search_contact:
                                sc = search_contact.strip()
                                df_filtered = df_filtered[
                                    df_filtered["contact"].astype(str).str.strip() == sc
                                ]

                            if status_filter != "All":
                                df_filtered = df_filtered[
                                    df_filtered["status"].fillna("Pending") == status_filter
                                ]

                            # 🎯 summary for current selection
                            st.subheader("Summary")
                            render_status_summary(df_filtered, scope_label="Current Selection")

                            # 📊 compact, coloured table – same look as Event-wise tab
                            df_display = make_admin_display_df(df_filtered)
                            styled = style_status_df(df_display)
                            st.dataframe(styled, use_container_width=True)

                            st.download_button(
                                "Download Combined Data (full, unfiltered)",
                                data=all_participants_df.to_csv(index=False).encode("utf-8"),
                                file_name="Combined_Participants.csv",
                                mime="text/csv"
                            )

                # Winners entry tab
                with tab_objs[1]:
                    st.subheader("🎯 Enter Event Winners (Admin Only)")
                    events_list = [e for events in event_details.values() for e in events]
                    event = st.selectbox("Select Event", events_list)
                    category = st.selectbox("Select Category", ["M", "F", "M/F"])
                    with st.form("winner_entry_form"):
                        first_place = st.text_input("🥇 1st Place (Enter Name/Team Name)")
                        first_place_house = st.selectbox("House for 1st Place", houses)
                        second_place = st.text_input("🥈 2nd Place (Enter Name/Team Name)")
                        second_place_house = st.selectbox("House for 2nd Place", houses)
                        third_place = st.text_input("🥉 3rd Place (Optional - Enter Name/Team Name)")
                        third_place_house = st.selectbox("House for 3rd Place (Optional)", ["None"] + houses)
                        submitted = st.form_submit_button("Save Winners")
                    if submitted:
                        positions = {
                            "1st": (first_place, first_place_house),
                            "2nd": (second_place, second_place_house),
                        }
                        if third_place:
                            positions["3rd"] = (third_place, third_place_house if third_place_house != "None" else None)
                        ok = upsert_winner(event, category, positions)
                        if ok:
                            st.success("Winners saved successfully!")

                # Individual house tabs
                for i, house in enumerate(houses, start=2):
                    with tab_objs[i]:
                        df = all_participants_df[all_participants_df["house"] == house] if not all_participants_df.empty else pd.DataFrame()
                        # 🎯 summary for current selection
                        st.subheader("Summary")
                        render_status_summary(df, scope_label="Current Selection")
                        st.subheader(f"📋 {house} Participants Data")
                        
                        if not df.empty:
                            df_disp = add_status_chip_column(df)
                            # 📊 compact, coloured table – same look as Event-wise tab
                            df_display = make_admin_display_df(df)
                            styled = style_status_df(df_display)
                            st.dataframe(styled, use_container_width=True)
                            

                            st.download_button(
                                f"Download {house} Data",
                                data=df.to_csv(index=False).encode("utf-8"),
                                file_name=f"{house.replace(' ', '_')}_Participants.csv",
                                mime="text/csv"
                            )
                        else:
                            st.warning(f"No data available for {house}.")


            else:
                # 🏠 House admin
                house_name = admin_house
                # fallback if for some reason admin_house is None
                if not house_name:
                    house_name = role.replace(" Admin", "") if role.endswith(" Admin") else role

                with tab_objs[0]:
                    st.subheader(f"📋 {house_name} Participants Data")

                    df_house = all_participants_df[all_participants_df["house"] == house_name] if not all_participants_df.empty else pd.DataFrame()

                    if df_house.empty:
                        st.warning(f"No data available for {house_name}.")
                    else:
                        # ---------- Filters (contact + status) ----------
                        fcols = st.columns([2, 2, 3])
                        with fcols[0]:
                            search_contact = st.text_input(
                                "Search by Contact Number",
                                key="admin_house_search_contact"
                            )
                        with fcols[1]:
                            status_filter = st.selectbox(
                                "Filter by Status",
                                ["All", "Approved", "Pending", "Rejected"],
                                key="admin_house_status_filter"
                            )

                        df_house_filtered = df_house.copy()

                        # filter by exact contact match (string)
                        if search_contact:
                            sc = search_contact.strip()
                            df_house_filtered = df_house_filtered[
                                df_house_filtered["contact"].astype(str).str.strip() == sc
                            ]

                        # filter by status
                        if status_filter != "All":
                            df_house_filtered = df_house_filtered[
                                df_house_filtered["status"].fillna("Pending") == status_filter
                            ]

                        # ---------- Summary for current view ----------
                        st.subheader("Summary")
                        render_status_summary(df_house_filtered, scope_label=house_name)

                        # ---------- Compact, coloured table ----------
                        df_display = make_admin_display_df(df_house_filtered)
                        styled = style_status_df(df_display)
                        st.dataframe(styled, use_container_width=True)

                        # download full house data (unfiltered)
                        st.download_button(
                            f"Download {house_name} Data (full, unfiltered)",
                            data=df_house.to_csv(index=False).encode("utf-8"),
                            file_name=f"{house_name.replace(' ', '_')}_Participants.csv",
                            mime="text/csv"
                        )

                        st.markdown("---")
                        st.subheader("✅ Pending Approvals")

                        # pending approvals always from full house data
                        pending = df_house[df_house["status"].fillna("Pending") == "Pending"]

                        if pending.empty:
                            st.info("No pending registrations for approval.")
                        else:
                            for _, row in pending.iterrows():
                                cols = st.columns([4, 1, 1])
                                with cols[0]:
                                    st.markdown(
                                        f"**{row['name']}**  \n"
                                        f"House: {row['house']}  \n"
                                        f"Designation: {row.get('designation','')}  \n"
                                        f"Events: {row.get('all_selected_events','')}"
                                    )
                                with cols[1]:
                                    if st.button("Approve ✅", key=f"approve_{row['id']}"):
                                        update_participant_status(
                                            participant_id=row["id"],
                                            status="Approved",
                                            approved_by=user_email,
                                            fee_collected=True
                                        )
                                        st.success(f"Approved {row['name']}")
                                        st.rerun()
                                with cols[2]:
                                    if st.button("Reject ❌", key=f"reject_{row['id']}"):
                                        update_participant_status(
                                            participant_id=row["id"],
                                            status="Rejected",
                                            approved_by=user_email,
                                            fee_collected=False
                                        )
                                        st.warning(f"Rejected {row['name']}")
                                        st.rerun()

            # Event-wise participants tab (last tab)
            with tab_objs[tabs.index("Event-wise List")]:
                st.subheader("📜 Event-wise Participant List")
                event_data = all_participants_df if role == "Super Admin" else (all_participants_df[all_participants_df["house"] == house_name] if not all_participants_df.empty else pd.DataFrame())

                if event_data.empty:
                    st.warning("No registration data available.")
                else:
                    event_data["All Selected Events"] = event_data["All Selected Events"].fillna("")
                    exploded = event_data.assign(Event=event_data["All Selected Events"].str.split(", ")).explode("Event")
                    event_list = exploded["Event"].dropna().unique().tolist()
                    selected_event = st.selectbox("Select Event", options=event_list)
                    if selected_event:
                        filtered = exploded[exploded["Event"] == selected_event]
                        filtered_filtered = filtered.drop(columns=["tshirt_size", "Selected Events", "all_selected_events", "fee"], errors="ignore")
                        st.write(f"### Participants for {selected_event}")
                        st.dataframe(filtered_filtered)
                        st.download_button(label=f"Download {selected_event} Participants", data=filtered_filtered.to_csv(index=False).encode("utf-8"), file_name=f"{selected_event.replace(' ', '_')}_Participants.csv", mime="text/csv")


            # =======================
            # Doubles Pairs Admin Tab
            # =======================
            with tab_objs[tabs.index("Doubles Pairs")]:
                st.subheader("🎾 Doubles Pairs Management")

                # Load all pairs
                pairs_df = load_all_pairs()

                if pairs_df.empty:
                    st.info("No doubles pairs registered yet.")
                else:
                    # If house admin, restrict to their house
                    if role != "Super Admin":
                        house_name = admin_house or role.replace(" Admin", "") if role.endswith(" Admin") else role
                        pairs_df = pairs_df[pairs_df["house"] == house_name]

                    if pairs_df.empty:
                        st.info("No doubles pairs for your house yet.")
                    else:
                        # Filters
                        fcols = st.columns([2, 2, 3])
                        with fcols[0]:
                            event_filter = st.selectbox(
                                "Filter by Event",
                                ["All Events"] + sorted(pairs_df["event_name"].dropna().unique().tolist()),
                                key="pairs_event_filter"
                            )
                        with fcols[1]:
                            house_filter = st.selectbox(
                                "Filter by House",
                                ["All Houses"] + sorted(pairs_df["house"].dropna().unique().tolist()),
                                key="pairs_house_filter"
                            ) if role == "Super Admin" else (None)

                        df_view = pairs_df.copy()

                        if event_filter != "All Events":
                            df_view = df_view[df_view["event_name"] == event_filter]

                        if role == "Super Admin" and house_filter and house_filter != "All Houses":
                            df_view = df_view[df_view["house"] == house_filter]

                        if df_view.empty:
                            st.info("No pairs match current filters.")
                        else:
                            show_cols = [
                                c for c in [
                                    "id", "event_name", "house",
                                    "player1_name", "player1_contact",
                                    "player2_name", "player2_contact",
                                    "created_at"
                                ] if c in df_view.columns
                            ]

                            st.markdown("#### Registered Pairs")
                            st.dataframe(df_view[show_cols], use_container_width=True)

                            st.markdown("---")
                            st.markdown("#### Manage Pairs")

                            # per-row actions
                            for _, row in df_view.iterrows():
                                st.markdown(
                                    f"**{row['event_name']}** — {row['player1_name']} & {row['player2_name']} "
                                    f"({row['house']})"
                                )
                                c1, c2, c3 = st.columns([2, 2, 1])
                                with c1:
                                    # Print Pair Slip
                                    if st.button("🧾 Print Pair Slip", key=f"print_pair_{row['id']}"):
                                        pair_data = {
                                            "event_name": row["event_name"],
                                            "house": row["house"],
                                            "player1_name": row["player1_name"],
                                            "player1_contact": row["player1_contact"],
                                            "player2_name": row["player2_name"],
                                            "player2_contact": row["player2_contact"],
                                        }
                                        pdf_path = generate_pair_slip_pdf(
                                            pair_data,
                                            logo_path="logo.jpg",
                                            output_path=f"pair_slip_{row['id']}.pdf"
                                        )
                                        with open(pdf_path, "rb") as f:
                                            st.download_button(
                                                label="⬇️ Download Pair Slip PDF",
                                                data=f,
                                                file_name=f"pair_slip_{row['id']}.pdf",
                                                mime="application/pdf",
                                                key=f"download_pair_slip_{row['id']}"
                                            )
                                with c2:
                                    # Delete pair (Super Admin or House Admin)
                                    if st.button("🗑️ Delete Pair", key=f"delete_pair_{row['id']}"):
                                        ok = delete_partner_pair(row["id"])
                                        if ok:
                                            st.success("Pair deleted.")
                                            st.rerun()
                                with c3:
                                    st.write("")  # spacer
                                st.markdown("---")

# ---------------------
# Insight
# ---------------------
if menu == "Insight":
    st.title("📊 Insights")

    df = load_all_participants_df()
    if df.empty:
        st.warning("No registration data available.")
    else:
        # Work on a copy so we don't mutate original
        df = df.copy()

        # Normalise some columns
        df["All Selected Events"] = df.get("All Selected Events", df.get("all_selected_events", "")).fillna("")
        if "status" in df.columns:
            df["status"] = df["status"].fillna("Pending")
        else:
            df["status"] = "Pending"

        # Age groups (if age column present)
        if "age" in df.columns:
            bins = [18, 45, 61, 200]
            labels = ["18–44", "45–60", "60+"]
            df["Age Group"] = pd.cut(df["age"], bins=bins, labels=labels, right=False)

        # Call your existing summary helper
        #render_status_summary(df, scope_label="All Houses")

        # ---------------------
        # Top KPI row
        # ---------------------
        total_participants = len(df)
        approved_cnt = (df["status"] == "Approved").sum()
        pending_cnt = (df["status"] == "Pending").sum()
        rejected_cnt = (df["status"] == "Rejected").sum()

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("👥 Total Participants", total_participants)
        k2.metric("✅ Approved", approved_cnt)
        k3.metric("⏳ Pending", pending_cnt)
        k4.metric("❌ Rejected", rejected_cnt)

        st.markdown("---")

        # ---------------------
        # Filters
        # ---------------------
        with st.expander("🔍 Filters", expanded=False):
            house_opts = sorted(df["house"].dropna().unique().tolist()) if "house" in df.columns else []
            status_opts = ["Approved", "Pending", "Rejected"]
            event_list = (
                df["All Selected Events"].str.split(", ").explode().dropna().unique().tolist()
                if "All Selected Events" in df.columns else []
            )

            c1, c2, c3 = st.columns(3)
            with c1:
                selected_houses = st.multiselect(
                    "House",
                    options=house_opts,
                    default=house_opts,
                )
            with c2:
                selected_status = st.multiselect(
                    "Status",
                    options=status_opts,
                    default=status_opts,
                )
            with c3:
                selected_event = st.selectbox(
                    "Filter by specific Event (optional)",
                    options=["(All Events)"] + event_list,
                    index=0,
                )

        # Apply filters
        filtered_df = df.copy()
        if selected_houses:
            filtered_df = filtered_df[filtered_df["house"].isin(selected_houses)]
        if selected_status:
            filtered_df = filtered_df[filtered_df["status"].isin(selected_status)]
        if selected_event and selected_event != "(All Events)":
            filtered_df = filtered_df[
                filtered_df["All Selected Events"].str.contains(selected_event, case=False, na=False)
            ]

        if filtered_df.empty:
            st.warning("No data after applying filters.")
        else:
            # ---------------------
            # Tabs for different insight views
            # ---------------------
            tab_overview, tab_events, tab_demo, tab_fee = st.tabs(
                ["🏠 Overview", "🏅 Events & Houses", "🧬 Demographics", "💰 Fee & Status"]
            )

            # ====== OVERVIEW TAB ======
            with tab_overview:
                st.subheader("House-wise Distribution (Filtered)")

                house_counts = (
                    filtered_df["house"].value_counts().reset_index()
                    if "house" in filtered_df.columns
                    else pd.DataFrame(columns=["index", "house"])
                )
                if not house_counts.empty:
                    house_counts.columns = ["House", "Count"]
                    fig_house = px.bar(
                        house_counts,
                        x="House",
                        y="Count",
                        color="House",
                        title="Participants by House",
                    )
                    st.plotly_chart(fig_house, use_container_width=True)
                else:
                    st.info("House information not available.")

                st.subheader("Status by House")
                if "house" in filtered_df.columns and "status" in filtered_df.columns:
                    status_house = (
                        filtered_df.groupby(["house", "status"])["id"].count().reset_index()
                        if "id" in filtered_df.columns
                        else filtered_df.groupby(["house", "status"]).size().reset_index(name="count")
                    )
                    status_house.columns = ["House", "Status", "Count"]
                    fig_status_house = px.bar(
                        status_house,
                        x="House",
                        y="Count",
                        color="Status",
                        barmode="stack",
                        title="Approved / Pending / Rejected by House",
                    )
                    st.plotly_chart(fig_status_house, use_container_width=True)

                # Daily registrations
                if "date_of_reg" in filtered_df.columns:
                    try:
                        date_series = pd.to_datetime(filtered_df["date_of_reg"]).dt.date
                        daily = date_series.value_counts().sort_index().reset_index()
                        daily.columns = ["Date", "Registrations"]
                        st.subheader("📅 Registrations Over Time")
                        fig_daily = px.line(
                            daily,
                            x="Date",
                            y="Registrations",
                            markers=True,
                            title="Daily Registrations",
                        )
                        st.plotly_chart(fig_daily, use_container_width=True)
                    except Exception:
                        pass

            # ====== EVENTS & HOUSES TAB ======
            with tab_events:
                st.subheader("Event-wise Distribution (Filtered)")

                all_events = filtered_df["All Selected Events"].str.split(", ").explode()
                event_counts = all_events.value_counts().reset_index()
                event_counts.columns = ["Event", "Count"]
                if not event_counts.empty:
                    fig_event = px.bar(
                        event_counts,
                        x="Event",
                        y="Count",
                        title="Participants by Event",
                    )
                    st.plotly_chart(fig_event, use_container_width=True)
                else:
                    st.info("No event data available for current filters.")

                # House vs Event heatmap
                st.subheader("House vs Event Heatmap")
                if "house" in filtered_df.columns and not all_events.empty:
                    tmp = filtered_df.copy()
                    tmp = tmp.assign(Event=tmp["All Selected Events"].str.split(", ")).explode("Event")
                    tmp = tmp[tmp["Event"].notna() & (tmp["Event"] != "")]
                    if not tmp.empty:
                        pivot = pd.pivot_table(
                            tmp,
                            index="house",
                            columns="Event",
                            values="id" if "id" in tmp.columns else "name",
                            aggfunc="count",
                            fill_value=0,
                        )
                        fig_heat = px.imshow(
                            pivot,
                            labels=dict(x="Event", y="House", color="Participants"),
                            aspect="auto",
                            title="Participation Heatmap (House x Event)",
                        )
                        st.plotly_chart(fig_heat, use_container_width=True)
                    else:
                        st.info("No events found after filtering.")
                else:
                    st.info("House or event information not available.")

            # ====== DEMOGRAPHICS TAB ======
            with tab_demo:
                st.subheader("Age-wise Distribution")
                if "Age Group" in filtered_df.columns:
                    age_group_counts = filtered_df["Age Group"].value_counts().reset_index()
                    age_group_counts.columns = ["Age Group", "Count"]
                    fig_age = px.bar(
                        age_group_counts,
                        x="Age Group",
                        y="Count",
                        title="Participants by Age Group",
                    )
                    st.plotly_chart(fig_age, use_container_width=True)
                else:
                    st.info("Age data not available.")

                st.subheader("Gender-wise Distribution")
                if "gender" in filtered_df.columns:
                    gender_counts = filtered_df["gender"].value_counts().reset_index()
                    gender_counts.columns = ["Gender", "Count"]
                    fig_gender = px.pie(
                        gender_counts,
                        names="Gender",
                        values="Count",
                        title="Participants by Gender",
                    )
                    st.plotly_chart(fig_gender, use_container_width=True)

                # Designation-wise
                if "designation" in filtered_df.columns:
                    st.subheader("Top Designations by Participation")
                    desig_counts = (
                        filtered_df["designation"].value_counts().head(10).reset_index()
                    )
                    desig_counts.columns = ["Designation", "Count"]
                    fig_desig = px.bar(
                        desig_counts,
                        x="Designation",
                        y="Count",
                        title="Top 10 Designations",
                    )
                    st.plotly_chart(fig_desig, use_container_width=True)

                # T-shirt size distribution
                if "tshirt_size" in filtered_df.columns:
                    st.subheader("T-shirt Size Distribution")
                    tshirt_counts = filtered_df["tshirt_size"].value_counts().reset_index()
                    tshirt_counts.columns = ["T-shirt Size", "Count"]
                    fig_tshirt = px.bar(
                        tshirt_counts,
                        x="T-shirt Size",
                        y="Count",
                        title="T-shirt Sizes Requested",
                    )
                    st.plotly_chart(fig_tshirt, use_container_width=True)

            # ====== FEE & STATUS TAB ======
            with tab_fee:
                st.subheader("Fee Summary")

                if "fee" in filtered_df.columns:
                    total_fee = filtered_df["fee"].sum()
                    avg_fee = filtered_df["fee"].mean()
                    c1, c2 = st.columns(2)
                    c1.metric("Total Fee (by selection)", f"₹{int(total_fee)}")
                    c2.metric("Average Fee per Participant", f"₹{avg_fee:0.0f}")

                    # Fee by house
                    if "house" in filtered_df.columns:
                        fee_by_house = (
                            filtered_df.groupby("house")["fee"].sum().reset_index()
                        )
                        fee_by_house.columns = ["House", "Total Fee"]
                        fig_fee_house = px.bar(
                            fee_by_house,
                            x="House",
                            y="Total Fee",
                            title="Total Fee Collected by House (based on registrations)",
                        )
                        st.plotly_chart(fig_fee_house, use_container_width=True)

                # Fee collected flag vs status
                if "fee_collected" in filtered_df.columns:
                    st.subheader("Fee Collected vs Status")
                    status_fee = (
                        filtered_df.groupby(["status", "fee_collected"])
                        .size()
                        .reset_index(name="Count")
                    )
                    status_fee["fee_collected_label"] = status_fee["fee_collected"].map(
                        {True: "Fee Collected", False: "Not Collected"}
                    )
                    fig_status_fee = px.bar(
                        status_fee,
                        x="status",
                        y="Count",
                        color="fee_collected_label",
                        barmode="group",
                        title="Status vs Fee Collected",
                        labels={"status": "Status", "Count": "Participants"},
                    )
                    st.plotly_chart(fig_status_fee, use_container_width=True)

# ---------------------
# Events Schedule (static content kept)
# ---------------------
# ---------------------
# ---------------------
# Events Schedule
# ---------------------
if menu == "Events Schedule":
    st.title("📅 Events Schedule")
    st.subheader("Schedule for ITSRC Sports Events 2025-26")
    st.info("Scroll the schedule below or download it for printing.")

    pdf_path = Path("Schedule 2025.pdf")   # 👈 make sure this filename/path is correct

    if pdf_path.exists():
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

        base64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")

        # 🔹 Embedded scrollable PDF
        html(
            f"""
            <iframe
                src="data:application/pdf;base64,{base64_pdf}"
                style="width:100%; height:800px; border:none;"
            ></iframe>
            """,
            height=820,
        )

        # 🔹 Download button
        st.download_button(
            label="📥 Download Full Schedule (PDF)",
            data=pdf_bytes,
            file_name="Schedule 2025.pdf",
            mime="application/pdf",
        )
    else:
        st.error("Schedule PDF not found on the server. Please contact the organizer.")


# ---------------------
# ---------------------
# Leadership Board
# ---------------------
if menu == "Leadership Board":
    st.title("🏆 Leadership Board")

    # Live refresh button (auto-update from Supabase)
    if st.button("🔄 Refresh Leaderboard"):
        st.rerun()

    # Compute leaderboard
    board_df = compute_leaderboard_from_winners()

    # Load winners once for both display + PDF
    winners_df = load_winners_df()
    if isinstance(winners_df, list):
        winners_df = pd.DataFrame(winners_df)

    # 🏆 Trophy section
    if not board_df.empty:
        top_row = board_df.sort_values("Rank").iloc[0]
        st.markdown(
            f"""
            <div style="padding:10px 15px;border-radius:10px;
                        background:#fff3cd;border-left:5px solid #ffb300;
                        margin-bottom:15px;">
                <span style="font-size:26px;">🏆</span>
                <span style="font-size:20px;font-weight:600;margin-left:8px;">
                    Current Top House: {top_row['House']} ({int(top_row['Points'])} pts)
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Optional celebration
        if st.button("🎉 Celebrate Top House"):
            st.balloons()

    # 🎖️ Medal-styled leaderboard table
    st.subheader("House Rankings")
    #st.markdown(styled_leaderboard_html(board_df), unsafe_allow_html=True)
    html(styled_leaderboard_html(board_df), height=260, scrolling=False)

    # 📄 Export as PDF
    st.markdown("---")
    st.subheader("Export")
    if st.button("📄 Generate Leadership Board PDF"):
        pdf_buf = generate_leadership_board_pdf(board_df, winners_df)
        st.download_button(
            "Download Leadership Board PDF",
            data=pdf_buf,
            file_name="Leadership_Board.pdf",
            mime="application/pdf",
        )


        # ---------------------
    # Event-wise Winners (grouped nicely)
    # ---------------------
    st.subheader("📜 Event-wise Winners")

    winners_raw = load_winners_df()
    if isinstance(winners_raw, list):
        winners_df = pd.DataFrame(winners_raw)
    else:
        winners_df = winners_raw

    if winners_df is None or winners_df.empty:
        st.warning("No winners data available yet.")
    else:
        # Make sure we have needed columns
        winners_df = winners_df.fillna("")
        # Group by Event + Category
        grouped = winners_df.groupby(["event_name", "category"], sort=True)

        for (event_name, cat), grp in grouped:
            # Event + category heading (once, in bold)
            heading = f"**{event_name} ({cat})**" if cat else f"**{event_name}**"
            st.markdown(heading)

            # Sort positions so 1st,2nd,3rd appear in order
            order_map = {"1st": 1, "2nd": 2, "3rd": 3}
            grp = grp.copy()
            grp["pos_order"] = grp["position"].map(order_map).fillna(99)
            grp = grp.sort_values("pos_order")

            # Lines for winners
            for _, row in grp.iterrows():
                st.markdown(
                    f"- {row['position']}: **{row['winner_name']}** "
                    f"(_{row['house']}_)"
                )

            st.markdown("---")

    

# ---------------------
# Doubles Partner Selection / Registration
# ---------------------
if menu == "Doubles Partner Selection":
    st.title("🎾 Doubles Partner Registration")

    # Only events that are Doubles / Mixed Doubles
    doubles_events = [
        event
        for events in event_details.values()
        for event in events
        if "doubles" in event.lower()
    ]

    selected_event = st.selectbox("Select Doubles Event", doubles_events)

    if selected_event:
        # Load all registered participants from Supabase
        all_df = load_all_participants_df()

        if all_df.empty:
            st.warning("No participants registered yet.")
        else:
            # ✅ Enforce APPROVED status only
            if "status" in all_df.columns:
                all_df["status_clean"] = all_df["status"].fillna("Pending")
                approved_df = all_df[all_df["status_clean"] == "Approved"].copy()
            else:
                # If for some reason status column missing, safest is to block pairing
                st.error("Status column missing. For safety, doubles pairing is disabled until status is configured.")
                approved_df = pd.DataFrame()

            if approved_df.empty:
                st.warning("No approved participants available for doubles pairing.")
            else:
                # Ensure "All Selected Events" exists and is string
                approved_df["All Selected Events"] = approved_df["All Selected Events"].fillna("")

                # participants who have chosen this doubles event
                event_mask = approved_df["All Selected Events"].str.contains(
                    selected_event, case=False, na=False
                )
                event_participants = approved_df[event_mask].copy()

                if event_participants.empty:
                    st.warning(
                        f"No APPROVED participants have registered for '{selected_event}' yet. "
                        "Participants must be approved before forming doubles pairs."
                    )
                else:
                    st.info(
                        f"{len(event_participants)} approved participant(s) are eligible for '{selected_event}'."
                    )

                    # show compact view
                    display_cols = [
                        c for c in [
                            "name", "house", "designation", "posting_details",
                            "contact", "gender", "age", "all_selected_events", "status_clean"
                        ] if c in event_participants.columns
                    ]
                    st.markdown("#### Eligible Approved Participants for this Event")
                    st.dataframe(event_participants[display_cols], use_container_width=True)

                    st.markdown("---")
                    st.markdown("### 🧑‍🤝‍🧑 Register a Doubles Pair")

                    col1, col2 = st.columns(2)
                    with col1:
                        contact_1 = st.text_input("Your Contact Number (Player 1)", key="dbl_contact1")
                    with col2:
                        contact_2 = st.text_input("Partner's Contact Number (Player 2)", key="dbl_contact2")

                    if st.button("Submit Pair", key="submit_doubles_pair"):
                        c1 = contact_1.strip()
                        c2 = contact_2.strip()

                        # basic validation
                        if not c1 or not c2:
                            st.error("Please enter both contact numbers.")
                        elif not c1.isdigit() or len(c1) != 10:
                            st.error("Player 1: Invalid contact number. Please enter a 10-digit number.")
                        elif not c2.isdigit() or len(c2) != 10:
                            st.error("Player 2: Invalid contact number. Please enter a 10-digit number.")
                        elif c1 == c2:
                            st.error("Both contact numbers are the same. Please enter two different participants.")
                        else:
                            # normalize contact
                            event_participants["contact_str"] = event_participants["contact"].astype(str).str.strip()

                            p1 = event_participants[event_participants["contact_str"] == c1]
                            p2 = event_participants[event_participants["contact_str"] == c2]

                            if p1.empty or p2.empty:
                                st.error(
                                    "One or both contact numbers are not APPROVED participants "
                                    f"for '{selected_event}'."
                                )
                            else:
                                house1 = p1.iloc[0]["house"]
                                house2 = p2.iloc[0]["house"]
                                if house1 != house2:
                                    st.error(
                                        f"Participants belong to different houses ({house1} vs {house2}). "
                                        "Both players must be from the same house."
                                    )
                                else:
                                    # load existing pairs for this event
                                    existing_pairs = load_pairs_for_event(selected_event)
                                    dup_pair = False
                                    already_paired = False

                                    if not existing_pairs.empty:
                                        existing_pairs["p1"] = existing_pairs["player1_contact"].astype(str).str.strip()
                                        existing_pairs["p2"] = existing_pairs["player2_contact"].astype(str).str.strip()

                                        # 1) prevent exact or reversed duplicates (A-B vs B-A)
                                        for _, r in existing_pairs.iterrows():
                                            if ((r["p1"] == c1 and r["p2"] == c2) or
                                                (r["p1"] == c2 and r["p2"] == c1)):
                                                dup_pair = True
                                                break

                                        # 2) also prevent either player being in another pair
                                        existing_contacts = set(existing_pairs["p1"]) | set(existing_pairs["p2"])
                                        if c1 in existing_contacts or c2 in existing_contacts:
                                            already_paired = True

                                    if dup_pair:
                                        st.error("This pair is already registered (including reversed order).")
                                    elif already_paired:
                                        st.error(
                                            "One of these participants is already registered as a doubles partner "
                                            "for this event."
                                        )
                                    else:
                                        pair = {
                                            "player1_name": p1.iloc[0]["name"],
                                            "player1_contact": c1,
                                            "player2_name": p2.iloc[0]["name"],
                                            "player2_contact": c2,
                                            "event_name": selected_event,
                                            "house": house1,
                                        }

                                        ok = save_partner_pair(pair)
                                        if ok:
                                            st.success(
                                                f"Pair registered successfully: "
                                                f"{pair['player1_name']} & {pair['player2_name']} ({house1})"
                                            )
                                            st.rerun()

                    # ---------- Existing pairs ----------
                    st.markdown("---")
                    st.markdown("### 📋 Existing Pairs for this Event")

                    pairs_df = load_pairs_for_event(selected_event)
                    if pairs_df.empty:
                        st.info("No pairs registered yet for this event.")
                    else:
                        show_cols = [
                            c for c in [
                                "house", "player1_name", "player1_contact",
                                "player2_name", "player2_contact"
                            ] if c in pairs_df.columns
                        ]
                        st.dataframe(pairs_df[show_cols], use_container_width=True)
    else:
        st.info("Please select a doubles event to proceed.")

# ---------------------
# Footer note
# ---------------------
st.markdown("---")
st.markdown("Built with ❤️ — ITSRC Vadodara IT Sports Committee 2025-26")
st.markdown('</div>', unsafe_allow_html=True)

# ---------------------



