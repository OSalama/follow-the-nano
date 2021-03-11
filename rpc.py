import nano
from typing import Dict
from random import randint
import logging
from models import RAW_TO_MNANO

NODE_URL = "https://proxy.nanos.cc/proxy/" # Put your node URL in here. Public nodes available at https://publicnodes.somenano.com/


class HistoryRequestor:

    def __init__(self, use_real_rpc=True, transaction_limit=100):
        self.rpc_client = nano.rpc.Client(NODE_URL)
        self.use_real_rpc = use_real_rpc
        self.transaction_limit = transaction_limit

    def get_account_history(self, nano_address: str) -> Dict:
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
        numtx = randint(1, 2)
        transactions = []
        for _ in range(numtx):
            account = f"nano_{randint(1000, 9999)}"
            transactions.append(
                {"type": "send", "account": account, "amount": randint(1, 10) * RAW_TO_MNANO})
        return transactions