// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract PharmaSupplyChain {
    struct Batch {
        string medicine_name;
        address manufacturer;
        address distributor;
        address pharmacy;
        uint256 manufacture_date;
        uint256 expiry_date;
        bool distributor_accepted;
        bool pharmacy_accepted;
        string certificate_hash;
    }

    mapping(uint256 => Batch) public batches;
    uint256[] public batchIDs; // Store actual batch IDs

    // NEW: Address to Name mapping
    mapping(address => string) public addressNames;

    // --- Batch Management ---

    function createBatch(
        uint256 batch_id,
        string memory medicine_name,
        uint256 manufacture_date,
        uint256 expiry_date,
        string memory certificate_hash
    ) public {
        require(batch_id > 0, "Batch ID must be greater than zero");
        require(bytes(medicine_name).length > 0, "Medicine name is required");
        require(batches[batch_id].manufacturer == address(0), "Batch ID already exists");

        batches[batch_id] = Batch({
            medicine_name: medicine_name,
            manufacturer: msg.sender,
            distributor: address(0),
            pharmacy: address(0),
            manufacture_date: manufacture_date,
            expiry_date: expiry_date,
            distributor_accepted: false,
            pharmacy_accepted: false,
            certificate_hash: certificate_hash
        });

        batchIDs.push(batch_id);
    }

    function getAllBatchIDs() public view returns (uint256[] memory) {
        return batchIDs;
    }

    function getBatchInfo(uint256 batch_id) public view returns (
        string memory medicine_name,
        address manufacturer,
        address distributor,
        address pharmacy,
        uint256 manufacture_date,
        uint256 expiry_date,
        bool distributor_accepted,
        bool pharmacy_accepted,
        string memory certificate_hash
    ) {
        Batch storage batch = batches[batch_id];
        return (
            batch.medicine_name,
            batch.manufacturer,
            batch.distributor,
            batch.pharmacy,
            batch.manufacture_date,
            batch.expiry_date,
            batch.distributor_accepted,
            batch.pharmacy_accepted,
            batch.certificate_hash
        );
    }

    function acceptBatchAsDistributor(uint256 batch_id) public {
        Batch storage batch = batches[batch_id];
        require(batch.manufacturer != address(0), "Batch does not exist");
        require(batch.distributor == address(0), "Batch already accepted by distributor");

        batch.distributor = msg.sender;
        batch.distributor_accepted = true;
    }

    function requestTransferToPharmacy(uint256 batch_id, address pharmacy_address) public {
        Batch storage batch = batches[batch_id];
        require(batch.distributor == msg.sender, "You are not the distributor");
        require(batch.pharmacy == address(0), "Batch already transferred");

        batch.pharmacy = pharmacy_address;
    }

    function acceptTransferAtPharmacy(uint256 batch_id) public {
        Batch storage batch = batches[batch_id];
        require(batch.pharmacy == msg.sender, "You are not the pharmacy");

        batch.pharmacy_accepted = true;
    }

    // --- New Functions for Address Name Management ---

    // Admin function: Register name for an address
    function registerAddressName(address _addr, string memory _name) public {
        require(_addr != address(0), "Invalid address");
        addressNames[_addr] = _name;
    }

    // View function: Get name by address
    function getNameByAddress(address _addr) public view returns (string memory) {
        return addressNames[_addr];
    }

}
