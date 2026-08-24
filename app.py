import json
import random
import string
from pathlib import Path
from datetime import datetime
import streamlit as st
import pandas as pd
import plotly.express as px

# ============================================================
# PAGE CONFIGURATION & ENTERPRISE STYLING
# ============================================================
st.set_page_config(
    page_title="Apex Financial - Core Banking System",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #0B0F19;
        color: #E2E8F0;
    }

    .stApp {
        background-color: #0B0F19;
    }

    /* Disable Auto-fill visual overlays */
    input:-webkit-autofill,
    input:-webkit-autofill:hover, 
    input:-webkit-autofill:focus, 
    input:-webkit-autofill:active {
        -webkit-box-shadow: 0 0 0 30px #111827 inset !important;
        -webkit-text-fill-color: #F8FAFC !important;
        transition: background-color 5000s ease-in-out 0s;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #111827 !important;
        border-right: 1px solid #1F2937 !important;
    }
    
    .brand-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #F8FAFC;
        letter-spacing: 0.05em;
        margin-bottom: 2px;
    }

    .brand-subtitle {
        font-size: 0.75rem;
        color: #64748B;
        margin-bottom: 24px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    /* Navigation Menu */
    div[role="radiogroup"] label {
        background: #1E293B !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        padding: 10px 14px !important;
        color: #94A3B8 !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        margin-bottom: 8px !important;
        transition: all 0.2s ease;
    }
    div[role="radiogroup"] label:hover {
        border-color: #0284C7 !important;
        color: #F8FAFC !important;
    }
    div[role="radiogroup"] label[data-checked="true"] {
        background: #0284C7 !important;
        border-color: #38BDF8 !important;
        color: #FFFFFF !important;
    }

    /* KPI Cards */
    .kpi-card {
        background: #111827;
        border: 1px solid #1F2937;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }
    .kpi-title {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #64748B;
        font-weight: 600;
    }
    .kpi-value {
        font-size: 1.85rem;
        font-weight: 700;
        color: #F8FAFC;
        margin-top: 6px;
    }
    .kpi-value-green { color: #10B981; }
    .kpi-value-blue { color: #38BDF8; }

    /* Account Receipt & Transaction Banner Styling */
    .account-card {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 1px solid #0284C7;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 10px 25px -5px rgba(2, 132, 199, 0.25);
        margin-top: 15px;
    }
    .card-id {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.6rem;
        font-weight: 700;
        letter-spacing: 2px;
        color: #38BDF8;
        margin: 12px 0;
        background: #0F172A;
        padding: 12px;
        border-radius: 8px;
        border: 1px dashed #0284C7;
        text-align: center;
    }

    .success-banner {
        background: linear-gradient(90deg, #064E3B 0%, #022C22 100%);
        border: 1px solid #10B981;
        border-radius: 10px;
        padding: 20px;
        margin-top: 15px;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.15);
    }

    /* Primary Action Buttons */
    div.stButton > button {
        background: #0284C7 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        width: 100%;
        transition: background 0.2s ease !important;
    }
    div.stButton > button:hover {
        background: #0369A1 !important;
    }
</style>
""", unsafe_allow_html=True)

# Disable Auto-complete script injection
st.components.v1.html("""
<script>
    const inputs = window.parent.document.querySelectorAll('input');
    inputs.forEach(input => {
        input.setAttribute('autocomplete', 'new-password');
        input.setAttribute('aria-autocomplete', 'none');
    });
</script>
""", height=0)

# ============================================================
# BACKEND CORE ENGINE
# ============================================================
class BankEngine:
    database = "data.json"

    @classmethod
    def load_records(cls):
        try:
            db_path = Path(cls.database)
            if not db_path.exists():
                db_path.write_text("[]", encoding="utf-8")
                return []
            
            with open(db_path, "r", encoding="utf-8") as fs:
                content = fs.read().strip()
                if not content:
                    return []
                data = json.loads(content)
                if isinstance(data, list):
                    for rec in data:
                        rec.setdefault("acc_type", "Standard Account")
                        rec.setdefault("balance", 0.0)
                        rec.setdefault("created_at", "N/A")
                        rec.setdefault("history", [])
                    return data
                return []
        except Exception:
            return []

    @classmethod
    def save_records(cls, data):
        try:
            with open(cls.database, "w", encoding="utf-8") as fs:
                json.dump(data, fs, indent=4)
            return True
        except Exception:
            return False

    @classmethod
    def generate_account_number(cls):
        alpha = "".join(random.choices(string.ascii_uppercase, k=3))
        dig = "".join(random.choices(string.digits, k=3))
        spchr = "".join(random.choices("!@#$%&*", k=1))
        combined = list(alpha + dig + spchr)
        random.shuffle(combined)
        return "".join(combined)

    def create_account(self, name, age, email, pin, acc_type):
        data = self.load_records()
        
        if not name or not email:
            return False, "Validation Error: Holder Name and Email Address are required.", None
        if age is None or age < 18:
            return False, "Validation Error: Minimum age requirement is 18 years.", None
        if not pin or len(str(pin)) != 4 or not str(pin).isdigit():
            return False, "Validation Error: Security PIN must be exactly 4 digits.", None

        acc_no = self.generate_account_number()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        record = {
            "acc_no": acc_no,
            "name": name.strip(),
            "age": int(age),
            "email": email.strip(),
            "pin": int(pin),
            "acc_type": acc_type,
            "balance": 0.0,
            "created_at": timestamp,
            "history": []
        }
        
        data.append(record)
        if self.save_records(data):
            return True, "Account registered successfully.", record
        return False, "Database Write Error.", None

    def deposit_capital(self, acc_no, pin, amount):
        data = self.load_records()
        user = [item for item in data if item.get("acc_no") == acc_no and str(item.get("pin")) == str(pin)]
        
        if not user:
            return False, "Authentication Failed: Account Number or PIN is incorrect.", None
        if amount is None or amount <= 0:
            return False, "Transaction Error: Please enter a deposit amount greater than PKR 0.", None

        target = user[0]
        target["balance"] += float(amount)
        target.setdefault("history", []).append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": "Deposit",
            "amount": float(amount),
            "balance": target["balance"]
        })
        
        if self.save_records(data):
            return True, "Amount deposited successfully.", target
        return False, "System Error.", None

    def withdraw_capital(self, acc_no, pin, amount):
        data = self.load_records()
        user = [item for item in data if item.get("acc_no") == acc_no and str(item.get("pin")) == str(pin)]
        
        if not user:
            return False, "Authentication Failed: Account Number or PIN is incorrect.", None
        
        target = user[0]
        if amount is None or amount <= 0:
            return False, "Transaction Error: Please enter a valid withdrawal amount.", None
        if amount > target.get("balance", 0.0):
            return False, "Transaction Error: Insufficient balance in account.", None

        target["balance"] -= float(amount)
        target.setdefault("history", []).append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": "Withdrawal",
            "amount": float(amount),
            "balance": target["balance"]
        })

        if self.save_records(data):
            return True, "Amount withdrawn successfully.", target
        return False, "System Error.", None

    def fetch_account(self, acc_no, pin):
        data = self.load_records()
        user = [item for item in data if item.get("acc_no") == acc_no and str(item.get("pin")) == str(pin)]
        if not user:
            return False, "Authentication Failed: Account not found.", None
        return True, "Account details fetched.", user[0]

    def update_account(self, acc_no, pin, new_name, new_email, new_pin):
        data = self.load_records()
        user = [item for item in data if item.get("acc_no") == acc_no and str(item.get("pin")) == str(pin)]
        if not user:
            return False, "Authentication Failed: Record not found.", None

        target = user[0]
        if new_name.strip(): 
            target["name"] = new_name.strip()
        if new_email.strip(): 
            target["email"] = new_email.strip()
        if new_pin.strip() and len(new_pin.strip()) == 4 and new_pin.strip().isdigit():
            target["pin"] = int(new_pin.strip())

        if self.save_records(data):
            return True, "Details updated successfully.", target
        return False, "System Error.", None

    def delete_account(self, acc_no, pin, confirmation):
        if not confirmation:
            return False, "Authorization Warning: Please check the confirmation checkbox.", None

        data = self.load_records()
        user = [item for item in data if item.get("acc_no") == acc_no and str(item.get("pin")) == str(pin)]
        if not user:
            return False, "Authentication Failed: Record not found.", None

        data.remove(user[0])
        if self.save_records(data):
            return True, "Account deleted successfully.", None
        return False, "System Error.", None

engine = BankEngine()

# ============================================================
# SIDEBAR NAVIGATION
# ============================================================
with st.sidebar:
    st.markdown('<div class="brand-title">🏦 APEX BANKING</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-subtitle">Core Financial Network</div>', unsafe_allow_html=True)
    
    menu = st.radio(
        "Navigation Menu",
        [
            "📊 Dashboard Overview",
            "Create Account",
            "Deposit Money",
            "Withdraw Money",
            "Account Lookup & Ledger",
            "Update Details",
            "Delete Account"
        ],
        label_visibility="collapsed"
    )
    
    records = engine.load_records()
    st.markdown("---")
    st.markdown(f"""
    <div style="font-size: 0.8rem; color: #64748B; line-height: 1.8;">
        System Status: <strong style="color: #10B981;">ONLINE</strong><br>
        Active Accounts: <strong style="color: #F8FAFC;">{len(records)}</strong><br>
        Currency: <strong style="color: #38BDF8;">PKR</strong>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# MAIN APPLICATION INTERFACE
# ============================================================

# ------------------------------------------------------------
# 1. DASHBOARD OVERVIEW
# ------------------------------------------------------------
if menu == "📊 Dashboard Overview":
    st.title("System Dashboard Overview")
    
    records = engine.load_records()
    total_accounts = len(records)
    total_liquidity = sum(item.get("balance", 0.0) for item in records)
    average_balance = (total_liquidity / total_accounts) if total_accounts > 0 else 0.0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Active Accounts</div>
            <div class="kpi-value">{total_accounts}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Holdings Liquidity</div>
            <div class="kpi-value kpi-value-green">PKR {total_liquidity:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Average Account Balance</div>
            <div class="kpi-value kpi-value-blue">PKR {average_balance:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    if total_accounts > 0:
        df = pd.DataFrame(records)
        if "acc_type" not in df.columns:
            df["acc_type"] = "Standard Account"

        chart_col1, chart_col2 = st.columns([1.6, 1])
        with chart_col1:
            st.markdown("##### Balance Distribution across Accounts")
            fig_bar = px.bar(
                df, x="name", y="balance", color="acc_type",
                labels={"name": "Account Holder", "balance": "Holdings (PKR)", "acc_type": "Tier"},
                template="plotly_dark",
                color_discrete_sequence=["#0284C7", "#38BDF8", "#818CF8"]
            )
            fig_bar.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter", color="#94A3B8"), margin=dict(l=10, r=10, t=10, b=10)
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        with chart_col2:
            st.markdown("##### Portfolio Tier Breakdown")
            fig_pie = px.pie(
                df, names="acc_type", values="balance", hole=0.45,
                template="plotly_dark", color_discrete_sequence=["#0284C7", "#38BDF8", "#818CF8"]
            )
            fig_pie.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter", color="#94A3B8"), margin=dict(l=10, r=10, t=10, b=10)
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("##### Central Accounts Registry")
        display_cols = [col for col in ["acc_no", "name", "acc_type", "email", "balance", "created_at"] if col in df.columns]
        st.dataframe(df[display_cols], use_container_width=True, hide_index=True)
    else:
        st.info("System database contains no accounts. Go to 'Create Account' to register one.")

# ------------------------------------------------------------
# 2. CREATE ACCOUNT
# ------------------------------------------------------------
elif menu == "Create Account":
    st.title("Create New Account")
    
    with st.form("register_form_clean"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name", placeholder="Enter full legal name", key="ca_name")
            age = st.number_input("Age", min_value=18, max_value=100, value=None, placeholder="Enter age (18+)", key="ca_age")
        with col2:
            email = st.text_input("Email Address", placeholder="e.g. user@domain.com", key="ca_email")
            pin = st.text_input("4-Digit Security PIN", max_chars=4, type="password", placeholder="Enter 4-digit PIN", key="ca_pin")

        acc_type = st.selectbox("Account Tier", ["Current Account", "Savings Account", "Corporate Account"], key="ca_type")
        submitted = st.form_submit_button("Create Account")

    if submitted:
        success, message, data = engine.create_account(name, age, email, pin, acc_type)
        if success:
            st.markdown(f"""
            <div class="account-card">
                <div style="font-size:0.85rem; color:#10B981; font-weight:700; text-align:center;">✅ ACCOUNT CREATED SUCCESSFULLY</div>
                <div style="font-size:0.8rem; color:#EF4444; font-weight:600; text-align:center; margin-top:6px;">📌 PLEASE NOTE DOWN YOUR ACCOUNT NUMBER SECURELY</div>
                <div class="card-id">{data['acc_no']}</div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-top:15px; font-size:0.9rem; border-top:1px solid #1F2937; padding-top:12px;">
                    <div><strong>Holder Name:</strong> {data['name']}</div>
                    <div><strong>Tier:</strong> {data['acc_type']}</div>
                    <div><strong>Opening Balance:</strong> <span style="color:#10B981; font-weight:700;">PKR 0.00</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error(message)

# ------------------------------------------------------------
# 3. DEPOSIT MONEY
# ------------------------------------------------------------
elif menu == "Deposit Money":
    st.title("Deposit Money")
    
    with st.form("deposit_form_clean"):
        col1, col2 = st.columns(2)
        with col1:
            acc_no = st.text_input("Account Number", placeholder="Enter account number", key="dep_acc")
        with col2:
            pin = st.text_input("Security PIN", max_chars=4, type="password", placeholder="Enter PIN", key="dep_pin")
        
        amount = st.number_input("Deposit Amount (PKR)", min_value=1.0, step=500.0, value=None, placeholder="Enter amount to deposit", key="dep_amt")
        submitted = st.form_submit_button("Deposit Amount")

    if submitted:
        success, message, data = engine.deposit_capital(acc_no, pin, amount)
        if success:
            st.markdown(f"""
            <div class="success-banner">
                <div style="font-size:0.85rem; color:#A7F3D0; font-weight:600;">TRANSACTION COMPLETED</div>
                <div style="font-size:1.1rem; color:#FFFFFF; font-weight:700; margin:4px 0;">Deposit of PKR {amount:,.2f} Successful</div>
                <div style="font-size:1.25rem; color:#10B981; font-weight:700; margin-top:8px;">Updated Account Balance: PKR {data['balance']:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error(message)

# ------------------------------------------------------------
# 4. WITHDRAW MONEY
# ------------------------------------------------------------
elif menu == "Withdraw Money":
    st.title("Withdraw Money")
    
    with st.form("withdraw_form_clean"):
        col1, col2 = st.columns(2)
        with col1:
            acc_no = st.text_input("Account Number", placeholder="Enter account number", key="wd_acc")
        with col2:
            pin = st.text_input("Security PIN", max_chars=4, type="password", placeholder="Enter PIN", key="wd_pin")
        
        amount = st.number_input("Withdrawal Amount (PKR)", min_value=1.0, step=500.0, value=None, placeholder="Enter amount to withdraw", key="wd_amt")
        submitted = st.form_submit_button("Withdraw Amount")

    if submitted:
        success, message, data = engine.withdraw_capital(acc_no, pin, amount)
        if success:
            st.markdown(f"""
            <div class="success-banner">
                <div style="font-size:0.85rem; color:#A7F3D0; font-weight:600;">TRANSACTION COMPLETED</div>
                <div style="font-size:1.1rem; color:#FFFFFF; font-weight:700; margin:4px 0;">Withdrawal of PKR {amount:,.2f} Successful</div>
                <div style="font-size:1.25rem; color:#38BDF8; font-weight:700; margin-top:8px;">Remaining Account Balance: PKR {data['balance']:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error(message)

# ------------------------------------------------------------
# 5. ACCOUNT LOOKUP & LEDGER
# ------------------------------------------------------------
elif menu == "Account Lookup & Ledger":
    st.title("Show Account Details")
    
    with st.form("search_form_clean"):
        col1, col2 = st.columns(2)
        with col1:
            acc_no = st.text_input("Account Number", placeholder="Enter account number", key="sh_acc")
        with col2:
            pin = st.text_input("Security PIN", max_chars=4, type="password", placeholder="Enter PIN", key="sh_pin")
        submitted = st.form_submit_button("Fetch Details")

    if submitted:
        success, message, data = engine.fetch_account(acc_no, pin)
        if success:
            st.success("Record fetched successfully.")
            col1, col2, col3 = st.columns(3)
            col1.metric("Account Holder", data["name"])
            col2.metric("Email Address", data["email"])
            col3.metric("Current Balance", f"PKR {data['balance']:,.2f}")

            st.markdown("##### Account Transaction History")
            history = data.get("history", [])
            if history:
                st.dataframe(pd.DataFrame(history), use_container_width=True, hide_index=True)
            else:
                st.info("No recorded transactions present for this account.")
        else:
            st.error(message)

# ------------------------------------------------------------
# 6. UPDATE DETAILS
# ------------------------------------------------------------
elif menu == "Update Details":
    st.title("Update Account Details")
    
    with st.form("update_form_clean"):
        col1, col2 = st.columns(2)
        with col1:
            acc_no = st.text_input("Account Number", placeholder="Enter account number", key="up_acc")
        with col2:
            pin = st.text_input("Current Security PIN", max_chars=4, type="password", placeholder="Enter PIN", key="up_pin")

        st.markdown("---")
        st.markdown("##### New Details (Leave empty to skip)")
        new_name = st.text_input("New Name", placeholder="Leave blank to keep existing name", key="up_name")
        new_email = st.text_input("New Email", placeholder="Leave blank to keep existing email", key="up_email")
        new_pin = st.text_input("New PIN (4-Digits)", max_chars=4, type="password", placeholder="Leave blank to keep existing PIN", key="up_npin")

        submitted = st.form_submit_button("Update Details")

    if submitted:
        success, message, data = engine.update_account(acc_no, pin, new_name, new_email, new_pin)
        if success:
            st.success(message)
        else:
            st.error(message)

# ------------------------------------------------------------
# 7. DELETE ACCOUNT
# ------------------------------------------------------------
elif menu == "Delete Account":
    st.title("Delete Account")
    
    with st.form("delete_form_clean"):
        col1, col2 = st.columns(2)
        with col1:
            acc_no = st.text_input("Account Number", placeholder="Enter account number", key="del_acc")
        with col2:
            pin = st.text_input("Security PIN", max_chars=4, type="password", placeholder="Enter PIN", key="del_pin")
        
        confirmation = st.checkbox("Confirm permanent deletion of this bank account.")
        submitted = st.form_submit_button("Delete Account")

    if submitted:
        success, message, _ = engine.delete_account(acc_no, pin, confirmation)
        if success:
            st.success(message)
        else:
            st.error(message)
