import streamlit as st
from utils import show_navbar, apply_custom_css

st.set_page_config(
    page_title="Settings — PIEZA",
    layout="wide",
)
apply_custom_css()
show_navbar("Settings")

# ── Check if arriving from edit-profile link ───────────────────────────────────
edit_target = st.query_params.get("edit_profile", None)
if edit_target:
    st.session_state["_settings_edit_profile"] = edit_target
    del st.query_params["edit_profile"]

st.title("Settings")
st.markdown("Manage your API keys, profiles, and application preferences.")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — AI Settings
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("AI Settings")
st.markdown(
    """
    <div style="
        background:#FFFFFF;border:1px solid #E8E8E8;border-top:3px solid #4CAF50;
        border-radius:12px;padding:1.5rem 1.75rem;margin-bottom:1.5rem;
        box-shadow:0 1px 4px rgba(0,0,0,0.05);
    ">
        <div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;
                    letter-spacing:0.1em;color:#757575;margin-bottom:0.35rem;">Gemini API Key</div>
        <p style="font-size:0.87rem;color:#555;margin:0 0 0.75rem;line-height:1.5;">
            Required for the AI screenshot scanner and AI Financial Advisor.
            Get your key from <strong>Google AI Studio</strong>.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

api_col, status_col = st.columns([3, 1])

with api_col:
    new_key = st.text_input(
        "Gemini API key",
        value=st.session_state.get("gemini_api_key", ""),
        type="password",
        placeholder="Paste your Gemini API key here…",
        help="Your key is stored only in the current session and never sent anywhere except Google.",
    )
    if st.button("Save API key", type="primary"):
        st.session_state.gemini_api_key = new_key.strip()
        st.success("API key saved for this session.")
        st.rerun()

with status_col:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.session_state.get("gemini_api_key"):
        st.success("Key active")
    else:
        st.warning("Not set")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — Profile Management
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("Profiles")
st.markdown("Manage family member profiles. Each profile has its own transactions, loans, and cards.")

# Determine which profile to show in the editor by default
default_edit = st.session_state.pop("_settings_edit_profile", None)
profiles = st.session_state.get("profiles", ["Default Family"])

# ── Add new profile ────────────────────────────────────────────────────────────
with st.expander("Add new profile", expanded=not bool(default_edit)):
    with st.form("add_profile_form", clear_on_submit=True):
        new_name = st.text_input("Profile name", placeholder="e.g. Priya, Dad, Joint Account")
        if st.form_submit_button("Create profile", type="primary"):
            if not new_name.strip():
                st.error("Please enter a name.")
            elif new_name.strip() in st.session_state.profiles:
                st.warning(f"'{new_name.strip()}' already exists.")
            else:
                st.session_state.profiles.append(new_name.strip())
                st.success(f"Profile '{new_name.strip()}' created.")
                st.rerun()

st.markdown("---")

# ── Existing profiles ──────────────────────────────────────────────────────────
st.markdown(
    '<p class="section-label">Existing profiles</p>',
    unsafe_allow_html=True,
)

for profile in list(st.session_state.profiles):
    initial = profile[0].upper() if profile else "?"
    is_active = profile == st.session_state.get("active_profile")
    active_badge = (
        '<span style="font-size:0.7rem;font-weight:700;background:#EBF5EB;'
        'color:#1B5E20;padding:0.18rem 0.5rem;border-radius:10px;'
        'border:1px solid #A5D6A7;margin-left:0.5rem;">Active</span>'
        if is_active else ""
    )

    # Profile card
    st.markdown(
        f"""
        <div style="background:#FFFFFF;border:1px solid #E8E8E8;border-radius:10px;
                    padding:1rem 1.25rem;margin-bottom:0.75rem;
                    box-shadow:0 1px 4px rgba(0,0,0,0.04);
                    display:flex;align-items:center;gap:1rem;">
            <div style="width:44px;height:44px;border-radius:50%;background:#1B5E20;
                        color:white;display:flex;align-items:center;justify-content:center;
                        font-size:1.1rem;font-weight:700;flex-shrink:0;">
                {initial}
            </div>
            <div style="flex:1;">
                <span style="font-size:1rem;font-weight:600;color:#1A1A1A;">{profile}</span>
                {active_badge}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Expand edit controls if this is the one from edit_profile query param
    is_edit_target = (default_edit == profile)
    with st.expander(f"Edit — {profile}", expanded=is_edit_target):
        # Set as active
        col_activate, col_delete = st.columns([2, 1])
        with col_activate:
            if not is_active:
                if st.button(f"Set as active profile", key=f"activate_{profile}"):
                    st.session_state.active_profile = profile
                    st.success(f"Now viewing as '{profile}'.")
                    st.rerun()
            else:
                st.caption("This is the currently active profile.")

        # Profile picture upload
        st.markdown("**Profile picture**")
        pic_col, action_col = st.columns([2, 1])
        with pic_col:
            uploaded = st.file_uploader(
                "Upload photo",
                type=["png", "jpg", "jpeg"],
                key=f"pic_{profile}",
                label_visibility="collapsed",
            )
            if uploaded:
                st.session_state.profile_pictures[profile] = uploaded.getvalue()
                st.success("Photo updated.")
                st.rerun()

        with action_col:
            if profile in st.session_state.get("profile_pictures", {}):
                st.image(
                    st.session_state.profile_pictures[profile],
                    width=80,
                    caption=profile,
                )
                if st.button("Remove photo", key=f"remove_pic_{profile}"):
                    del st.session_state.profile_pictures[profile]
                    st.success("Photo removed.")
                    st.rerun()
            else:
                st.caption("No photo set.")

        # Delete profile
        with col_delete:
            if len(st.session_state.profiles) > 1:
                if st.button(
                    "Delete profile",
                    key=f"delete_{profile}",
                    type="secondary",
                ):
                    st.session_state.profiles.remove(profile)
                    if st.session_state.get("profile_pictures", {}).pop(profile, None):
                        pass
                    if st.session_state.get("active_profile") == profile:
                        st.session_state.active_profile = st.session_state.profiles[0]
                    st.success(f"Profile '{profile}' deleted.")
                    st.rerun()
            else:
                st.caption("Cannot delete the only profile.")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — Application Settings
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("Application Settings")

with st.expander("Google Sheets configuration"):
    st.markdown(
        """
        **Sheet name** — the app connects to a Google Sheet named `PIEZA_DB` by default.
        If you've renamed it, update `secrets.toml`:

        ```toml
        sheet_name = "MY_CUSTOM_NAME"
        ```

        **Required worksheets and headers:**

        | Worksheet | Headers |
        |-----------|---------|
        | Sheet1 (main) | ID, Profile, Date, Type, Category, Amount, Bank Name, Has Proof |
        | Loans | ID, Profile, Loan Name, Bank, Principal, Principal Left, Interest Rate %, Tenure Months, EMI Day, EMI Amount, Start Date, End Date, Status |
        | CreditCards | ID, Profile, Card Name, Bank, Credit Limit, Outstanding, Min Payment, Due Date, Status |
        """
    )

with st.expander("About PIEZA"):
    st.markdown(
        """
        **PIEZA** is a personal family finance tracker built with Streamlit,
        Google Sheets, and the Gemini AI API.

        - All data is stored in your own Google Sheet — nothing is stored on any server.
        - The Gemini API key is kept in your browser session only.
        - Profiles are session-scoped; for persistent profiles across sessions,
          store them in `.streamlit/secrets.toml` or your Google Sheet.
        """
    )
