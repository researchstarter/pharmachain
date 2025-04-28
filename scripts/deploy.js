const { ethers, artifacts } = require("hardhat");
const fs = require("fs");

async function main() {
    const PharmaSupplyChain = await ethers.getContractFactory("PharmaSupplyChain");

    console.log("Deploying contract...");
    const pharma = await PharmaSupplyChain.deploy();

    const deployedAddress = pharma.target;
    console.log(`PharmaSupplyChain deployed to: ${deployedAddress}`);

    // === Save Deployed Contract Address ===
    const addressContent = {
        address: deployedAddress
    };
    fs.writeFileSync('backend/json/contractAddress.json', JSON.stringify(addressContent, null, 2));
    console.log("Deployed contract address saved to backend/json/contractAddress.json");

    // === Save ABI ===
    const artifact = await artifacts.readArtifact("PharmaSupplyChain");
    fs.writeFileSync('backend/json/PharmaSupplyChainABI.json', JSON.stringify(artifact.abi, null, 2));
    console.log("ABI saved to backend/json/PharmaSupplyChainABI.json");
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error("Error during deployment:", error);
        process.exit(1);
    });
