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

    def __init__(self, address: str):
        self.address = address
        self.amount_received = Decimal()
        self.total_num_receives = 0
        self.amount_sent = Decimal()
        self.total_num_sends = 0

    def make_label(self, direction):
        if direction == TransactionDirection.SEND:
            return f"{self.amount_sent}/{self.total_num_sends}"
        elif direction == TransactionDirection.RECEIVE:
            return f"{self.amount_received}/{self.total_num_receives}"

    def process_send(self, mnano_amount):
        self.total_num_sends += 1
        self.amount_sent += mnano_amount

    def process_receive(self, mnano_amount):
        self.total_num_receives += 1
        self.amount_received += mnano_amount
