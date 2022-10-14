from fastapi.testclient import TestClient
from fastapi import status
from app.main import app
from app.models import TransactionsStore

client = TestClient(app)

transactions = [
    { "payer": "DANNON", "points": 1000, "timestamp": "2020-11-02T14:00:00Z" },
    { "payer": "UNILEVER", "points": 200, "timestamp": "2020-10-31T11:00:00Z" },
    { "payer": "DANNON", "points": -200, "timestamp": "2020-10-31T15:00:00Z" },
    { "payer": "MILLER COORS", "points": 10000, "timestamp": "2020-11-01T14:00:00Z" },
    { "payer": "DANNON", "points": 300, "timestamp": "2020-10-31T10:00:00Z" }
]

def test_add_transactions():
    for transaction in transactions:
        response = client.post("/transactions", json=transaction)
        assert response.status_code == 200

def test_add_negative_balance_transaction():
    transaction = { "payer": "AMAZON", "points": -1000, "timestamp": "2020-11-02T14:00:00Z" }
    response = client.post("/transactions", json=transaction)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "-1000" in response.json()['detail']

def test_get_balances():
    response = client.get("/balances")
    print(response.json())
    assert response.json()["DANNON"] == 1100
    assert response.json()["MILLER COORS"] == 10000
    
def test_ts_get_total_balance():
    ts = TransactionsStore()
    ts.balances = {"1": 100, "2": 300}
    assert ts.get_total_balance() == 400

    