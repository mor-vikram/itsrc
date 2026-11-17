# streamlit_app_neon.py
import time
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
import hashlib
import hmac
from contextlib import closing
import re as _re
from types import SimpleNamespace
import psycopg2
from psycopg2.extras import RealDictCursor, Json
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
    st.markdown('<div class="navbar-title" style="text-align:center;">(Sports Events @2026-27)</div>', unsafe_allow_html=True)
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





# =========================================================
# NEON POSTGRESQL CONNECTION + COMPATIBILITY QUERY ADAPTER
# =========================================================
# Configure DATABASE_URL in .streamlit/secrets.toml or environment.
# Example secrets.toml:
# DATABASE_URL = "postgresql://USER:PASSWORD@HOST/DB?sslmode=require"

load_dotenv()
DATABASE_URL = st.secrets.get("DATABASE_URL", None) or os.getenv("DATABASE_URL")

if not DATABASE_URL:
    st.warning(
        "Neon database connection is not configured. Add DATABASE_URL to "
        ".streamlit/secrets.toml or your environment variables."
    )


class NeonQueryResponse:
    """Small response object retaining the existing response.data interface."""
    def __init__(self, data=None):
        self.data = data or []
        self.error = None


class NeonTableQuery:
    """Minimal query builder supporting operations used by this Streamlit app."""
    ALLOWED_TABLES = {
        "participants", "admins", "winners", "match_draws", "doubles_partners"
    }

    def __init__(self, database_url, table_name):
        if table_name not in self.ALLOWED_TABLES:
            raise ValueError(f"Unsupported database table: {table_name}")
        self.database_url = database_url
        self.table_name = table_name
        self.operation = None
        self.payload = None
        self.columns = "*"
        self.filters = []
        self.order_by = None
        self.order_desc = False

    @staticmethod
    def _identifier(value):
        if not _re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", str(value)):
            raise ValueError(f"Invalid SQL identifier: {value}")
        return f'"{value}"'

    def select(self, columns="*"):
        self.operation = "select"
        if columns.strip() == "*":
            self.columns = "*"
        else:
            self.columns = ", ".join(
                self._identifier(c.strip()) for c in columns.split(",")
            )
        return self

    def insert(self, payload):
        self.operation = "insert"
        self.payload = payload
        return self

    def update(self, payload):
        self.operation = "update"
        self.payload = payload
        return self

    def delete(self):
        self.operation = "delete"
        return self

    def eq(self, column, value):
        self.filters.append((column, value))
        return self

    def order(self, column, desc=False):
        self.order_by = column
        self.order_desc = bool(desc)
        return self

    @staticmethod
    def _adapt_value(column, value):
        # Convert Python dict/list (and the legacy JSON string) into JSONB.
        if column == "selected_events":
            if isinstance(value, str):
                try:
                    value = json.loads(value)
                except (TypeError, ValueError):
                    value = {}
            return Json(value if value is not None else {})
        if isinstance(value, (dict, list)):
            return Json(value)
        return value

    def execute(self):
        if not self.database_url:
            raise RuntimeError("DATABASE_URL is missing; Neon connection is unavailable.")

        where_sql = ""
        params = []
        if self.filters:
            clauses = []
            for col, value in self.filters:
                clauses.append(f"{self._identifier(col)} = %s")
                params.append(value)
            where_sql = " WHERE " + " AND ".join(clauses)

        table_sql = self._identifier(self.table_name)
        query = None
        data = []

        try:
            with closing(psycopg2.connect(
                self.database_url,
                sslmode="require",
                connect_timeout=15,
            )) as conn:
                with conn:
                    with conn.cursor(cursor_factory=RealDictCursor) as cur:
                        if self.operation == "select":
                            query = f"SELECT {self.columns} FROM {table_sql}{where_sql}"
                            if self.order_by:
                                direction = "DESC" if self.order_desc else "ASC"
                                query += f" ORDER BY {self._identifier(self.order_by)} {direction}"
                            cur.execute(query, params)
                            data = [dict(row) for row in cur.fetchall()]

                        elif self.operation == "insert":
                            records = self.payload if isinstance(self.payload, list) else [self.payload]
                            if not records:
                                data = []
                            else:
                                for record in records:
                                    if not isinstance(record, dict) or not record:
                                        raise ValueError("Insert data must be a non-empty dictionary or list of dictionaries.")
                                    cols = list(record.keys())
                                    col_sql = ", ".join(self._identifier(c) for c in cols)
                                    placeholders = ", ".join(["%s"] * len(cols))
                                    values = [self._adapt_value(c, record[c]) for c in cols]
                                    query = (
                                        f"INSERT INTO {table_sql} ({col_sql}) "
                                        f"VALUES ({placeholders}) RETURNING *"
                                    )
                                    cur.execute(query, values)
                                    row = cur.fetchone()
                                    if row:
                                        data.append(dict(row))

                        elif self.operation == "update":
                            if not isinstance(self.payload, dict) or not self.payload:
                                raise ValueError("Update data must be a non-empty dictionary.")
                            assignments = []
                            values = []
                            for col, value in self.payload.items():
                                assignments.append(f"{self._identifier(col)} = %s")
                                values.append(self._adapt_value(col, value))
                            query = (
                                f"UPDATE {table_sql} SET {', '.join(assignments)}"
                                f"{where_sql} RETURNING *"
                            )
                            cur.execute(query, values + params)
                            data = [dict(row) for row in cur.fetchall()]

                        elif self.operation == "delete":
                            query = f"DELETE FROM {table_sql}{where_sql} RETURNING *"
                            cur.execute(query, params)
                            data = [dict(row) for row in cur.fetchall()]
                        else:
                            raise RuntimeError("No database operation was selected.")

            return NeonQueryResponse(data)
        except Exception:
            # Preserve the original exception so existing error handlers can display it.
            raise


class NeonClient:
    def __init__(self, database_url):
        self.database_url = database_url

    def table(self, table_name):
        return NeonTableQuery(self.database_url, table_name)


neon_client = NeonClient(DATABASE_URL)

# Verify Neon connectivity early so deployment/configuration errors are visible.
if DATABASE_URL:
    try:
        with closing(psycopg2.connect(DATABASE_URL, sslmode="require", connect_timeout=15)) as _conn:
            with _conn.cursor() as _cur:
                _cur.execute("SELECT 1")
                _cur.fetchone()
        st.sidebar.success("Neon database connected")
    except Exception as _db_error:
        st.sidebar.error("Neon database connection failed")
        st.error(f"Unable to connect to Neon. Check DATABASE_URL and network access. Details: {_db_error}")

# The rest of the application now uses Neon PostgreSQL; Supabase SDK is not required.

