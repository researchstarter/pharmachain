import requests
import random

batch_id = random.randint(10000, 99999)


BASE_URL = "http://127.0.0.1:8000"

# ⚡ Use real pharmacy blockchain address
pharmacy_address = "0x1A0ee922e717C44d8D99F195b1Fe435C8380DD01"

# --- Helper functions ---


def create_batch():
    payload = {
        "batch_id": batch_id,
        "medicine_name": "Painkiller X",
        "manufacture_date": "2025-04-27",
        "expiry_date": "2027-04-27",
        "certificate_hash": "some_cert_hash_value",
        "username": "manufacturer",
        "password": "1234"
    }
    response = requests.post(f"{BASE_URL}/create_batch", json=payload)
    response.raise_for_status()
    print("✅ Batch created by Manufacturer")


def accept_batch():
    payload = {
        "batch_id": batch_id,
        "username": "distributor",
        "password": "1234"
    }
    response = requests.post(
        f"{BASE_URL}/accept_batch_as_distributor", json=payload)
    response.raise_for_status()
    print("✅ Distributor accepted the batch")


def request_transfer():
    payload = {
        "batch_id": batch_id,
        "pharmacy_address": pharmacy_address,
        "username": "distributor",
        "password": "1234"
    }
    response = requests.post(
        f"{BASE_URL}/request_transfer_to_pharmacy", json=payload)
    response.raise_for_status()
    print("✅ Distributor requested transfer to Pharmacy")


def accept_transfer():
    payload = {
        "batch_id": batch_id,
        "username": "pharmacy",
        "password": "1234"
    }
    response = requests.post(
        f"{BASE_URL}/accept_transfer_at_pharmacy", json=payload)
    response.raise_for_status()
    print("✅ Pharmacy accepted the batch")


def get_batch_info():
    response = requests.get(f"{BASE_URL}/get_batch/{batch_id}")
    response.raise_for_status()
    batch = response.json()
    print("✅ Customer view of batch:")
    print(batch)

# --- Full workflow test ---


def run_workflow():
    print("\n=== 🚀 Starting full Pharma SupplyChain Workflow Test ===\n")
    create_batch()
    accept_batch()
    request_transfer()
    accept_transfer()
    get_batch_info()
    print("\n=== ✅ Full Workflow Completed Successfully ===\n")


if __name__ == "__main__":
    run_workflow()
