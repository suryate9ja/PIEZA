import streamlit as st
import uuid
import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta

from utils import (
    show_navbar,
    apply_custom_css,
    calculate_emi,
    fetch_loans,
    add_loan,
    delete_loan,
    fetch_credit_cards,
    add_credit_card,
    delete_credit_card,
    _next_emi_date,
)

st.set_page_config(
    page_title="Loans & Reminders — PIEZA",
    layout="wide",
)
apply_custom_css()
show_navbar("Loans")

# ── Page header ────────────────────────────────────────────────────────────────
st.title("Loans and Reminders")
st.markdown(
    "Track your loans and EMIs, manage credit card due dates, "
    "and get upcoming payment reminders — all in one place."
)

st.markdown("---")

tab_loans, tab_cards = st.tabs(["Loans and EMI", "Credit Cards"])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Loans and EMI
# ══════════════════════════════════════════════════════════════════════════════
with tab_loans:
    st.subheader("Active loans")

    loan_df = fetch_loans()

    # ── Add loan form ───────────────────────────────────────────────────────
    with st.expander("Add a new loan", expanded=loan_df.empty):
        with st.form("loan_form", clear_on_submit=True):
            c1, c2 = st.columns(2, gap="large")

            with c1:
                loan_name = st.text_input(
                    "Loan name",
                    placeholder="e.g. Home Loan, Car Loan",
                )
                bank = st.text_input(
                    "Lender / bank",
                    placeholder="e.g. HDFC Bank, SBI",
                )
                principal = st.number_input(
                    "Original principal amount",
                    min_value=0.0,
                    format="%.2f",
                    step=1000.0,
                    help="The full loan amount when it was sanctioned.",
                )
                principal_left = st.number_input(
                    "Principal amount left (outstanding)",
                    min_value=0.0,
                    format="%.2f",
                    step=1000.0,
                    help=(
                        "For a brand-new loan, this equals the original principal. "
                        "For an existing/old loan, enter the remaining balance as of today."
                    ),
                )
                interest_rate = st.number_input(
                    "Annual interest rate (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=10.0,
                    format="%.2f",
                    step=0.25,
                )

            with c2:
                tenure = st.number_input(
                    "Total tenure (months)",
                    min_value=1,
                    max_value=360,
                    value=12,
                    step=1,
                    help="Full loan duration in months.",
                )
                emi_day = st.number_input(
                    "EMI day of month",
                    min_value=1,
                    max_value=28,
                    value=1,
                    step=1,
                    help="Day of the month on which EMI is debited (1–28).",
                )
                start_date = st.date_input(
                    "Loan start date",
                    value=date.today(),
                    help="The date on which the loan was originally disbursed.",
                )
                status = st.selectbox("Status", ["Active", "Closed"])

            # ── Auto-computed end date preview ──────────────────────────────
            try:
                end_date = start_date + relativedelta(months=int(tenure))
            except Exception:
                end_date = None

            # ── Live EMI + end-date preview ─────────────────────────────────
            if principal > 0 and tenure > 0:
                # Use principal_left for EMI if it's entered, else fall back to principal
                emi_base = principal_left if principal_left > 0 else principal
                emi_preview = calculate_emi(emi_base, interest_rate, tenure)
                preview_parts = [
                    f"Estimated monthly EMI: **{emi_preview:,.2f}**  "
                    f"(at {interest_rate:.2f}% p.a. over {tenure} months)"
                ]
                if end_date:
                    preview_parts.append(
                        f"Loan end date: **{end_date.strftime('%d %b %Y')}**"
                    )
                st.info("  \n".join(preview_parts))

            submitted = st.form_submit_button("Save loan", type="primary")

            if submitted:
                if not loan_name.strip():
                    st.error("Loan name is required.")
                elif principal <= 0:
                    st.error("Principal must be greater than zero.")
                elif principal_left > principal:
                    st.error("Principal left cannot exceed the original principal amount.")
                else:
                    p_left = principal_left if principal_left > 0 else principal
                    emi_amount = calculate_emi(p_left, interest_rate, int(tenure))
                    computed_end = (
                        (start_date + relativedelta(months=int(tenure))).strftime("%Y-%m-%d")
                        if end_date else ""
                    )
                    loan_data = {
                        "ID":              str(uuid.uuid4()),
                        "Profile":         st.session_state.get("active_profile", ""),
                        "Loan Name":       loan_name.strip(),
                        "Bank":            bank.strip(),
                        "Principal":       principal,
                        "Principal Left":  p_left,
                        "Interest Rate %": interest_rate,
                        "Tenure Months":   int(tenure),
                        "EMI Day":         int(emi_day),
                        "EMI Amount":      emi_amount,
                        "Start Date":      start_date.strftime("%Y-%m-%d"),
                        "End Date":        computed_end,
                        "Status":          status,
                    }
                    if add_loan(loan_data):
                        st.success(
                            f"Loan '{loan_name}' saved — "
                            f"EMI {emi_amount:,.2f} / month, "
                            f"closes {computed_end or 'N/A'}."
                        )
                        st.rerun()

    st.markdown("---")

    if loan_df.empty:
        st.info("No loans found. Add your first loan using the form above.")
    else:
        today = date.today()

        # ── Enrich display table ────────────────────────────────────────────
        # Next EMI date
        try:
            loan_df["Next EMI"] = loan_df.apply(
                lambda r: _next_emi_date(int(r["EMI Day"])).strftime("%d %b %Y")
                if str(r.get("Status", "")).lower() == "active" else "—",
                axis=1,
            )
        except Exception:
            loan_df["Next EMI"] = "—"

        # Repayment progress % (amount repaid / original principal)
        def _progress(row) -> float:
            try:
                orig = float(row.get("Principal", 0) or 0)
                left = float(row.get("Principal Left", orig) or orig)
                if orig <= 0:
                    return 0.0
                paid = orig - left
                return max(0.0, min(100.0, round(paid / orig * 100, 1)))
            except Exception:
                return 0.0

        loan_df["Repaid %"] = loan_df.apply(_progress, axis=1)

        # ── Loan cards with progress bars ───────────────────────────────────
        for _, row in loan_df.iterrows():
            status_val = str(row.get("Status", "")).lower()
            name  = row.get("Loan Name", "Loan")
            bank_ = row.get("Bank", "")
            orig  = float(row.get("Principal", 0) or 0)
            left  = float(row.get("Principal Left", orig) or orig)
            rate  = row.get("Interest Rate %", "")
            emi   = float(row.get("EMI Amount", 0) or 0)
            start = row.get("Start Date", "")
            end   = row.get("End Date", "")
            next_emi = row.get("Next EMI", "—")
            repaid_pct = float(row.get("Repaid %", 0))

            badge_color = "#4CAF50" if status_val == "active" else "#9E9E9E"
            bar_color   = "#4CAF50" if repaid_pct < 80 else "#1B5E20"

            st.markdown(
                f"""
                <div style="background:#FFFFFF;border:1px solid #E8F5E9;border-left:4px solid {badge_color};
                            border-radius:10px;padding:1.2rem 1.5rem;margin-bottom:1rem;
                            box-shadow:0 1px 4px rgba(27,94,32,0.07);">
                  <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.5rem;">
                    <div>
                      <span style="font-size:1.05rem;font-weight:700;color:#1B5E20;">{name}</span>
                      {'&nbsp;<span style="font-size:0.75rem;color:#757575;">· ' + bank_ + '</span>' if bank_ else ''}
                    </div>
                    <span style="font-size:0.72rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;
                                 color:{badge_color};background:{'#E8F5E9' if status_val=='active' else '#F5F5F5'};
                                 padding:0.2rem 0.6rem;border-radius:20px;">
                      {row.get("Status", "—")}
                    </span>
                  </div>
                  <div style="display:flex;gap:2.5rem;flex-wrap:wrap;font-size:0.85rem;color:#4A4A4A;margin-bottom:0.9rem;">
                    <div><span style="color:#757575;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.07em;">Original</span><br>
                         <strong style="font-size:1rem;">{orig:,.2f}</strong></div>
                    <div><span style="color:#757575;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.07em;">Outstanding</span><br>
                         <strong style="font-size:1rem;color:#C62828;">{left:,.2f}</strong></div>
                    <div><span style="color:#757575;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.07em;">EMI / month</span><br>
                         <strong style="font-size:1rem;">{emi:,.2f}</strong></div>
                    <div><span style="color:#757575;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.07em;">Rate</span><br>
                         <strong>{rate}%</strong></div>
                    <div><span style="color:#757575;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.07em;">Start → End</span><br>
                         <strong>{start} → {end if end else '—'}</strong></div>
                    <div><span style="color:#757575;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.07em;">Next EMI</span><br>
                         <strong>{next_emi}</strong></div>
                  </div>
                  <div style="background:#E8F5E9;border-radius:99px;height:8px;overflow:hidden;">
                    <div style="width:{repaid_pct}%;background:{bar_color};height:100%;
                                border-radius:99px;transition:width 0.6s ease;"></div>
                  </div>
                  <div style="font-size:0.72rem;color:#757575;margin-top:0.35rem;">{repaid_pct:.1f}% repaid</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.caption(f"Showing {len(loan_df)} loan(s).")

        # ── Aggregate summary ───────────────────────────────────────────────
        try:
            loan_df["Principal Left"]  = pd.to_numeric(loan_df["Principal Left"],  errors="coerce").fillna(0)
            loan_df["EMI Amount"]      = pd.to_numeric(loan_df["EMI Amount"],       errors="coerce").fillna(0)
            active = loan_df[loan_df["Status"].str.lower() == "active"]

            m1, m2, m3 = st.columns(3)
            m1.metric("Total Outstanding",  f"{active['Principal Left'].sum():,.2f}")
            m2.metric("Total EMI / month",  f"{active['EMI Amount'].sum():,.2f}")
            m3.metric("Active loans",        str(len(active)))
        except Exception:
            pass

        # ── Delete loans ────────────────────────────────────────────────────
        st.markdown("---")
        with st.expander("Delete loans"):
            if "ID" not in loan_df.columns:
                st.warning("ID column missing — cannot delete.")
            else:
                id_label = {
                    str(r["ID"]): (
                        f"{r.get('Loan Name', '')}  |  {r.get('Bank', '')}  "
                        f"|  {r.get('Principal Left', '')} left"
                    )
                    for _, r in loan_df.iterrows()
                }
                selected = st.multiselect(
                    "Select loans to remove",
                    options=list(id_label.keys()),
                    format_func=lambda x: id_label.get(x, x),
                    placeholder="Choose one or more loans…",
                )
                if st.button("Delete selected loans", type="primary"):
                    if not selected:
                        st.warning("Please select at least one loan.")
                    else:
                        with st.spinner("Deleting…"):
                            if delete_loan(selected):
                                st.success(f"{len(selected)} loan(s) deleted.")
                                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Credit Cards
# ══════════════════════════════════════════════════════════════════════════════
with tab_cards:
    st.subheader("Credit cards")

    card_df = fetch_credit_cards()

    # ── Add card form ───────────────────────────────────────────────────────
    with st.expander("Add a new credit card", expanded=card_df.empty):
        with st.form("card_form", clear_on_submit=True):
            c1, c2 = st.columns(2, gap="large")

            with c1:
                card_name = st.text_input(
                    "Card name",
                    placeholder="e.g. HDFC Regalia, SBI SimplyCLICK",
                )
                card_bank = st.text_input(
                    "Issuing bank",
                    placeholder="e.g. HDFC Bank, Axis Bank",
                )
                credit_limit = st.number_input(
                    "Credit limit",
                    min_value=0.0,
                    format="%.2f",
                    step=1000.0,
                )
                outstanding = st.number_input(
                    "Outstanding balance",
                    min_value=0.0,
                    format="%.2f",
                    step=100.0,
                )

            with c2:
                min_payment = st.number_input(
                    "Minimum payment due",
                    min_value=0.0,
                    format="%.2f",
                    step=100.0,
                )
                due_date = st.date_input(
                    "Payment due date",
                    value=date.today(),
                )
                card_status = st.selectbox("Status", ["Active", "Closed"])

            # Utilisation preview
            if credit_limit > 0 and outstanding > 0:
                util_pct = outstanding / credit_limit * 100
                util_color = "red" if util_pct > 80 else ("orange" if util_pct > 40 else "green")
                st.markdown(
                    f"Credit utilisation: "
                    f"<span style='color:{util_color};font-weight:700'>{util_pct:.1f}%</span>",
                    unsafe_allow_html=True,
                )

            card_submitted = st.form_submit_button("Save card", type="primary")

            if card_submitted:
                if not card_name.strip():
                    st.error("Card name is required.")
                else:
                    card_data = {
                        "ID":           str(uuid.uuid4()),
                        "Profile":      st.session_state.get("active_profile", ""),
                        "Card Name":    card_name.strip(),
                        "Bank":         card_bank.strip(),
                        "Credit Limit": credit_limit,
                        "Outstanding":  outstanding,
                        "Min Payment":  min_payment,
                        "Due Date":     due_date.strftime("%Y-%m-%d"),
                        "Status":       card_status,
                    }
                    if add_credit_card(card_data):
                        st.success(f"Card '{card_name}' saved.")
                        st.rerun()

    st.markdown("---")

    if card_df.empty:
        st.info("No credit cards found. Add your first card using the form above.")
    else:
        today = date.today()

        def _days_until(raw_date: str) -> int:
            try:
                return (date.fromisoformat(str(raw_date)) - today).days
            except Exception:
                return 999

        card_df["Days Until Due"] = card_df["Due Date"].apply(_days_until)

        def _urgency(days: int, status: str) -> str:
            if str(status).lower() == "closed":
                return "Closed"
            if days < 0:
                return "Overdue"
            if days <= 3:
                return "Due soon"
            if days <= 7:
                return "This week"
            return "Upcoming"

        card_df["Urgency"] = card_df.apply(
            lambda r: _urgency(r["Days Until Due"], r.get("Status", "")), axis=1
        )

        display_cols = [
            c for c in
            ["Card Name", "Bank", "Credit Limit", "Outstanding",
             "Min Payment", "Due Date", "Days Until Due", "Urgency", "Status"]
            if c in card_df.columns
        ]

        st.dataframe(
            card_df[display_cols],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Credit Limit":   st.column_config.NumberColumn("Credit Limit",  format="%.2f"),
                "Outstanding":    st.column_config.NumberColumn("Outstanding",    format="%.2f"),
                "Min Payment":    st.column_config.NumberColumn("Min Payment",    format="%.2f"),
                "Days Until Due": st.column_config.NumberColumn("Days Until Due"),
            },
        )

        st.caption(f"Showing {len(card_df)} card(s).")

        # Overdue / urgent callout
        urgent = card_df[card_df["Days Until Due"] <= 3]
        if not urgent.empty:
            for _, row in urgent.iterrows():
                days = int(row["Days Until Due"])
                label = "today" if days == 0 else (f"in {days} day(s)" if days > 0 else "overdue")
                st.warning(
                    f"**{row.get('Card Name', 'Card')}** — minimum payment of "
                    f"{row.get('Min Payment', '—')} is due {label}."
                )

        # ── Delete cards ────────────────────────────────────────────────────
        st.markdown("---")
        with st.expander("Delete credit cards"):
            if "ID" not in card_df.columns:
                st.warning("ID column missing — cannot delete.")
            else:
                card_id_label = {
                    str(r["ID"]): f"{r.get('Card Name', '')}  |  {r.get('Bank', '')}  |  due {r.get('Due Date', '')}"
                    for _, r in card_df.iterrows()
                }
                selected_cards = st.multiselect(
                    "Select cards to remove",
                    options=list(card_id_label.keys()),
                    format_func=lambda x: card_id_label.get(x, x),
                    placeholder="Choose one or more cards…",
                )
                if st.button("Delete selected cards", type="primary"):
                    if not selected_cards:
                        st.warning("Please select at least one card.")
                    else:
                        with st.spinner("Deleting…"):
                            if delete_credit_card(selected_cards):
                                st.success(f"{len(selected_cards)} card(s) deleted.")
                                st.rerun()