# ---------------------
# App config / state
# ---------------------
#st.set_page_config(page_title="ITSRC Sports Registration (Neon)", page_icon="🏅", layout="wide")

if "user" not in st.session_state:
    st.session_state["user"] = None  # store logged-in user info (email, id, etc.)

# Houses list etc.
houses = ["CC Challengers", "JAO Giants", "Faceless Fighters", "Investigation Warriors"]
CURRENT_SEASON = str(st.secrets.get("CURRENT_SEASON", "2026-27"))
if "admin_view_season" not in st.session_state:
    st.session_state.admin_view_season = CURRENT_SEASON

def selected_season():
    return st.session_state.get("admin_view_season", CURRENT_SEASON)

def db_rows(sql, params=(), fetch=True):
    """Execute parameterized SQL against Neon for season/history workflows."""
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not configured")
    with closing(psycopg2.connect(DATABASE_URL, sslmode="require", connect_timeout=15)) as conn:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql, params)
                return [dict(r) for r in cur.fetchall()] if fetch else cur.rowcount

def available_seasons():
    rows = db_rows("""SELECT season FROM sports_seasons UNION SELECT DISTINCT season FROM participants WHERE season IS NOT NULL UNION SELECT DISTINCT season FROM winners WHERE season IS NOT NULL ORDER BY season DESC""")
    seasons = [r["season"] for r in rows if r.get("season")]
    return list(dict.fromkeys([CURRENT_SEASON] + seasons))

def render_season_selector(key_suffix):
    try:
        seasons = available_seasons()
    except Exception:
        seasons = [CURRENT_SEASON]
    current = st.session_state.get("admin_view_season", CURRENT_SEASON)
    if current not in seasons:
        current = CURRENT_SEASON
    st.selectbox("Season / Year", seasons, index=seasons.index(current), key=f"season_picker_{key_suffix}", on_change=lambda: setattr(st.session_state, "admin_view_season", st.session_state[f"season_picker_{key_suffix}"]))
    return selected_season()

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
# Helper: Neon CRUD wrappers
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
            "season": CURRENT_SEASON,
        }
        resp = neon_client.table("participants").insert(payload).execute()
        return resp
    except Exception as e:
        st.error(f"Error saving participant to Neon: {e}")
        return None

def render_house_tshirt_printing(df_house, house_name, key_prefix):
    """House-scoped T-shirt printing roster and size-wise quantity summary."""
    st.markdown("---")
    st.subheader("👕 T-shirt Printing List")
    st.caption("Prepare a house-wise participant roster and size quantities for T-shirt printing.")

    if df_house is None or df_house.empty:
        st.info("No participant records are available for this house and season.")
        return

    df = df_house.copy()
    if "tshirt_size" not in df.columns:
        st.warning("T-shirt size information is not available in the participant records.")
        return

    status_col = df.get("status", pd.Series("Pending", index=df.index)).fillna("Pending").astype(str)
    status_options = ["Approved only", "Approved + Pending", "All registrations"]
    selected_status = st.selectbox(
        "Include registrations",
        status_options,
        index=0,
        key=f"{key_prefix}_tshirt_status",
        help="For final printing, Approved only is recommended."
    )
    if selected_status == "Approved only":
        df = df[status_col.str.lower() == "approved"].copy()
    elif selected_status == "Approved + Pending":
        df = df[status_col.str.lower().isin(["approved", "pending"])].copy()

    df["tshirt_size"] = df["tshirt_size"].fillna("").astype(str).str.strip().str.upper()
    df = df[df["tshirt_size"].isin(tshirt_sizes)].copy()
    if df.empty:
        st.info("No participants match the selected status filter and have a valid T-shirt size.")
        return

    size_order = [size for size in tshirt_sizes if size in df["tshirt_size"].unique()]
    counts = df["tshirt_size"].value_counts().reindex(size_order, fill_value=0)
    total_col, size_col = st.columns([1, 2])
    with total_col:
        st.metric("👕 Total shirts", int(counts.sum()))
    with size_col:
        st.markdown("**Size-wise quantities**")
        st.dataframe(
            counts.rename_axis("T-shirt Size").reset_index(name="Quantity"),
            hide_index=True,
            use_container_width=True
        )

    output_cols = [
        ("name", "Participant Name"), ("gender", "Gender"),
        ("designation", "Designation"), ("tshirt_size", "T-shirt Size"),
        ("contact", "Contact"), ("status", "Registration Status")
    ]
    available = [(src, label) for src, label in output_cols if src in df.columns]
    print_df = df[[src for src, _ in available]].rename(columns=dict(available)).copy()
    print_df.insert(0, "S. No.", range(1, len(print_df) + 1))
    print_df = print_df.sort_values(["T-shirt Size", "Participant Name"], kind="stable")
    st.dataframe(print_df, hide_index=True, use_container_width=True)

    season_label = selected_season().replace("/", "-")
    safe_house = re.sub(r"[^A-Za-z0-9_-]+", "_", str(house_name)).strip("_")
    csv_bytes = print_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ Download T-shirt Printing List (CSV)",
        data=csv_bytes,
        file_name=f"Tshirt_Printing_{safe_house}_{season_label}.csv",
        mime="text/csv",
        key=f"{key_prefix}_tshirt_download"
    )


def load_all_participants_df(season=None):
    """Load participants for one season; historical seasons remain queryable."""
    try:
        season = season or selected_season()
        resp = neon_client.table("participants").select("*").eq("season", season).order("date_of_reg", desc=False).execute()
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
        resp = neon_client.table("participants").select("*").eq("contact", contact).eq("season", CURRENT_SEASON).execute()
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
# Neon helper: Get participant by record ID
# ---------------------
def get_participant_by_id(record_id):
    try:
        if not neon_client:
            st.error("Neon service client not configured.")
            return pd.DataFrame()
        resp = neon_client.table("participants").select("*").eq("id", record_id).execute()
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

        resp = neon_client.table("participants")\
                         .update(update_fields)\
                         .eq("id", participant_id)\
                         .execute()
        return resp
    except Exception as e:
        st.error(f"Error updating participant status: {e}")
        return None
# ---------------------
# Winners
def load_winners_df(season=None):
    try:
        season = season or selected_season()
        resp = neon_client.table("winners").select("*").eq("season", season).order("created_at", desc=False).execute()
        data = resp.data or []
        return pd.DataFrame(data) if data else []
    except Exception as e:
        st.error(f"Error loading winners: {e}")
        return []

