import nano
from typing import Dict, Optional
from random import randint, choice
import logging
from models import RAW_TO_MNANO, TransactionDirection

NODE_URL = "https://proxy.nanos.cc/proxy/" # Put your node URL in here. Public nodes available at https://publicnodes.somenano.com/

MAX_CALLS_PER_GRAPH = 100
class HistoryRequestor:

    def __init__(self, use_real_rpc=True, transaction_limit=100):
        self.rpc_client = nano.rpc.Client(NODE_URL)
        self.use_real_rpc = use_real_rpc
        self.transaction_limit = transaction_limit
        self.call_counter = 0

    def get_account_history(self, nano_address: str) -> Optional[Dict]:
        if self.call_counter >= MAX_CALLS_PER_GRAPH:
            logging.error("Reached max calls per graph")
            raise ValueError("Graph reached max call limit")
        self.call_counter += 1
        if self.use_real_rpc:
            return self.rpc_account_history(nano_address)
        else:
            return self.random_history(nano_address)

    def rpc_account_history(self, nano_address: str) -> Dict:
        logging.info("Requesting account history for %s", nano_address)
        response = self.rpc_client.account_history(
            account=nano_address, count=self.transaction_limit)
        return response

    @staticmethod
    def random_history(nano_address: str) -> Dict:
        logging.info("Faking account history for %s", nano_address)
        numtx = randint(1, 5)
        transactions = []
        for _ in range(numtx):
            transactions.append(
                {"type": choice(list(TransactionDirection)).value,
                "account": f"nano_{randint(1000, 9999)}",
                "amount": randint(1, 10) * RAW_TO_MNANO})
        return transactions
