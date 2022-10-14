from typing import Union
from fastapi import FastAPI, Response, status, HTTPException
from datetime import datetime
from app.models import Points, Transaction, TransactionsStore

description = '''This web service accepts HTTP requests and returns json responses. 
It follows the logic provided in the directions PDF located in the root of this repository. 

### Endpoints Implemented:

* add transactions
* spend points
* point balance
'''

app = FastAPI(
    title="Fetch Rewards Coding Exercise - BSE",
    description=description,
    version="0.0.1",
    contact={
        "name": "Robert Heineman",
        "email": "heineman.bob@gmail.com"
    },
    docs_url="/", redoc_url="/docs",
)

# Using in memory data stores
data_store = TransactionsStore()

@app.post("/transactions", tags=["Transactions"])
def create_transaction(transaction: Transaction, response: Response):
    """Add transactions for a specific payer and date.
    """
    try:
        created_transaction = data_store.add_transaction(transaction)
        return created_transaction
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))  


@app.post("/transactions/spend", tags=["Transactions"])
def spend_points(points: Points):
    """Spend points using the rules outlined and return a list deduction transactions
    """
    if points.points > data_store.get_total_balance():
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                detail="Not enough available points")
    
    return data_store.spend_points(points)


@app.get("/transactions", tags=["Transactions"])
def get_transactions():
    """List all transactions

    Notes:
         I included this for transparency into how spend transactions are recorded
    """
    return data_store.transactions


@app.get("/balances", tags=["Accounts"])
def get_balances():
    """Return all payer point balances.
    """
    return data_store.get_balance_summary()