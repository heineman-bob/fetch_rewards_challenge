from fastapi.testclient import TestClient
from fastapi import status
from app.main import app
from app.models import TransactionsStore
import pytest
from datetime import datetime, timedelta, timezone

class TestTransactions():

    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def provided_test_transactions(self):
        return [
            { "payer": "DANNON", "points": 1000, "timestamp": "2020-11-02T14:00:00Z" },
            { "payer": "UNILEVER", "points": 200, "timestamp": "2020-10-31T11:00:00Z" },
            { "payer": "DANNON", "points": -200, "timestamp": "2020-10-31T15:00:00Z" },
            { "payer": "MILLER COORS", "points": 10000, "timestamp": "2020-11-01T14:00:00Z" },
            { "payer": "DANNON", "points": 300, "timestamp": "2020-10-31T10:00:00Z" }
        ]

    @pytest.fixture
    def create_timestamp(self):
        def _create_timestamp(delta=None):
            timestamp = datetime.utcnow().replace(tzinfo=timezone.utc, microsecond=0).isoformat()
            
            if delta:
                return timestamp + delta
            else:
                return timestamp
        return _create_timestamp

    @pytest.fixture
    def create_transaction_payload(self, create_timestamp):
        def _create_transaction_payload(payer, points, timestamp=create_timestamp()):
            return { "payer": payer, "points": points, "timestamp": timestamp }

        return _create_transaction_payload

    def test_add_transactions(self, client, provided_test_transactions):
        for transaction in provided_test_transactions:
            response = client.post("/transactions", json=transaction)
            assert response.status_code == 200

    def test_get_balances(self, client, create_transaction_payload):
        payload = create_transaction_payload(payer="TEST", points=1000)
        for i in range(2):
            client.post("/transactions", json=payload)
        response = client.get("/balances")
        assert response.json()["TEST"] == 2000
        

    