require("@nomicfoundation/hardhat-toolbox");

module.exports = {
  solidity: {
    version: "0.8.20",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200,
      },
    },
  },
  networks: {
    hardhat: {
      accounts: [
        {
          privateKey: "0x4f3edf983ac636a65a842ce7c78d9aa706d3b113b37ac6b622c0e0e64211e8d1",
          balance: "10000000000000000000000"
        },
        {
          privateKey: "0x6c9a409cfb8f8e7096e5cc204e69bdffab6ed7a0ad540b1e7de33d22451dc7e1",
          balance: "10000000000000000000000"
        },
        {
          privateKey: "0x8c62b2ff1cbb0653c76b20ae49c4e62d1d99dfd9a13d8fb3b8fcf0fbd8c3f5d6",
          balance: "10000000000000000000000"
        }
      ]
    }
  }
};
