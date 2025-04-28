import streamlit as st
import requests
from datetime import datetime
import time
import uuid
import barcode
from barcode.writer import ImageWriter
from io import BytesIO


st.set_page_config(
    page_title="PharmaChain Portal", layout="wide"
)

# === First-time Setup ===
if 'setup_done' not in st.session_state:
    try:
        response = requests.post(
            "http://localhost:8000/setup_register_names", timeout=10)
        if response.status_code == 200:
            st.success("✅ Initial setup complete! Users' names registered.")
        else:
            st.error(f"❌ Setup failed: {response.text}")
    except Exception as e:
        st.error(f"🚫 Could not complete setup: {str(e)}")
    st.session_state.setup_done = True


st.markdown(
    """
    <style>
    #MainMenu, .stAppToolbar { visibility: hidden; }
    footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("💊 PharmaChain - Blockchain-based Medicine Tracking")

# === Auth Session Handling ===
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'address' not in st.session_state:
    st.session_state.address = None

# Demo addresses
user_addresses = {
    "manufacturer": "0x1CDC1E0504221Ce47e499B7bC212C3F1d18ECbBf",
    "distributor": "0xD2C521d4928bBC80a9bf6E59BE12bE1B02925A1d",
    "pharmacy": "0x1A0ee922e717C44d8D99F195b1Fe435C8380DD01"
}

# === Helper Functions ===


def fetch_registered_pharmacies():
    try:
        res = requests.get(
            "http://localhost:8000/get_registered_pharmacies", timeout=5)
        if res.status_code == 200:
            pharmacies = res.json()
            return {pharmacy["name"]: pharmacy["address"] for pharmacy in pharmacies}
        else:
            st.sidebar.error(f"API Error ({res.status_code}): {res.text}")
            return {}
    except Exception as e:
        st.sidebar.error(f"🚫 Error fetching pharmacies: {str(e)}")
        return {}


def fetch_batches():
    username = st.session_state.username
    address = st.session_state.address

    try:
        if username == "manufacturer":
            res = requests.get(
                f"http://localhost:8000/get_batches_by_manufacturer/{address}", timeout=5)
        elif username == "distributor":
            res = requests.get(
                f"http://localhost:8000/get_batches_by_distributor/{address}", timeout=5)
        elif username == "pharmacy":
            res = requests.get(
                f"http://localhost:8000/get_batches_by_pharmacy/{address}", timeout=5)
        else:
            return []

        if res.status_code == 200:
            return res.json()
        else:
            st.sidebar.error(f"API Error ({res.status_code}): {res.text}")
            return []
    except requests.exceptions.ConnectionError:
        st.sidebar.error(
            "❌ Cannot connect to backend server at localhost:8000. Make sure it's running.")
        return []
    except Exception as e:
        st.sidebar.error(f"🚫 Error: {str(e)}")
        return []


registered_pharmacies = fetch_registered_pharmacies()


# === Login Section ===
with st.sidebar:
    if not st.session_state.authenticated:
        st.header("🔐 Login")
        username = st.selectbox(
            "Username", ["manufacturer", "distributor", "pharmacy"])
        password = st.text_input("Password", type="password", value="1234")
        if st.button("🔓 Login"):
            if password == "1234":
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.address = user_addresses[username]
                st.success(f"Login successful as {username.capitalize()}")
                st.rerun()
            else:
                st.error("Incorrect credentials")
    else:
        st.markdown(f"✅ Logged in as: **{st.session_state.username}**")
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.address = None
            st.rerun()


# === Main Interface ===
if st.session_state.authenticated:
    batches = fetch_batches()

    if st.session_state.username == "manufacturer":
        pending_batches = [(bid, b)
                           for bid, b in batches if not b["distributor_accepted"]]
        in_distributor_batches = [
            (bid, b) for bid, b in batches if b["distributor_accepted"] and not b["pharmacy_accepted"]]
        delivered_batches = [(bid, b)
                             for bid, b in batches if b["pharmacy_accepted"]]

        tabs = st.tabs([
            "🏭 Create Batch",
            f"⏳ Pending Batches ({len(pending_batches)})",
            f"🚚 In Distributor ({len(in_distributor_batches)})",
            f"🛬 Delivered Batches ({len(delivered_batches)})"
        ])

        # --- Create Batch ---
        with tabs[0]:
            st.header("🏭 Create a New Medicine Batch")
            with st.form("create_batch_form"):
                medicine_name = st.text_input("Medicine Name")
                manufacture_date = st.date_input(
                    "Manufacture Date", value=datetime.today())
                expiry_date = st.date_input("Expiry Date")
                certificate_hash = st.text_input("Certificate Hash (optional)")
                submit_btn = st.form_submit_button("✅ Create Batch")

                if submit_btn:
                    batch_id = int(uuid.uuid4().int & (1 << 32) - 1)
                    st.info(f"Generated Batch ID: {batch_id}")
                    payload = {
                        "batch_id": batch_id,
                        "medicine_name": medicine_name,
                        "manufacture_date": manufacture_date.strftime("%Y-%m-%d"),
                        "expiry_date": expiry_date.strftime("%Y-%m-%d"),
                        "certificate_hash": certificate_hash or "",
                        "username": "manufacturer",
                        "password": "1234"
                    }
                    with st.spinner("🚀 Creating batch..."):
                        try:
                            response = requests.post(
                                "http://localhost:8000/create_batch", json=payload)
                            if response.status_code == 200:
                                st.success(
                                    f"✅ Batch created successfully! Tx Hash: {response.json()['tx_hash']}")
                                time.sleep(2)
                                st.rerun()
                            else:
                                st.error(f"❌ Failed: {response.text}")
                        except Exception as e:
                            st.error(f"🚫 Exception: {str(e)}")

        # --- Pending Batches ---
        with tabs[1]:
            st.header(f"⏳ Pending Batches ({len(pending_batches)})")
            if pending_batches:
                for batch_id, batch in pending_batches:
                    with st.expander(f"📦 Batch {batch_id} - {batch['medicine_name']}"):
                        st.json(batch)
            else:
                st.info("No pending batches available.")

        # --- In Distributor ---
        with tabs[2]:
            st.header(f"🚚 In Distributor ({len(in_distributor_batches)})")
            if in_distributor_batches:
                for batch_id, batch in in_distributor_batches:
                    with st.expander(f"🚚 Batch {batch_id} - {batch['medicine_name']}"):
                        st.json(batch)
            else:
                st.info("No batches currently in distributor.")

        # --- Delivered Batches ---
        with tabs[3]:
            st.header(f"🛬 Delivered Batches ({len(delivered_batches)})")
            if delivered_batches:
                for batch_id, batch in delivered_batches:
                    with st.expander(f"🛬 Batch {batch_id} - {batch['medicine_name']}"):
                        st.json(batch)
            else:
                st.info("No delivered batches yet.")

    elif st.session_state.username == "distributor":
        incoming_batches = [(bid, b)
                            for bid, b in batches if not b["distributor_accepted"]]
        accepted_batches = [
            (bid, b) for bid, b in batches if b["distributor_accepted"] and b["pharmacy"] == "0x0000000000000000000000000000000000000000"]
        transferred_batches = [
            (bid, b) for bid, b in batches if b["pharmacy"] != "0x0000000000000000000000000000000000000000" and not b["pharmacy_accepted"]]

        tabs = st.tabs([
            f"📥 Incoming Batches ({len(incoming_batches)})",
            f"✅ Accepted Batches ({len(accepted_batches)})",
            f"🚚 Transferred Batches ({len(transferred_batches)})"
        ])

        # --- Incoming Batches ---
        with tabs[0]:
            st.header(f"📥 Incoming Batches ({len(incoming_batches)})")
            if incoming_batches:
                for batch_id, batch in incoming_batches:
                    with st.expander(f"📦 Batch {batch_id} - {batch['medicine_name']}"):
                        st.json(batch)
                        if st.button(f"✅ Accept Batch", key=f"accept_{batch_id}"):
                            payload = {
                                "batch_id": batch_id,
                                "username": "distributor",
                                "password": "1234"
                            }
                            try:
                                response = requests.post(
                                    "http://localhost:8000/accept_batch_as_distributor",
                                    json=payload,
                                    timeout=5
                                )
                                if response.status_code == 200:
                                    st.success(
                                        f"✅ Batch {batch_id} accepted successfully!")
                                    time.sleep(2)
                                    st.rerun()
                                else:
                                    st.error(
                                        f"❌ Failed to accept batch: {response.text}")
                            except Exception as e:
                                st.error(f"🚫 Error: {str(e)}")
            else:
                st.info("No incoming batches to accept.")

        # --- Accepted Batches ---
        with tabs[1]:
            st.header(f"✅ Accepted Batches ({len(accepted_batches)})")
            if accepted_batches:
                for batch_id, batch in accepted_batches:
                    with st.expander(f"✅ Batch {batch_id} - {batch['medicine_name']}"):
                        st.subheader("📋 Batch Details")
                        st.json(batch)

                        selected_pharmacy_name = st.selectbox(
                            f"🏥 Select Pharmacy for Batch {batch_id}",
                            list(registered_pharmacies.keys()),
                            key=f"pharmacy_select_{batch_id}"
                        )
                        selected_pharmacy_address = registered_pharmacies[selected_pharmacy_name]

                        if st.button(f"🚚 Request Transfer to {selected_pharmacy_name} for Batch {batch_id}", key=f"transfer_{batch_id}"):
                            payload = {
                                "batch_id": batch_id,
                                "pharmacy_address": selected_pharmacy_address,
                                "username": "distributor",
                                "password": "1234"
                            }
                            try:
                                response = requests.post(
                                    "http://localhost:8000/request_transfer_to_pharmacy",
                                    json=payload,
                                    timeout=5
                                )
                                if response.status_code == 200:
                                    st.success(
                                        f"🚚 Transfer request for Batch {batch_id} sent to {selected_pharmacy_name}!")
                                    time.sleep(2)
                                    st.rerun()
                                else:
                                    st.error(
                                        f"❌ Failed to request transfer: {response.text}")
                            except Exception as e:
                                st.error(f"🚫 Error: {str(e)}")
            else:
                st.info("No accepted batches ready to transfer.")

        # --- Transferred Batches ---
        with tabs[2]:
            st.header(f"🚚 Transferred Batches ({len(transferred_batches)})")
            if transferred_batches:
                for batch_id, batch in transferred_batches:
                    status_tag = "🟢 Accepted by Pharmacy" if batch[
                        "pharmacy_accepted"] else "🔴 Pending Acceptance"
                    with st.expander(f"🚚 Batch {batch_id} - {batch['medicine_name']} [{status_tag}]"):
                        st.subheader("📋 Batch Details")
                        st.json(batch)
            else:
                st.info("No transferred batches yet.")

    elif st.session_state.username == "pharmacy":
        incoming_batches = [(bid, b)
                            for bid, b in batches if not b["pharmacy_accepted"]]
        accepted_batches = [(bid, b)
                            for bid, b in batches if b["pharmacy_accepted"]]

        tabs = st.tabs([
            f"📥 Incoming Batches ({len(incoming_batches)})",
            f"✅ Accepted Batches ({len(accepted_batches)})"
        ])

        # --- Incoming Batches ---
        with tabs[0]:
            st.header(f"📥 Incoming Batches ({len(incoming_batches)})")
            if incoming_batches:
                for batch_id, batch in incoming_batches:
                    with st.expander(f"📦 Batch {batch_id} - {batch['medicine_name']}"):
                        st.subheader("📋 Batch Details")
                        st.json(batch)

                        if st.button(f"✅ Accept Batch", key=f"accept_pharmacy_{batch_id}"):
                            payload = {
                                "batch_id": batch_id,
                                "username": "pharmacy",
                                "password": "1234"
                            }
                            try:
                                response = requests.post(
                                    "http://localhost:8000/accept_transfer_at_pharmacy",
                                    json=payload,
                                    timeout=5
                                )
                                if response.status_code == 200:
                                    st.success(
                                        f"✅ Batch {batch_id} accepted at pharmacy!")
                                    time.sleep(2)
                                    st.rerun()
                                else:
                                    st.error(
                                        f"❌ Failed to accept batch: {response.text}")
                            except Exception as e:
                                st.error(f"🚫 Error: {str(e)}")
            else:
                st.info("No incoming batches to accept.")

        # --- Accepted Batches ---
        with tabs[1]:
            st.header(f"✅ Accepted Batches ({len(accepted_batches)})")
            if accepted_batches:
                for batch_id, batch in accepted_batches:
                    with st.expander(f"✅ Batch {batch_id} - {batch['medicine_name']}"):
                        st.subheader("📋 Batch Details")
                        st.json(batch)

                        # Show loading spinner while generating barcode
                        with st.spinner("🔄 Generating barcode..."):
                            # optional tiny delay to show animation smoothly
                            time.sleep(0.5)
                            barcode_buffer = BytesIO()
                            # Ensure 12 digits for EAN-13
                            ean_code = str(batch_id).zfill(12)

                            # Generate EAN-13
                            ean = barcode.get(
                                'ean13', ean_code, writer=ImageWriter())
                            ean.write(barcode_buffer)

                            st.image(barcode_buffer.getvalue(
                            ), caption=f"📦 Batch ID: {batch_id} Barcode (EAN-13)", width=250)

            else:
                st.info("No accepted batches yet.")

    else:
        st.info("🔄 Unkown user!")