def save_result_draft(event_name, category, positions_dict, participant_refs=None):
    """Store a versioned draft in event_result_history without publishing it."""
    try:
        payload = {"season": selected_season(), "event_name": event_name, "category": category,
                   "results": [{"position": pos, "winner_name": val[0], "house": val[1],
                                "participant_id": (participant_refs or {}).get(pos)}
                               for pos, val in positions_dict.items()],
                   "status": "Draft", "is_locked": False,
                   "entered_by": (st.session_state.get("user") or {}).get("email", "")}
        rows = db_rows("""INSERT INTO event_result_history
            (season,event_name,category,results,status,is_locked,entered_by,created_at,updated_at)
            VALUES (%s,%s,%s,%s::jsonb,'Draft',FALSE,%s,NOW(),NOW()) RETURNING id""",
            (payload["season"], event_name, category, json.dumps(payload["results"]), payload["entered_by"]))
        return rows[0]["id"] if rows else None
    except Exception as e:
        st.error(f"Error saving result draft: {e}")
        return None

def load_result_history(season=None):
    return db_rows("SELECT * FROM event_result_history WHERE season=%s ORDER BY created_at DESC", (season or selected_season(),))

def approve_result(result_id):
    try:
        db_rows("UPDATE event_result_history SET status='Approved', approved_by=%s, updated_at=NOW() WHERE id=%s AND status='Draft' AND is_locked=FALSE",
                ((st.session_state.get("user") or {}).get("email", ""), result_id), fetch=False)
        return True
    except Exception as e:
        st.error(f"Unable to approve result: {e}")
        return False

def publish_result(result_id):
    """Atomically publish an approved version; retain all prior versions in history."""
    try:
        with closing(psycopg2.connect(DATABASE_URL, sslmode="require", connect_timeout=15)) as conn:
            with conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("SELECT * FROM event_result_history WHERE id=%s FOR UPDATE", (result_id,))
                    item = cur.fetchone()
                    if not item or item["status"] != "Approved" or item["is_locked"]:
                        st.error("Only an approved, unlocked result can be published.")
                        return False
                    cur.execute("SELECT 1 FROM event_result_history WHERE season=%s AND event_name=%s AND category=%s AND status='Published' AND is_locked=TRUE LIMIT 1",
                                (item["season"], item["event_name"], item["category"]))
                    if cur.fetchone():
                        st.error("A published result for this event/category is locked. Unlock the earlier result before publishing a correction.")
                        return False
                    results = item["results"] if isinstance(item["results"], list) else json.loads(item["results"])
                    cur.execute("UPDATE event_result_history SET status='Superseded', updated_at=NOW() WHERE season=%s AND event_name=%s AND category=%s AND status='Published'",
                                (item["season"], item["event_name"], item["category"]))
                    cur.execute("DELETE FROM winners WHERE season=%s AND event_name=%s AND category=%s",
                                (item["season"], item["event_name"], item["category"]))
                    for result in results:
                        cur.execute("""INSERT INTO winners (season,event_name,category,position,winner_name,house,participant_id,created_at)
                                      VALUES (%s,%s,%s,%s,%s,%s,%s,NOW())""",
                                    (item["season"], item["event_name"], item["category"], result["position"], result["winner_name"], result.get("house"), result.get("participant_id")))
                    cur.execute("UPDATE event_result_history SET status='Published', published_at=NOW(), updated_at=NOW() WHERE id=%s", (result_id,))
        return True
    except Exception as e:
        st.error(f"Unable to publish result: {e}")
        return False

def lock_result(result_id, locked=True):
    try:
        db_rows("UPDATE event_result_history SET is_locked=%s, updated_at=NOW() WHERE id=%s AND status IN ('Approved','Published')", (locked, result_id), fetch=False)
        return True
    except Exception as e:
        st.error(f"Unable to change result lock: {e}")
        return False

# Draws
def save_match_draw(event_name, gender, df_pairs):
    """
    df_pairs: list of (team1, team2) tuples or DataFrame rows
    """
    try:
        # delete existing for event+gender to avoid duplicates if re-generating
        neon_client.table("match_draws").delete().eq("event_name", event_name).eq("gender", gender).eq("season", selected_season()).execute()
        to_insert = []
        for i, row in enumerate(df_pairs):
            team1, team2 = row[0], row[1]
            to_insert.append({
                "event_name": event_name,
                "gender": gender,
                "season": selected_season(),
                "round": i+1,
                "team1": team1,
                "team2": team2
            })
        if to_insert:
            neon_client.table("match_draws").insert(to_insert).execute()
        return True
    except Exception as e:
        st.error(f"Error saving match draw: {e}")
        return False

def load_draws_for_event(event_name):
    try:
        resp = neon_client.table("match_draws").select("*").eq("event_name", event_name).eq("season", selected_season()).order("round", desc=False).execute()
        data = resp.data or []
        return pd.DataFrame(data) if data else pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading draws: {e}")
        return pd.DataFrame()

# Doubles partners
def save_partner_pair(part):
    try:
        part = dict(part)
        part["season"] = CURRENT_SEASON
        neon_client.table("doubles_partners").insert(part).execute()
        return True
    except Exception as e:
        st.error(f"Error saving partner pair: {e}")
        return False

def load_pairs_for_event(event_name):
    try:
        resp = neon_client.table("doubles_partners").select("*").eq("event_name", event_name).eq("season", selected_season()).execute()
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
            neon_client
            .table("doubles_partners")
            .select("*")
            .eq("season", selected_season())
            .order("id", desc=False)   # <-- changed from created_at to id
            .execute()
        )
        data = resp.data or []
        return pd.DataFrame(data) if data else pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading doubles pairs: {e}")
        return pd.DataFrame()

def is_registered_for_event(all_events_str: str, target_event: str) -> bool:
    """
    Safely check if target_event is in the comma-separated All Selected Events.
    Matching is exact, case-insensitive, and ignores extra spaces.
    """
    if not isinstance(all_events_str, str):
        return False
    events = [e.strip().lower() for e in all_events_str.split(",") if e.strip()]
    return target_event.strip().lower() in events


def delete_partner_pair(pair_id):
    """Delete a doubles pair by ID."""
    try:
        neon_client.table("doubles_partners").delete().eq("id", pair_id).execute()
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
    story.append(Paragraph("<b>ITSRC Annual Sports 2026-27</b>", styles["Title"]))
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
        resp = neon_client.table("admins").select("role, house").eq("email", email).execute()
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
        ["Age (as on 30.11.2026)", str(registration["Age"])],
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
    elements.append(Paragraph(f"(ITSRC, Vadodara - Sports Events {selected_season()})", styles["Heading2"]))
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
        # Do NOT cast to int; let Neon handle it
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
# Auth: Admin login using Neon admin mapping + password hashes in Streamlit secrets
# Admin role/house permissions remain in public.admins; credentials are verified locally from Streamlit secrets.
# Configure [ADMIN_PASSWORD_HASHES] in secrets.toml, with one PBKDF2 hash per admin email.
def verify_admin_password(email, password):
    password_hashes = st.secrets.get("ADMIN_PASSWORD_HASHES", {})
    stored = password_hashes.get(email.strip().lower())
    if not stored:
        return False
    try:
        salt_hex, expected_hex = str(stored).split("$", 1)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(expected_hex)
        actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 310_000)
        return hmac.compare_digest(actual, expected)
    except Exception:
        return False


