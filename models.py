from decimal import Decimal
from enum import Enum

RAW_TO_MNANO = Decimal(10 ** 30)


class TransactionDirection(Enum):
    SEND = "send"
    RECEIVE = "receive"

    def invert(self):
        if self == TransactionDirection.SEND:
            return TransactionDirection.RECEIVE
        else:
            return TransactionDirection.SEND


class TransactionSummary:

    def __init__(self, source_address: str, target_address: str):
        self.source_address = source_address
        self.target_address = target_address
        self.total_amount = Decimal()
        self.total_num_transactions = 0

    def __eq__(self, other: object) -> bool:
        return (
            self.source_address == other.source_address and
            self.target_address == other.target_address and
            self.total_amount == other.total_amount and
            self.total_num_transactions == other.total_num_transactions
        )

    def add(self, mnano_amount):
        self.total_num_transactions += 1
        self.total_amount += mnano_amount
