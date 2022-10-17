from pydantic import BaseModel
from datetime import datetime, timezone
from typing import List, Dict
import bisect


class Transaction(BaseModel):
    """Represents a single transaction schema"""

    payer: str
    points: int
    timestamp: datetime
    remaining_points: int = 0


class Points(BaseModel):
    """Represents an amount of points"""

    points: int


class TransactionsStore:
    """Processes and stores various transactions in memory"""

    def __init__(self):
        """Creates new transaction store"""
        self.transactions = []

    def add_transaction(self, transaction: Transaction) -> List[Transaction]:
        """Inserts a new transaction into a sorted list of transactions

        Args:
            transaction (Transaction): Transaction model instance to add

        Returns:
            List[Transaction]: All transactions stored in memory
        """
        transaction.remaining_points = transaction.points
        bisect.insort(self.transactions, transaction, key=lambda d: d.timestamp)
        return self.transactions

    def get_remaining_point_transactions(
        self, payer: str = None, timestamp: datetime = None
    ) -> List[Transaction]:
        """Gets all transactions with available remaining points

        Args:
            payer (str, optional): Filter for payer field. Defaults to None.
            timestamp (datetime, optional): Filter for timestamp which retrieves
                    all transactions up until this timestamp. Defaults to None.

        Returns:
            List[Transaction]: Transactions with remaining points after filters are applied
        """
        transactions = [
            x for x in self.transactions if x.remaining_points > 0 and x.points != 0
        ]

        if payer:
            transactions = [x for x in transactions if x.payer == payer]

        if timestamp:
            transactions = [x for x in transactions if x.timestamp <= timestamp]

        return transactions

    def get_total_balance(self) -> int:
        """returns the total balance of remaining points

        Returns:
            int: remaining points
        """
        return sum([x.remaining_points for x in self.transactions])

    def get_balance_summary(self) -> Dict:
        """Returns a dictionary of payers and their remaining points

        Returns:
            Dict: Summary of payers and their balances
        """
        balance_summary = {}
        for transaction in self.transactions:
            if transaction.payer in balance_summary:
                balance_summary[transaction.payer] += transaction.remaining_points
            else:
                balance_summary[transaction.payer] = transaction.remaining_points
        return balance_summary

    def deduct_points(
        self, points_to_deduct: int, payer: str = None, timestamp: datetime = None
    ) -> Dict:
        """Process the spend points transaction and update remaining points for historic transactions which have not been applied yet

        Args:
            points_to_deduct (int): how many points to spend
            payer (str, optional): which payer to deduct points for.  This is used to process unapplied spend transactions. Defaults to None.
            timestamp (datetime, optional): filter used to only retreive transactions up until this time. Defaults to None.

        Returns:
            Dict: Summary of payers and how many points were deducted for each
        """
        payer_summary = {}
        deduct_transactions = []

        def _create_deduct_transaction(payer: str, points: int) -> Transaction:
            """Creates a deduct transaction object with the current timestamp to store

            Args:
                payer (str): Payer the points are being deducted from
                points (int): Number of points being deducted

            Returns:
                Transaction: Unsaved transaction instance
            """
            created_at = (
                datetime.utcnow()
                .replace(tzinfo=timezone.utc, microsecond=0)
                .isoformat()
            )
            return Transaction(
                payer=payer, points=-points, timestamp=created_at, reamining_points=0
            )

        for transaction in self.get_remaining_point_transactions(
            payer=payer, timestamp=timestamp
        ):
            if points_to_deduct > 0:
                if points_to_deduct > transaction.remaining_points:
                    # Deduct all of the transactions remaining points
                    points_to_deduct -= transaction.remaining_points
                    payer_summary[transaction.payer] = (
                        payer_summary.get(transaction.payer, 0)
                        - transaction.remaining_points
                    )
                    deduct_transactions.append(
                        _create_deduct_transaction(
                            transaction.payer, transaction.remaining_points
                        )
                    )
                    transaction.remaining_points = 0
                else:
                    # Deduct the remaining points from this transaction
                    transaction.remaining_points -= points_to_deduct
                    payer_summary[transaction.payer] = (
                        payer_summary.get(transaction.payer, 0) - points_to_deduct
                    )
                    deduct_transactions.append(
                        _create_deduct_transaction(transaction.payer, points_to_deduct)
                    )
                    points_to_deduct = 0
                    break
            else:
                break

        # We only insert spend transactions since historic
        # spend transactions already exist in the transaction list
        if not payer or not timestamp:
            for transaction in deduct_transactions:
                bisect.insort(self.transactions, transaction, key=lambda d: d.timestamp)

        return payer_summary

    def process_historic_spend(self) -> None:
        """Since the instructions make it clear we can add transactions out of
        order and with negative amounts before we attempt to spend any points
        we need to process any negative transactions before doing so
        """
        historic_spend_transactions = [
            x for x in self.transactions if x.remaining_points < 0
        ]
        for transaction in historic_spend_transactions:
            self.deduct_points(
                abs(transaction.remaining_points),
                payer=transaction.payer,
                timestamp=transaction.timestamp,
            )
            transaction.remaining_points = 0

    def spend_points(self, points: Points) -> Dict:
        """Spend points and update our transactions remaining points

        Args:
            points (Points): Amount of points to spend

        Returns:
            Dict: Summary of opints spent for each payer
        """
        self.process_historic_spend()
        return self.deduct_points(points.points)
