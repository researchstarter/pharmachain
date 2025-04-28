
# 📈 PharmaChain - Blockchain-based Medicine Tracking

A blockchain-based pharma supply chain tracking system. Built using:

- **Solidity** (Smart Contract)
- **Hardhat** (Development environment)
- **FastAPI** (Backend server)
- **Telegram Bot** (Frontend interaction)
- **Streamlit** (Web UI)

---

# 📅 Project Structure

```
/pharma-supplychain
|-- backend/           # FastAPI server
|-- telegram_bot/      # Telegram Bot app
|-- frontend/          # Streamlit UI (ui.py)
|-- contracts/         # Solidity Smart Contract (.sol files)
|-- scripts/           # Deployment scripts
|-- artifacts/         # Hardhat build artifacts
|-- cache/             # Hardhat cache
|-- ignition/          # Hardhat ignition (optional deployments)
|-- test/              # Smart contract tests
|-- node_modules/      # Node.js modules
|-- hardhat.config.js  # Hardhat configuration
|-- package.json       # Node.js project config
|-- config.py          # Custom Python config
|-- README.md          # Project documentation
```

---

# ✨ How to Run Everything

## 1. Install Requirements

Make sure you have installed:

- Node.js (>= v16)
- Python 3.9+
- Ganache or Hardhat Node (for local blockchain)
- Anaconda (recommended for Python)

Install system-level dependencies:

```bash
conda install -c conda-forge pyzbar zbar
```

Install Python dependencies:

```bash
cd backend
pip install -r requirements.txt

cd ../telegram_bot
pip install -r requirements.txt

cd ../frontend
pip install -r requirements.txt
```

Install Node.js dependencies:

```bash
cd contracts
npm install
```

---

## 2. Compile and Deploy Smart Contract

### (A) Start Local Blockchain

```bash
npx hardhat node
```

### (B) Deploy Contract

In a new terminal:

```bash
npx hardhat run scripts/deploy.js --network localhost
```

Deployment saves:

- `contractAddress.json`
- `PharmaSupplyChainABI.json`

into the `backend/json/` folder.

---

## 3. Start FastAPI Backend

```bash
cd backend
uvicorn main:app --reload
```

Server will run at:

```
http://127.0.0.1:8000
```

---

## 4. Start Telegram Bot

```bash
cd telegram_bot
python app.py
```

Make sure you have added your Bot Token inside a `.env` file:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
```

---

## 5. Start Streamlit Frontend

```bash
cd frontend
streamlit run ui.py
```

Available at:

```
http://localhost:8501
```

---

# 🌐 Environment Variables

For FastAPI:

```env
BLOCKCHAIN_RPC_URL=http://127.0.0.1:8545
PRIVATE_KEY=your_wallet_private_key
ACCOUNT_ADDRESS=your_wallet_public_address
CONTRACT_ADDRESS=deployed_contract_address
```

For Telegram Bot:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
```

---

# 📒 Key Commands Summary

| Task                     | Command                                                 |
| ------------------------ | ------------------------------------------------------- |
| Start Blockchain         | `npx hardhat node`                                      |
| Compile Contract         | `npx hardhat compile`                                   |
| Deploy Contract          | `npx hardhat run scripts/deploy.js --network localhost` |
| Run Backend              | `uvicorn main:app --reload`                             |
| Run Telegram Bot         | `python app.py`                                         |
| Run Frontend (Streamlit) | `streamlit run ui.py`                                   |

---

# 📆 After Deployment: Register Address Names

Example Python code:

```python
contract.functions.registerAddressName("0x123...", "Oppo Pharma").transact({"from": admin_address})
contract.functions.registerAddressName("0x456...", "Azamat Distributor").transact({"from": admin_address})
contract.functions.registerAddressName("0x789...", "Shifo Pharmacy").transact({"from": admin_address})
```

---

# 🌟 Features

- Smart Contract for batch tracking
- FastAPI server for blockchain interaction
- Telegram Bot for easy user interface
- Streamlit-based Web UI
- QR code scanning and batch verification

---

# 📽️ Video Tutorial

Watch the full walkthrough here:

[![Watch the video](https://img.youtube.com/vi/b_a03j7Jzs8/maxresdefault.jpg)](https://www.youtube.com/watch?v=b_a03j7Jzs8)

> (Click the image above or [watch on YouTube](https://www.youtube.com/watch?v=b_a03j7Jzs8)).

---

# 🛍️ Contact

Built by RAKUN AI team.
