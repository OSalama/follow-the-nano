
from decimal import Decimal
from typing import Dict, List, Set
from models import RAW_TO_MNANO, TransactionDirection, TransactionSummary
from rpc import HistoryRequestor
from graph import NanoGraph
import logging



IS_TESTING_MODE = False
NANO_NINJA_BASE_URL = "https://mynano.ninja/api"
ALIASES_ENDPOINT = "accounts/aliases"
API_KEY = ""
SEPARATOR = "-"
IGNORE_LIST = [
    "nano_3jwrszth46rk1mu7rmb4rhm54us8yg1gw3ipodftqtikf5yqdyr7471nsg1k"  # Binance
]


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class FollowTheNano:

    def __init__(self, starting_addresses, traversal_direction, show_all_transactions=False, aliases=None):
        self.traversal_direction = traversal_direction
        self.show_all_transactions = show_all_transactions
        self.all_transactions: Dict[Dict[TransactionSummary]] = {}
        self.explored_nodes = set()
        self.depth_counter = 0
        self.history_requestor = HistoryRequestor(
            use_real_rpc=not IS_TESTING_MODE)
        self.graph = NanoGraph(starting_addresses, aliases)

    def explore(self, addresses_to_explore: Set[str]):
        next_addresses_to_explore = set()
        for address in addresses_to_explore:
            if self.should_skip(address):
                continue
            transaction_history = self.history_requestor.get_account_history(address)
            next_nodes = self.summarise_transactions(address, transaction_history)

            self.explored_nodes.add(address)
            for next_node in next_nodes:
                if next_node not in self.explored_nodes:
                    next_addresses_to_explore.add(next_node)
        self.depth_counter += 1
        return next_addresses_to_explore

    def should_skip(self, address: str) -> bool:
        if address in self.explored_nodes:
            logger.warning("Skipping already explored %s", address)
            return True
        if address in IGNORE_LIST:
            logger.info("Skipping address %s in ignore list", address)
            return True
        return False

    def summarise_transactions(self, address: str, transaction_history: List[Dict]) -> Set[str]:
        next_addresses = set()
        current_transactions = {}
        for transaction in transaction_history:
            raw_amount = transaction["amount"]
            mnano_amount = (Decimal(raw_amount) / RAW_TO_MNANO)
            target_address = transaction["account"]
            if TransactionDirection(transaction["type"]) == self.traversal_direction:
                key = f"{address}{SEPARATOR}{target_address}"
                txn = current_transactions.get(key)
                if not txn:
                    txn = TransactionSummary(address, target_address)
                    current_transactions[key] = txn
                txn.add(mnano_amount)
                next_addresses.add(target_address)
            elif self.show_all_transactions:
                key = f"{target_address}{SEPARATOR}{address}"
                txn = current_transactions.get(key)
                if not txn:
                    txn = TransactionSummary(target_address, address)
                    current_transactions[key] = txn
                txn.add(mnano_amount)
        self.add_transactions_to_master_list(current_transactions)
        return next_addresses

    def add_transactions_to_master_list(self, transactions: Dict[str, TransactionSummary]):
        for key,transaction_summary in transactions.items():
            source = key.split(SEPARATOR)[0]
            target = key.split(SEPARATOR)[1]
            source_txns = self.all_transactions.get(source)
            if source_txns:
                target_txn = source_txns.get(target)
                if target_txn:
                    if target_txn == transaction_summary:
                        logger.debug("Already processed this transaction summary, ignoring")
                    else:
                        # Should this be an exception??
                        logger.error("Detected mismatching transaction summary between %s and %s",
                                      source,
                                      target)
                    continue
            else:
                self.all_transactions[source] = {}
            self.all_transactions[source][target] = transaction_summary
            self.graph.add_transaction(transaction_summary)

    def render_transactions(self):
        self.graph.render_graph()