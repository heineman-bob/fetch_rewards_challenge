"""
For speed sake I opted to focus on end to end testing leveraging the Test Client
packaged with FastAPI because in the end fulfilling the obligitory contract of the
api is the most important thing to test for.  In a real project I would have a combination
of unit testing for the model and behavior testing / integration testing as well.
"""
from fastapi.testclient import TestClient
from fastapi import status
from app.main import app, data_store
from app.models import TransactionsStore
import pytest
from datetime import datetime, timedelta, timezone
import json


class TestTransactions:
    def teardown_method(function):
        data_store.transactions.clear()

    @pytest.fixture
    def client(self):
        return TestClient(app)

    @pytest.fixture
    def create_spend_points_payload(self):
        def _create_spend_points_payload(points):
            return {"points": points}

        return _create_spend_points_payload

    @pytest.fixture
    def provided_test_transactions(self):
        return [
            {"payer": "DANNON", "points": 1000, "timestamp": "2020-11-02T14:00:00Z"},
            {"payer": "UNILEVER", "points": 200, "timestamp": "2020-10-31T11:00:00Z"},
            {"payer": "DANNON", "points": -200, "timestamp": "2020-10-31T15:00:00Z"},
            {
                "payer": "MILLER COORS",
                "points": 10000,
                "timestamp": "2020-11-01T14:00:00Z",
            },
            {"payer": "DANNON", "points": 300, "timestamp": "2020-10-31T10:00:00Z"},
        ]

    def post_transactions(self, client, transactions):
        """Helper method to apply transactions"""
        for transaction in transactions:
            response = client.post("/transactions", json=transaction)

    def test_add_get_transactions(self, client, provided_test_transactions):
        for transaction in provided_test_transactions:
            response = client.post("/transactions", json=transaction)
            assert response.status_code == 200
        response = client.get("/transactions")
        assert len(response.json()) == 5

    def test_add_bad_point_type_transaction(self, client):
        """This just shows a flex of the type validation pydantic offers with model typing"""
        response = client.post(
            "transactions", json={"payer": "payer", "points": "TESTING"}
        )
        assert response.status_code == 422
        assert "points" in str(response.json())

    def test_get_balances(self, client, provided_test_transactions):
        self.post_transactions(client, provided_test_transactions)
        response = client.get("/points/balances")
        assert response.json()["DANNON"] == 1100
        assert response.json()["UNILEVER"] == 200
        assert response.json()["MILLER COORS"] == 10000

    def test_spend_points_and_balances(
        self, client, provided_test_transactions, create_spend_points_payload
    ):
        self.post_transactions(client, provided_test_transactions)

        response = client.post("/points/spend", json=create_spend_points_payload(5000))
        assert response.status_code == 200
        assert len(response.json()) == 3
        response = response.json()
        assert response["DANNON"] == -100
        assert response["UNILEVER"] == -200
        assert response["MILLER COORS"] == -4700

        response = client.get("/points/balances")
        assert response.status_code == 200
        assert len(response.json()) == 3
        response = response.json()
        assert response["DANNON"] == 1000
        assert response["UNILEVER"] == 0
        assert response["MILLER COORS"] == 5300

    def test_spend_too_many_points(
        self, client, provided_test_transactions, create_spend_points_payload
    ):
        self.post_transactions(client, provided_test_transactions)

        response = client.post("/points/spend", json=create_spend_points_payload(40000))
        assert response.status_code == 422
        assert "Not enough" in str(response.json())

    def test_spend_zero_points(
        self, client, provided_test_transactions, create_spend_points_payload
    ):
        self.post_transactions(client, provided_test_transactions)
        before_balance = client.get("/points/balances").json()
        response = client.post("/points/spend", json=create_spend_points_payload(0))
        after_balance = client.get("/points/balances").json()
        assert before_balance == after_balance
