from fastapi import FastAPI, HTTPException, Body, WebSocket
from backend.users import authenticate
from backend.smart_contract import contract, send_transaction_as
from backend.websocket_manager import manager
from datetime import datetime
from backend.users import users_db

app = FastAPI()


@app.get("/get_batch_info/{batch_id}")
async def get_batch_info(batch_id: int):
    try:
        batch = contract.functions.getBatchInfo(batch_id).call()

        if batch[1] == "0x0000000000000000000000000000000000000000":
            raise HTTPException(status_code=404, detail="Batch not found")

        manufacturer_name = contract.functions.getNameByAddress(
            batch[1]).call()
        distributor_name = contract.functions.getNameByAddress(batch[2]).call()
        pharmacy_name = contract.functions.getNameByAddress(batch[3]).call()

        return {
            "batch_id": batch_id,
            "medicine_name": batch[0],
            "manufacturer_address": batch[1],
            "manufacturer_name": manufacturer_name,
            "distributor_address": batch[2],
            "distributor_name": distributor_name,
            "pharmacy_address": batch[3],
            "pharmacy_name": pharmacy_name,
            "manufacture_date": batch[4],
            "expiry_date": batch[5],
            "distributor_accepted": batch[6],
            "pharmacy_accepted": batch[7],
            "certificate_hash": batch[8],
        }
    except Exception as e:
        print(f"Error fetching batch info: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch batch info: {str(e)}")


@app.get("/get_registered_pharmacies")
def get_registered_pharmacies():
    pharmacies = []
    try:
        for username, user in users_db.items():
            if user["role"] == "pharmacy":
                pharmacies.append({
                    "address": user["address"],
                    "name": user["name"]
                })
        return pharmacies
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch pharmacies: {str(e)}")


@app.post("/setup_register_names")
async def setup_register_names():
    try:
        for username, user in users_db.items():
            address = user["address"]
            name = user["name"]
            private_key = user["private_key"]

            tx = contract.functions.registerAddressName(address, name)
            send_transaction_as(tx, address, private_key)

        return {"message": "All users' names registered successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Setup failed: {str(e)}")

# === Helper Functions ===


def get_all_batches():
    batches = []
    try:
        batch_ids = contract.functions.getAllBatchIDs().call()
        print(f"Retrieved batch IDs: {batch_ids}")  # Debug log

        for batch_id in batch_ids:
            try:
                batch = contract.functions.getBatchInfo(batch_id).call()
                print(f"Batch {batch_id} raw data: {batch}")  # Debug log

                # Skip invalid batches
                if batch[0] == "" or batch[1] == "0x0000000000000000000000000000000000000000":
                    print(f"Skipping batch {batch_id}: Invalid data")
                    continue

                manufacturer_name = contract.functions.getNameByAddress(
                    batch[1]).call()
                distributor_name = contract.functions.getNameByAddress(
                    batch[2]).call()
                pharmacy_name = contract.functions.getNameByAddress(
                    batch[3]).call()

                batch_dict = {
                    "manufacturer": batch[1],
                    "manufacturer_name": manufacturer_name,
                    "distributor": batch[2],
                    "distributor_name": distributor_name,
                    "pharmacy": batch[3],
                    "pharmacy_name": pharmacy_name,
                    "medicine_name": batch[0],
                    "manufacture_date": batch[4],
                    "expiry_date": batch[5],
                    "certificate_hash": batch[8],
                    "distributor_accepted": batch[6],
                    "pharmacy_accepted": batch[7]
                }
                batches.append((batch_id, batch_dict))
            except Exception as e:
                print(f"Error fetching batch {batch_id}: {e}")
    except Exception as e:
        print(f"Error fetching batch IDs: {e}")

    print(f"Returning batches: {batches}")  # Debug log
    return batches


# === API Routes ===


@app.get("/get_batches_by_manufacturer/{address}")
def get_batches_by_manufacturer(address: str):
    all_batches = get_all_batches()
    filtered = [batch for batch in all_batches if batch[1]
                ["manufacturer"].lower() == address.lower()]
    return filtered


