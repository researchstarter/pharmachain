import json
import os
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

# Connect to blockchain
w3 = Web3(Web3.HTTPProvider(os.getenv("BLOCKCHAIN_RPC_URL")))

PRIVATE_KEY = os.getenv("PRIVATE_KEY")
ACCOUNT_ADDRESS = os.getenv("ACCOUNT_ADDRESS")

# Load contract address
with open('backend/json/contractAddress.json', 'r') as f:
    CONTRACT_ADDRESS = json.load(f)['address']

# Load ABI
with open('backend/json/PharmaSupplyChainABI.json', 'r') as f:
    contract_abi = json.load(f)

# Connect to Contract
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_abi)


def send_transaction_as(function_call, sender_address, sender_private_key):
    nonce = w3.eth.get_transaction_count(sender_address)
    tx = function_call.build_transaction({
        'from': sender_address,
        'nonce': nonce,
        'gas': 3000000,
        'gasPrice': w3.to_wei('5', 'gwei')
    })
    signed_tx = w3.eth.account.sign_transaction(
        tx, private_key=sender_private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_receipt.transactionHash.hex()


def create_batch(batch_id, medicine_name, manufacture_date, expiry_date, certificate_hash):
    fn = contract.functions.createBatch(
        batch_id, medicine_name, manufacture_date, expiry_date, certificate_hash)
    return send_transaction(fn)


def accept_batch_as_distributor(batch_id):
    fn = contract.functions.acceptBatchAsDistributor(batch_id)
    return send_transaction(fn)


def request_transfer_to_pharmacy(batch_id, pharmacy_address):
    fn = contract.functions.requestTransferToPharmacy(
        batch_id, pharmacy_address)
    return send_transaction(fn)


def accept_transfer_at_pharmacy(batch_id):
    fn = contract.functions.acceptTransferAtPharmacy(batch_id)
    return send_transaction(fn)


def get_batch_info(batch_id):
    return contract.functions.getBatchInfo(batch_id).call()