def do_login():
    st.subheader("🔐 Login")

    email = st.text_input("Email", key="admin_login_email").strip().lower()
    password = st.text_input("Password", type="password", key="admin_login_password")
    login_success = False

    if st.button("Login", key="admin_login_button"):
        try:
            if not DATABASE_URL:
                st.error("Neon database is not configured. Please contact the administrator.")
                return
            if not email or not password:
                st.error("Please enter both email and password.")
                return

            # Only email addresses present in the admins table may log in.
            role_info = get_admin_role_for_email(email)
            if not role_info:
                st.error("This email is not registered as an application administrator.")
            elif not verify_admin_password(email, password):
                st.error("Invalid email or password.")
            else:
                st.session_state["user"] = {"email": email}
                st.success("Login successful! Redirecting...")
                login_success = True
        except Exception as e:
            st.error(f"Login failed: {e}")

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
    st.markdown("""
    <style>
    .reg-hero {background:linear-gradient(120deg,#063f3a 0%,#087f75 58%,#12a594 100%);
        border-radius:18px;padding:22px 26px;color:white;margin:0 0 14px 0;}
    .reg-hero h2 {color:white!important;margin:0 0 5px 0;font-size:27px;}
    .reg-hero p {color:#e5fffa;margin:0;font-size:14px;}
    .reg-chip {display:inline-block;background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.25);
        padding:5px 10px;border-radius:20px;margin:10px 6px 0 0;font-size:12px;color:white;}
    .reg-section {font-size:17px;font-weight:700;color:#087f75;padding:7px 0 5px 0;
        border-bottom:1px solid rgba(8,127,117,.2);margin:8px 0 10px 0;}
    .reg-note {background:#f0faf8;border-left:4px solid #0b9888;border-radius:8px;padding:10px 13px;
        color:#244b47;font-size:13px;margin:8px 0 12px 0;}
    div[data-testid="stForm"] {border:1px solid rgba(8,127,117,.22);border-radius:14px;padding:16px 18px;background:rgba(8,127,117,.025);}
    div[data-testid="stFormSubmitButton"] button {border-radius:10px;min-height:44px;font-weight:700;}
    </style>
    <div class="reg-hero">
      <h2>🏆 ITSRC Sports Meet · 2026–27</h2>
      <p>Income Tax Sports & Recreation Club, Vadodara</p>
      <span class="reg-chip">🗓️ 23 Nov – 20 Dec 2026</span>
      <span class="reg-chip">💳 Registration ₹250</span>
      <span class="reg-chip">⏰ Late fee ₹150 after 13 Dec</span>
    </div>
    """, unsafe_allow_html=True)

    # Registration window and fee rules
    REGISTRATION_START = datetime(2026, 11, 23).date()
    LAST_REG_DATE = datetime(2026, 12, 13).date()
    REGISTRATION_DEADLINE = datetime(2026, 12, 20).date()
    today = datetime.today().date()

    if today < REGISTRATION_START:
        st.info("📅 Registrations open on **23 November 2026**. You can review the details now and submit from the opening date.")
        st.stop()
    if today > REGISTRATION_DEADLINE:
        st.error("🚫 Registration for 2026–27 is closed.")
        st.markdown("Please contact your **House In-charge / Organising Committee** for assistance. The final date, including late fee, was **20 December 2026**.")
        st.stop()

    if today <= LAST_REG_DATE:
        st.success("🟢 Standard-fee registration is open. Submit by **13 December 2026** to avoid the late fee.")
        late_fee = 0
    else:
        st.warning("🟠 Late registration is open until **20 December 2026**. An additional ₹150 late fee applies.")
        late_fee = 150
    final_fee = 250 + late_fee

    st.markdown('<div class="reg-section">👤 Your details</div>', unsafe_allow_html=True)
    age_col, age_hint_col = st.columns([1, 2])
    with age_col:
        age = st.number_input("Age (as on 30.11.2026)", min_value=18, max_value=100, step=1, value=18)
    with age_hint_col:
        if age >= 45:
            st.markdown('<div class="reg-note">⭐ Veteran categories are available for your age group. You may choose regular and veteran events where eligible.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="reg-note">ℹ️ Veteran categories (45 years and above) are hidden. Select the events you wish to participate in below.</div>', unsafe_allow_html=True)

    with st.form("registration_form", clear_on_submit=False):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Full name *", placeholder="Enter your name")
            house = st.selectbox("House *", houses, index=None, placeholder="Choose your house")
            designation = st.selectbox("Post held *", [
                "CCIT", "PCIT", "CIT", "Addl.CIT", "Jt.CIT", "DCIT", "ACIT", "ITO",
                "Sr.PS", "PS", "AO-Gr III", "AO-Gr. II", "AO Gr. I", "ITI", "OS",
                "Steno-II", "TA", "Steno-I", "NS", "MTS", "Other"
            ], index=None, placeholder="Select designation")
        with c2:
            contact = st.text_input("Mobile number *", max_chars=10, placeholder="10-digit mobile number")
            gender = st.selectbox("Gender *", ["Male", "Female", "Other"], index=None, placeholder="Select gender")
            tshirt_size = st.selectbox("T-shirt size *", tshirt_sizes, index=None, placeholder="Select size")
        posting_details = st.text_input("Office / posting details *", placeholder="e.g. Range, Ward, Unit or Office")

        st.markdown('<div class="reg-section">🎯 Choose your sports events</div>', unsafe_allow_html=True)
        st.caption("You can select multiple events. Veteran events appear only when age eligibility is met.")
        selected_events = {}
        visible_categories = [(cat, evts) for cat, evts in event_details.items()
                              if not ("veteran" in cat.lower() and age < 45)]
        left, right = st.columns(2)
        for i, (category, events) in enumerate(visible_categories):
            target_col = left if i % 2 == 0 else right
            with target_col:
                selected_events[category] = st.multiselect(
                    f"{category}", options=events, key=f"reg_events_{category}"
                )

        st.markdown('<div class="reg-section">💳 Registration summary</div>', unsafe_allow_html=True)
        fee1, fee2, fee3 = st.columns(3)
        fee1.metric("Base fee", "₹250")
        fee2.metric("Late fee", f"₹{late_fee}")
        fee3.metric("Total payable", f"₹{final_fee}")
        st.caption("The registration fee is fixed and covers the participant's selected events. Late fee applies from 14 December 2026.")
        st.markdown("<div class='reg-note'>🔒 Please check your name, mobile number, house and event selections before submitting. Your registration will be recorded as pending until verified by the administration.</div>", unsafe_allow_html=True)
        preview_clicked = st.form_submit_button("👀 Preview registration", type="primary", use_container_width=True)

    # Build and validate the registration only after the user requests a preview.
    if preview_clicked:
        if not name or not name.strip():
            st.error("Please enter your full name.")
        elif not house:
            st.error("Please select your house.")
        elif not designation:
            st.error("Please select your post held.")
        elif not posting_details or not posting_details.strip():
            st.error("Please enter your office / posting details.")
        elif not contact.isdigit() or len(contact) != 10:
            st.error("Please enter a valid 10-digit mobile number.")
        elif not gender or not tshirt_size:
            st.error("Please select gender and T-shirt size.")
        else:
            flattened_events = [event for sub_events in selected_events.values() for event in sub_events]
            if not flattened_events:
                st.error("Please select at least one sports event before previewing.")
            else:
                st.session_state["registration_preview"] = {
                    "Name": name.strip(), "Age": age, "Gender": gender, "House": house,
                    "Designation": designation, "Posting Details": posting_details.strip(),
                    "Contact": contact, "T-shirt Size": tshirt_size,
                    "Selected Events": selected_events,
                    "All Selected Events": ", ".join(flattened_events),
                    "Fee": final_fee,
                    "Date of Reg.": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Is Late": bool(late_fee), "Late Fee": late_fee
                }

    # Review panel appears after Preview; no database write occurs at this stage.
    preview = st.session_state.get("registration_preview")
    if preview:
        st.markdown('<div class="reg-section">🧾 Review your registration</div>', unsafe_allow_html=True)
        st.info("Please review every detail carefully. Your registration will only be saved after you select Confirm & Submit.")
        p1, p2, p3 = st.columns(3)
        p1.metric("Participant", preview["Name"])
        p2.metric("House", preview["House"])
        p3.metric("Age", str(preview["Age"]))
        with st.container(border=True):
            st.markdown("**👤 Personal & office details**")
            a, b = st.columns(2)
            with a:
                st.write(f"**Gender:** {preview['Gender']}")
                st.write(f"**Designation:** {preview['Designation']}")
                st.write(f"**Mobile:** {preview['Contact']}")
            with b:
                st.write(f"**Posting:** {preview['Posting Details']}")
                st.write(f"**T-shirt size:** {preview['T-shirt Size']}")
                st.write(f"**Age category:** {'Veteran' if preview['Age'] >= 45 else 'Open'}")
            st.divider()
            st.markdown("**🏅 Selected sports events**")
            for category, events in preview["Selected Events"].items():
                if events:
                    st.markdown(f"**{category}:** " + " · ".join(events))
            st.divider()
            f1, f2, f3 = st.columns(3)
            f1.metric("Base fee", "₹250")
            f2.metric("Late fee", f"₹{preview['Late Fee']}")
            f3.metric("Total payable", f"₹{preview['Fee']}")
        confirm_col, edit_col = st.columns(2)
        with confirm_col:
            confirm_submit = st.button("✅ Confirm & Submit Registration", type="primary", use_container_width=True)
        with edit_col:
            edit_registration = st.button("✏️ Edit details", use_container_width=True)

        if edit_registration:
            st.session_state.pop("registration_preview", None)
            st.rerun()

        if confirm_submit:
            try:
                # Prevent accidental duplicate submission on reruns/double clicks.
                if st.session_state.get("registration_submitting", False):
                    st.warning("Your registration is being submitted. Please wait.")
                else:
                    st.session_state["registration_submitting"] = True
                    resp = insert_participant(preview)
                    if resp and resp.data:
                        inserted_id = resp.data[0].get("id", "")
                        st.session_state.pop("registration_preview", None)
                        st.session_state["registration_submitting"] = False
                        st.success("🎉 Registration successful! Your application has been recorded.")
                        st.balloons()
                        participant_data = {
                            "id": inserted_id, "name": preview["Name"], "post": preview["Designation"],
                            "house": preview["House"], "event": preview["All Selected Events"],
                            "contact": preview["Contact"], "posting": preview["Posting Details"],
                            "category": "Veterans" if preview["Age"] >= 45 else "Normal",
                            "gender": preview["Gender"], "age": preview["Age"], "fee": preview["Fee"],
                            "late_fee": preview["Late Fee"],
                            "registration_date": datetime.now().strftime("%d-%m-%Y"),
                        }
                        base_url = st.secrets.get("APP_BASE_URL", "http://localhost:8501")
                        participant_data["verification_url"] = f"{base_url}/?verify_id={inserted_id}"
                        pdf_path = generate_participant_pdf(
                            participant_data, logo_path=Path("its.gif"),
                            output_path=f"{preview['Name']}_form.pdf"
                        )
                        with open(pdf_path, "rb") as f:
                            st.download_button(
                                label="📄 Download registration form & receipt",
                                data=f, file_name=f"{preview['Name']}_participation_form.pdf",
                                mime="application/pdf", use_container_width=True
                            )
                    else:
                        st.session_state["registration_submitting"] = False
                        st.error("Registration could not be saved. Please try again or contact the organising team.")
            except Exception as exc:
                st.session_state["registration_submitting"] = False
                st.error(f"Registration failed: {exc}")

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

                # constants
                BASE_FEE = 250
                LATE_FEE = 150
                CUTOFF = datetime(2026, 12, 13, 23, 59, 59)  # last date without late fee, inclusive

                # helper to parse date string formats we might have saved
                def _parse_date(s):
                    if not s:
                        return None
                    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d-%m-%Y", "%d-%m-%Y %H:%M:%S"):
                        try:
                            return datetime.strptime(s, fmt)
                        except Exception:
                            pass
                    return None

                # Decide whether late fee was applied originally.
                # Prefer the saved fee (so edit doesn't change it unexpectedly).
                saved_fee = reg.get("fee", None)
                reg_date_str = reg.get("date_of_reg", None)
                reg_dt = _parse_date(reg_date_str)

                # If saved fee present, use it as starting value.
                if saved_fee is not None:
                    total_fee = int(saved_fee)
                else:
                    # fallback: compute by checking registration date (if present) else current time
                    check_dt = reg_dt or datetime.now()
                    total_fee = BASE_FEE + (LATE_FEE if check_dt > CUTOFF else 0)

                # Build selected_events UI (same as registration) but with defaults from DB
                selected_events = {}
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

                    # If you want to recalc fee based on category selections on edit,
                    # uncomment the block below — currently we *preserve saved fee* unless you want recompute.
                    #
                    # if selected_events[category] and category not in selected_categories:
                    #     total_fee += event_fees.get(category, 0)
                    #     selected_categories.add(category)

                # show the fee that will be saved (preserved from DB or computed default)
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
                    response = neon_client.table("participants").update(updated_data).eq("id", reg["id"]).execute()

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
            # Year-wise workspace: historical data is read-only unless explicitly managed.
            render_season_selector("admin")
            st.caption(f"Viewing records for season {selected_season()}")
            if role == "Super Admin":
                with st.expander("⚙️ Season administration", expanded=False):
                    with st.form("create_sports_season_form"):
                        new_season = st.text_input("Add future season (format YYYY-YY)", placeholder="2027-28")
                        create_season = st.form_submit_button("Create season")
                    if create_season:
                        import re as _season_re
                        if not _season_re.fullmatch(r"20\d{2}-\d{2}", new_season.strip()):
                            st.error("Enter the season in YYYY-YY format, e.g. 2027-28.")
                        else:
                            try:
                                db_rows("INSERT INTO sports_seasons (season, is_active, created_at) VALUES (%s,FALSE,NOW()) ON CONFLICT (season) DO NOTHING", (new_season.strip(),), fetch=False)
                                st.success(f"Season {new_season.strip()} is available. Select it from the Season / Year list.")
                                st.rerun()
                            except Exception as season_error:
                                st.error(f"Unable to create season: {season_error}")
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

                # Winners entry tab - candidates are fetched from live registration data.
                with tab_objs[1]:
                    st.subheader("🏆 Results & Winners Management")
                    st.caption("Choose an event to load eligible registered participants automatically, then confirm the actual podium finishers.")

                    events_list = [e for events in event_details.values() for e in events]
                    winner_event = st.selectbox("Sport / Event", events_list, key="winner_event_2026")
                    is_mixed_event = "mixed" in winner_event.lower()
                    is_house_event = winner_event in {"Cricket", "Volleyball", "Tug of War"}
                    is_doubles_event = "doubles" in winner_event.lower()

                    category_options = ["M/F"] if is_mixed_event or is_house_event else ["M", "F"]
                    default_category = "M/F" if category_options == ["M/F"] else "M"
                    category = st.selectbox("Result category", category_options, index=category_options.index(default_category), key="winner_category_2026")

                    participants_for_results = all_participants_df.copy() if not all_participants_df.empty else pd.DataFrame()
                    if not participants_for_results.empty:
                        participants_for_results["status"] = participants_for_results.get("status", "Pending").fillna("Pending")
                        participants_for_results["All Selected Events"] = participants_for_results.get("All Selected Events", participants_for_results.get("all_selected_events", "")).fillna("")
                        participants_for_results = participants_for_results[
                            (participants_for_results["status"].astype(str).str.lower() == "approved") &
                            participants_for_results["All Selected Events"].apply(lambda value: is_registered_for_event(value, winner_event))
                        ].copy()

                    candidate_options = {"": "— Select a finisher —"}
                    candidate_house = {}
                    candidate_winner_name = {}
                    candidate_participant_ref = {}
                    if is_house_event:
                        eligible_houses = sorted(participants_for_results.get("house", pd.Series(dtype=str)).dropna().unique().tolist()) if not participants_for_results.empty else []
                        candidate_options.update({f"HOUSE::{h}": h for h in eligible_houses})
                        candidate_house.update({f"HOUSE::{h}": h for h in eligible_houses})
                        candidate_winner_name.update({f"HOUSE::{h}": h for h in eligible_houses})
                        st.info("This is a house-based team event. Eligible houses are derived from approved registrations for this event.")
                    elif is_doubles_event:
                        registered_pairs = load_pairs_for_event(winner_event)
                        if not registered_pairs.empty:
                            for _, pair in registered_pairs.iterrows():
                                pair_house = str(pair.get("house", "")).strip()
                                pair_label = f"{pair.get('player1_name','')} + {pair.get('player2_name','')} — {pair_house}"
                                pair_key = f"PAIR::{pair.get('id', pair_label)}"
                                candidate_options[pair_key] = pair_label
                                candidate_house[pair_key] = pair_house
                                candidate_winner_name[pair_key] = f"{pair.get('player1_name','')} + {pair.get('player2_name','')}"
                        st.info("Doubles candidates are loaded from the registered doubles-pairs list.")
                    elif not participants_for_results.empty:
                        gender_value = "Male" if category == "M" else "Female" if category == "F" else None
                        eligible = participants_for_results.copy()
                        if gender_value and "gender" in eligible.columns:
                            eligible = eligible[eligible["gender"].astype(str).str.strip().str.lower() == gender_value.lower()]
                        for _, participant in eligible.iterrows():
                            pid = str(participant.get("id", ""))
                            if not pid:
                                continue
                            label = f"{participant.get('name','')} — {participant.get('house','')} | {participant.get('designation','')}"
                            candidate_options[pid] = label
                            candidate_house[pid] = participant.get("house")
                            candidate_winner_name[pid] = str(participant.get("name", "")).strip()
                            candidate_participant_ref[pid] = pid

                    if len(candidate_options) == 1:
                        st.warning("No eligible approved registrations were found for this event. Check the event name, approval status and registrations.")
                    else:
                        st.metric("Eligible candidates", len(candidate_options) - 1)
                        with st.form("winner_entry_form_2026"):
                            st.markdown("#### 🥇 Podium positions")
                            first_id = st.selectbox("1st Place", list(candidate_options), format_func=lambda x: candidate_options[x], key="winner_first_2026")
                            second_id = st.selectbox("2nd Place", list(candidate_options), format_func=lambda x: candidate_options[x], key="winner_second_2026")
                            third_id = st.selectbox("3rd Place (optional)", list(candidate_options), format_func=lambda x: candidate_options[x], key="winner_third_2026")
                            submitted = st.form_submit_button("📝 Save Result Draft", type="primary", use_container_width=True)

                        if submitted:
                            selected_ids = [x for x in [first_id, second_id, third_id] if x]
                            if not first_id or not second_id:
                                st.error("Please select at least 1st and 2nd place.")
                            elif len(selected_ids) != len(set(selected_ids)):
                                st.error("The same participant, pair or house cannot be assigned to more than one position.")
                            else:
                                positions = {}
                                for pos, selected_id in [("1st", first_id), ("2nd", second_id), ("3rd", third_id)]:
                                    if selected_id:
                                        positions[pos] = (candidate_winner_name.get(selected_id, candidate_options[selected_id]), candidate_house.get(selected_id))
                                refs = {pos: candidate_participant_ref.get(sel) for pos, sel in [("1st", first_id), ("2nd", second_id), ("3rd", third_id)] if sel}
                                result_id = save_result_draft(winner_event, category, positions, refs)
                                if result_id:
                                    st.success(f"Draft saved (ID {result_id}). Approve and publish it below to update the Leadership Board.")
                                    st.rerun()

                    st.markdown("---")
                    st.markdown("#### 📚 Recorded results")
                    recorded_winners = load_winners_df()
                    if isinstance(recorded_winners, list):
                        recorded_winners = pd.DataFrame(recorded_winners)
                    if recorded_winners is None or recorded_winners.empty:
                        st.info("No results have been recorded yet.")
                    else:
                        event_results = recorded_winners[recorded_winners["event_name"] == winner_event].copy()
                        if not event_results.empty:
                            event_results = event_results[event_results["category"] == category]
                        if event_results.empty:
                            st.caption("No results recorded for this event and category yet.")
                        else:
                            position_order = {"1st": 1, "2nd": 2, "3rd": 3}
                            event_results["_sort"] = event_results["position"].map(position_order).fillna(9)
                            event_results = event_results.sort_values("_sort")
                            st.dataframe(event_results[[c for c in ["position", "winner_name", "house"] if c in event_results.columns]].rename(columns={"position":"Position", "winner_name":"Winner / Team", "house":"House"}), hide_index=True, use_container_width=True)
                            st.caption("Published results are displayed here. Earlier versions remain available in Result History.")

                    st.markdown("#### 🛡️ Result approval & publication")
                    history_rows = load_result_history()
                    if not history_rows:
                        st.info("No draft or approval records for this season yet.")
                    else:
                        hist_df = pd.DataFrame(history_rows)
                        st.dataframe(hist_df[[c for c in ["id", "event_name", "category", "status", "is_locked", "entered_by", "approved_by", "created_at"] if c in hist_df.columns]], hide_index=True, use_container_width=True)
                        for hist in history_rows:
                            h1, h2, h3, h4 = st.columns([3, 1, 1, 1])
                            h1.write(f"**{hist['event_name']} ({hist['category']})** · {hist['status']} · #{hist['id']}")
                            if hist["status"] == "Draft" and not hist["is_locked"]:
                                if h2.button("Approve", key=f"approve_result_{hist['id']}"):
                                    approve_result(hist["id"]); st.rerun()
                            if hist["status"] == "Approved" and not hist["is_locked"]:
                                if h3.button("Publish", key=f"publish_result_{hist['id']}"):
                                    if publish_result(hist["id"]): st.success("Result published to Leadership Board.")
                                    st.rerun()
                            if hist["status"] in ("Approved", "Published"):
                                label = "Unlock" if hist["is_locked"] else "Lock"
                                if h4.button(label, key=f"lock_result_{hist['id']}"):
                                    lock_result(hist["id"], not hist["is_locked"]); st.rerun()

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
                        render_house_tshirt_printing(df, house, f"super_{i}_{house}")


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

                        render_house_tshirt_printing(df_house, house_name, "house_admin")

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

                event_data = (
                    all_participants_df
                    if role == "Super Admin"
                    else all_participants_df[all_participants_df["house"] == house_name]
                    if not all_participants_df.empty
                    else pd.DataFrame()
                )

                if event_data.empty:
                    st.warning("No registration data available.")
                else:
                    # explode events
                    event_data["All Selected Events"] = event_data["All Selected Events"].fillna("")
                    exploded = event_data.assign(
                        Event=event_data["All Selected Events"].str.split(", ")
                    ).explode("Event")

                    event_list = sorted(exploded["Event"].dropna().unique().tolist())
                    selected_event = st.selectbox("Select Event", options=event_list)

                    if selected_event:
                        filtered = exploded[exploded["Event"] == selected_event]

                        # -------- Relevant Columns Only --------
                        cols = [
                            "Event",
                            "name",
                            "house",
                            "designation",
                            "gender",
                            "age",
                            "contact",
                            "status",
                        ]
                        cols = [c for c in cols if c in filtered.columns]

                        display_df = filtered[cols].rename(
                            columns={
                                "Event": "Event",
                                "name": "Name",
                                "house": "House",
                                "designation": "Designation",
                                "gender": "Gender",
                                "age": "Age",
                                "contact": "Contact",
                                "status": "Status",
                            }
                        )

                        st.write(f"### Participants for **{selected_event}**")
                        st.dataframe(display_df, use_container_width=True)

                        # -------- Event-wise CSV (ONLY selected event) --------
                        st.download_button(
                            label=f"⬇️ Download {selected_event} Participants (CSV)",
                            data=display_df.to_csv(index=False).encode("utf-8"),
                            file_name=f"{selected_event.replace(' ', '_')}_participants.csv",
                            mime="text/csv",
                        )

                        # =====================================================
                        # 🤝 DOUBLES / MIXED DOUBLES – Partner-wise CSV
                        # =====================================================
                        if "double" in selected_event.lower():
                            st.markdown("---")
                            st.subheader("🤝 Doubles Pair List")

                            pairs_df = load_all_pairs()

                            required_cols = {"player1_name", "player2_name", "event_name", "house"}
                            if not required_cols.issubset(pairs_df.columns):
                                st.error("❌ Doubles table schema mismatch.")
                                st.stop()

                            if not pairs_df.empty:
                                pairs_df["Doubles Pair"] = (
                                    pairs_df["player1_name"].str.strip()
                                    + " + "
                                    + pairs_df["player2_name"].str.strip()
                                )


                            if pairs_df.empty:
                                st.info("No doubles pairs registered.")
                            else:
                                # Filter by selected event
                                pairs_df = pairs_df[pairs_df["event_name"] == selected_event]


                                # House admin scope
                                if role != "Super Admin":
                                    pairs_df = pairs_df[pairs_df["house"] == house_name]

                                if pairs_df.empty:
                                    st.info("No doubles pairs found for this event.")
                                else:
                                    

                                    pairs_export = (
                                        pairs_df[["event_name", "Doubles Pair", "house"]]
                                        .drop_duplicates()
                                        .rename(columns={
                                            "event_name": "Event",
                                            "house": "House"
                                        })
                                    )

                                    st.dataframe(pairs_export)
                                    st.download_button(
                                        label="⬇️ Download Doubles Pairs (CSV)",
                                        data=pairs_export.to_csv(index=False).encode("utf-8"),
                                        file_name=f"{selected_event.replace(' ', '_')}_Doubles_Pairs.csv",
                                        mime="text/csv"
                                    )

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
                    collected_fee = filtered_df[filtered_df["fee_collected"] == True]["fee"].sum() if "fee_collected" in filtered_df.columns else 0
                    c1, c2, c3= st.columns(3)
                    c1.metric("Total Fee (by Registration)", f"₹{int(total_fee)}")
                    c2.metric("Collected Fee(Approved)", f"₹{int(collected_fee)}")
                    c3.metric("Average Fee per Participant", f"₹{avg_fee:0.0f}")

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
    st.subheader("Schedule for ITSRC Sports Events 2026-27")
    st.info("Scroll the schedule below or download it for printing.")

    pdf_path = Path("Schedule 2026-27.pdf")

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
            file_name="Schedule 2026-27.pdf",
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
    season = render_season_selector("leaderboard")
    st.caption(f"Official standings · {season}")
    if st.button("🔄 Refresh Leaderboard"):
        st.rerun()

    board_df = compute_leaderboard_from_winners()
    winners_df = load_winners_df(season)
    winners_df = pd.DataFrame(winners_df) if isinstance(winners_df, list) else winners_df
    if winners_df is None: winners_df = pd.DataFrame()

    # Season dashboard metrics
    participant_df = load_all_participants_df(season)
    published_events = winners_df[["event_name", "category"]].drop_duplicates() if not winners_df.empty else pd.DataFrame(columns=["event_name", "category"])
    total_events = len([e for group in event_details.values() for e in group])
    done_events = published_events["event_name"].nunique() if not published_events.empty else 0
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Registered participants", len(participant_df))
    m2.metric("Events with published results", done_events)
    m3.metric("Events pending", max(total_events - done_events, 0))
    m4.metric("Houses competing", participant_df["house"].nunique() if not participant_df.empty and "house" in participant_df else 0)

    if not board_df.empty:
        top_row = board_df.sort_values(["Rank", "Points"], ascending=[True, False]).iloc[0]
        st.markdown(f"<div style='padding:14px 18px;border-radius:12px;background:linear-gradient(90deg,#fff3cd,#fff);border-left:5px solid #d4a017;margin:12px 0'><span style='font-size:25px'>🏆</span> <b style='font-size:20px'>Current House Leader: {top_row['House']} · {int(top_row['Points'])} points</b></div>", unsafe_allow_html=True)
        st.subheader("House Championship Standings")
        html(styled_leaderboard_html(board_df), height=260, scrolling=False)

    # Individual MVP points: individual events only; team-house events excluded.
    st.subheader("🌟 Top 3 Individual MVPs")
    mvp_rows = []
    team_events = {"Cricket", "Volleyball", "Tug of War"}
    if not winners_df.empty:
        individual = winners_df[~winners_df["event_name"].isin(team_events) & ~winners_df["event_name"].astype(str).str.contains("doubles", case=False, na=False)].copy()
        score_map = {"1st": 5, "2nd": 3, "3rd": 1}
        individual["MVP Points"] = individual["position"].map(score_map).fillna(0)
        # Resolve legacy records lacking participant_id by matching participant name + house.
        for _, win in individual.iterrows():
            pid = win.get("participant_id")
            if (not pid or pd.isna(pid)) and not participant_df.empty:
                matches = participant_df[(participant_df["name"].astype(str).str.casefold() == str(win["winner_name"]).casefold()) & (participant_df["house"].astype(str) == str(win.get("house", "")))]
                pid = str(matches.iloc[0]["id"]) if not matches.empty else str(win["winner_name"]) + "|" + str(win.get("house", ""))
            mvp_rows.append({"Participant ID": str(pid), "Participant": win["winner_name"], "House": win.get("house", ""), "MVP Points": int(win["MVP Points"]), "Event": win["event_name"], "Position": win["position"]})
    if mvp_rows:
        mvp_detail = pd.DataFrame(mvp_rows)
        mvp = mvp_detail.groupby(["Participant ID", "Participant", "House"], as_index=False).agg(**{"MVP Points": ("MVP Points", "sum"), "Medals": ("Position", "count"), "Events": ("Event", lambda x: ", ".join(sorted(set(x))))})
        mvp = mvp.sort_values(["MVP Points", "Medals", "Participant"], ascending=[False, False, True]).head(3).reset_index(drop=True)
        mvp.insert(0, "Rank", range(1, len(mvp) + 1))
        st.dataframe(mvp[["Rank", "Participant", "House", "MVP Points", "Medals", "Events"]], hide_index=True, use_container_width=True)
    else:
        st.info("MVP rankings will appear after individual event results are published.")

    # Event completion tracker
    st.subheader("📅 Event Completion Tracker")
    event_names = [e for group in event_details.values() for e in group]
    completed = set(published_events["event_name"].tolist()) if not published_events.empty else set()
    tracker = pd.DataFrame([{"Event": e, "Status": "Published" if e in completed else "Awaiting results"} for e in event_names])
    st.dataframe(tracker, hide_index=True, use_container_width=True)

    # Participant achievement history
    st.subheader("🎖️ Participant Achievement History")
    try:
        all_year_results = pd.DataFrame(db_rows("SELECT season,event_name,category,position,winner_name,house FROM winners ORDER BY season DESC, event_name", ()))
    except Exception:
        all_year_results = pd.DataFrame()
    if not all_year_results.empty:
        achievement_names = sorted(all_year_results["winner_name"].dropna().astype(str).unique().tolist())
        chosen_person = st.selectbox("Find participant / team (all seasons)", achievement_names, key="achievement_person") if achievement_names else None
        if chosen_person:
            achievements = all_year_results[all_year_results["winner_name"].astype(str) == chosen_person].copy()
            st.dataframe(achievements[[c for c in ["season", "event_name", "category", "position", "house"] if c in achievements.columns]].rename(columns={"season":"Season", "event_name":"Event", "category":"Category", "position":"Position", "house":"House"}), hide_index=True, use_container_width=True)
    else:
        st.caption("No published achievements are available yet.")

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📄 Generate Leadership Board PDF", use_container_width=True):
            pdf_buf = generate_leadership_board_pdf(board_df, winners_df)
            st.download_button("Download Leadership Board PDF", data=pdf_buf, file_name=f"Leadership_Board_{season}.pdf", mime="application/pdf")
    with c2:
        if not winners_df.empty:
            st.download_button("⬇️ Export published results (CSV)", data=winners_df.to_csv(index=False).encode("utf-8"), file_name=f"Published_Results_{season}.csv", mime="text/csv", use_container_width=True)