@app.get("/get_batches_by_distributor/{address}")
def get_batches_by_distributor(address: str):
    all_batches = get_all_batches()

    filtered = []

    for batch_id, batch in all_batches:
        # CASE 1: Distributor owns it
        if batch["distributor"].lower() == address.lower():
            filtered.append((batch_id, batch))

        # CASE 2: Distributor not assigned yet, and batch is open (not accepted yet)
        elif batch["distributor"] == "0x0000000000000000000000000000000000000000" and not batch["distributor_accepted"]:
            filtered.append((batch_id, batch))

    return filtered


@app.get("/get_batches_by_pharmacy/{address}")
def get_batches_by_pharmacy(address: str):
    all_batches = get_all_batches()
    filtered = [batch for batch in all_batches if batch[1]
                ["pharmacy"].lower() == address.lower()]
    return filtered

# === Authentication Helper ===


def check_auth(username: str, password: str, required_role: str = None):
    user = authenticate(username, password)
    if not user:
        raise HTTPException(
            status_code=401, detail="Invalid username or password")
    if required_role and user["role"] != required_role:
        raise HTTPException(
            status_code=403, detail=f"Only {required_role} can perform this action")
    return user

# === Transaction APIs ===


@app.post("/create_batch")
async def create_batch_api(
    batch_id: int = Body(...),
    medicine_name: str = Body(...),
    manufacture_date: str = Body(...),
    expiry_date: str = Body(...),
    certificate_hash: str = Body(...),
    username: str = Body(...),
    password: str = Body(...)
):
    user = authenticate(username, password)
    if not user or user["role"] != "manufacturer":
        raise HTTPException(
            status_code=403, detail="Unauthorized manufacturer access.")

    # Convert date strings to UNIX timestamps
    manufacture_timestamp = int(datetime.strptime(
        manufacture_date, "%Y-%m-%d").timestamp())
    expiry_timestamp = int(datetime.strptime(
        expiry_date, "%Y-%m-%d").timestamp())

    # Prepare contract function
    fn = contract.functions.createBatch(
        batch_id,
        medicine_name,
        manufacture_timestamp,
        expiry_timestamp,
        certificate_hash
    )

    # Now use user's private key and address dynamically!
    tx_hash = send_transaction_as(fn, user["address"], user["private_key"])

    await manager.broadcast(f"Batch created: {batch_id}")
    return {"tx_hash": tx_hash}


@app.post("/accept_batch_as_distributor")
async def accept_batch_api(
    batch_id: int = Body(...),
    username: str = Body(...),
    password: str = Body(...)
):
    user = check_auth(username, password, required_role="distributor")

    fn = contract.functions.acceptBatchAsDistributor(batch_id)
    tx_hash = send_transaction_as(fn, user["address"], user["private_key"])
    await manager.broadcast(f"Distributor accepted batch: {batch_id}")
    return {"tx_hash": tx_hash}


@app.post("/request_transfer_to_pharmacy")
async def request_transfer_api(
    batch_id: int = Body(...),
    pharmacy_address: str = Body(...),
    username: str = Body(...),
    password: str = Body(...)
):
    user = check_auth(username, password, required_role="distributor")

    fn = contract.functions.requestTransferToPharmacy(
        batch_id, pharmacy_address)
    tx_hash = send_transaction_as(fn, user["address"], user["private_key"])
    await manager.broadcast(f"Transfer requested to pharmacy: {batch_id}")
    return {"tx_hash": tx_hash}


@app.post("/accept_transfer_at_pharmacy")
async def accept_transfer_api(
    batch_id: int = Body(...),
    username: str = Body(...),
    password: str = Body(...)
):
    user = check_auth(username, password, required_role="pharmacy")

    fn = contract.functions.acceptTransferAtPharmacy(batch_id)
    tx_hash = send_transaction_as(fn, user["address"], user["private_key"])
    await manager.broadcast(f"Pharmacy accepted batch: {batch_id}")
    return {"tx_hash": tx_hash}

# === Get a Specific Batch ===


@app.get("/get_batch/{batch_id}")
async def get_batch_api(batch_id: int):
    try:
        batch = contract.functions.getBatchInfo(batch_id).call()
        return {
            "medicine_name": batch[0],
            "manufacturer": batch[1],
            "distributor": batch[2],
            "pharmacy": batch[3],
            "manufacture_date": batch[4],
            "expiry_date": batch[5],
            "distributor_accepted": batch[6],
            "pharmacy_accepted": batch[7],
            "certificate_hash": batch[8]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching batch {batch_id}: {str(e)}")
