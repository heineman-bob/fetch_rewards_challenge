from pydantic import BaseModel
from datetime import datetime, timezone
import bisect
import logging


logger = logging.getLogger(__name__)

class Transaction(BaseModel):
    """Represents a single transaction schema
    """    
    payer: str 
    points: int
    timestamp: datetime
    remaining_points: int = 0

class Points(BaseModel):
    """Represents an amount of points"""
    points: int


class TransactionsStore():
    """Memory store management and logic
    """
    # transactions = []

    def __init__(self):
        self.transactions = []

    def add_transaction(self, transaction: Transaction):    
        transaction.remaining_points = transaction.points
        bisect.insort(self.transactions, transaction, key=lambda d: d.timestamp)
        return self.transactions

    def get_remaining_point_transactions(self, payer:str=None, timestamp=None):
        transactions = [
            x for x in self.transactions if x.remaining_points > 0 and x.points != 0
        ]

        if payer:
            transactions = [x for x in transactions if x.payer == payer]
         
        if timestamp:
            transactions = [x for x in transactions if x.timestamp <= timestamp]

        return transactions

    def get_total_balance(self):
        return sum([x.remaining_points for x in self.transactions])

    def get_balance_summary(self):
        balance_summary = {}
        for transaction in self.transactions:
            if transaction.payer in balance_summary:
                balance_summary[transaction.payer] += transaction.remaining_points
            else:
                balance_summary[transaction.payer] = transaction.remaining_points
        return balance_summary

    def deduct_points(self, points_to_deduct: int, payer:str=None, timestamp=None):
        payer_summary = {} 
        deduct_transactions = []       
        
        def _create_deduct_transaction(payer:str, points:int) -> Transaction:
            created_at = datetime.utcnow().replace(tzinfo=timezone.utc, microsecond=0).isoformat()
            return Transaction(payer=payer, points=-points, timestamp=created_at, reamining_points=0)
        
        for transaction in self.get_remaining_point_transactions(payer=payer, timestamp=timestamp):
            if points_to_deduct > 0:
                if points_to_deduct > transaction.remaining_points:
                    # Deduct all of the transactions remaining points
                    points_to_deduct -= transaction.remaining_points
                    payer_summary[transaction.payer] = payer_summary.get(transaction.payer, 0) - transaction.remaining_points
                    deduct_transactions.append(_create_deduct_transaction(transaction.payer, transaction.remaining_points))                
                    transaction.remaining_points = 0  
                else:
                    # Deduct the remaining points from this transaction
                    transaction.remaining_points -= points_to_deduct  
                    payer_summary[transaction.payer] = payer_summary.get(transaction.payer, 0) - points_to_deduct
                    deduct_transactions.append(_create_deduct_transaction(transaction.payer, points_to_deduct))
                    points_to_deduct = 0
                    break
            else:
                break
        
        if not payer or not timestamp:
            for transaction in deduct_transactions:
                bisect.insort(self.transactions, transaction, key=lambda d: d.timestamp)

        return payer_summary
            
    def process_historic_spend(self):
        historic_spend_transactions = [x for x in self.transactions if x.remaining_points < 0]
        for transaction in historic_spend_transactions:
            self.deduct_points(abs(transaction.remaining_points), payer=transaction.payer, timestamp=transaction.timestamp)
            transaction.remaining_points = 0

    def spend_points(self, points: Points):
        self.process_historic_spend()
        return self.deduct_points(points.points)
        
        