users_db = {
    "manufacturer": {
        "password": "1234",
        "role": "manufacturer",
        "private_key": "0x4f3edf983ac636a65a842ce7c78d9aa706d3b113b37ac6b622c0e0e64211e8d1",
        "address": "0x1CDC1E0504221Ce47e499B7bC212C3F1d18ECbBf",
        "name": "RADIKS Manufacturer"
    },
    "distributor": {
        "password": "1234",
        "role": "distributor",
        "private_key": "0x6c9a409cfb8f8e7096e5cc204e69bdffab6ed7a0ad540b1e7de33d22451dc7e1",
        "address": "0xD2C521d4928bBC80a9bf6E59BE12bE1B02925A1d",
        "name": "GRAND PHARM Distributor"
    },
    "pharmacy": {
        "password": "1234",
        "role": "pharmacy",
        "private_key": "0x8c62b2ff1cbb0653c76b20ae49c4e62d1d99dfd9a13d8fb3b8fcf0fbd8c3f5d6",
        "address": "0x1A0ee922e717C44d8D99F195b1Fe435C8380DD01",
        "name": "DAIMON MED PHARM Pharmacy"
    }
}


def authenticate(username: str, password: str):
    user = users_db.get(username)
    if user and user["password"] == password:
        return user
    return None
