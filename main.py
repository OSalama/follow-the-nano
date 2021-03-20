import logging
from graph import NanoGraph
from typing import Dict, List, Set
from collections import defaultdict
from decimal import Decimal
from models import TransactionSummary, TransactionDirection, RAW_TO_MNANO
from rpc import HistoryRequestor
import requests

IS_TESTING_MODE = False
NANO_NINJA_BASE_URL = "https://mynano.ninja/api"
ALIASES_ENDPOINT = "accounts/aliases"
API_KEY = ""
SEPARATOR = "-"

IGNORE_LIST = [
    "nano_3jwrszth46rk1mu7rmb4rhm54us8yg1gw3ipodftqtikf5yqdyr7471nsg1k"  # Binance
]


class FollowTheNano:

    def __init__(self, traversal_direction, show_all_balance_sources=False, aliases=None):
        self.traversal_direction = traversal_direction
        self.show_all_balance_sources = show_all_balance_sources
        self.all_transactions: Dict[Dict[TransactionSummary]] = {}
        self.explored_nodes = set()
        self.depth_counter = 0
        self.history_requestor = HistoryRequestor(
            use_real_rpc=not IS_TESTING_MODE)
        self.aliases = aliases

    def start_exploring(self, starting_addresses: List[str], explore_depth:int=1):
        self.graph = NanoGraph(starting_addresses, self.aliases)
        explore_count = 0
        next_addresses = set(starting_addresses)
        while explore_count < explore_depth:
            next_addresses = self.explore(next_addresses)
            explore_count += 1
        return next_addresses

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
            logging.warning("Skipping already explored %s", address)
            return True
        if address in IGNORE_LIST:
            logging.info("Skipping address %s in ignore list", address)
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
            elif self.show_all_balance_sources:
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
                        logging.debug("Already processed this transaction summary, ignoring")
                    else:
                        # Should this be an exception??
                        logging.error("Detected mismatching transaction summary between %s and %s",
                                      source,
                                      target)
                    continue
            else:
                self.all_transactions[source] = {}
            self.all_transactions[source][target] = transaction_summary
            self.graph.add_transaction(transaction_summary)

    def render_transactions(self):
        self.graph.render_graph()


def main():
    # test with dodgy guy from reddit https://www.reddit.com/r/WeNano/comments/lcp64f/suspected_gps_spoofer/
    starting_addresses = [
        "nano_3qt7yt39jnzq516npbiicqy4oijoez3icpgbfbqxeayfgazyzrnk8qd4bdtf"]  # TODO: Take as input
    """
    Expected eventual flow:

    start a new graph for given set of addresses (app.start_exploring(...))
    option:
        explore a user defined number of times
    render graph so far
    pause for more input, which can either be:
             explore n more times
             start new graph
    """
    aliases = get_aliases()
    app = FollowTheNano(TransactionDirection.SEND, show_all_balance_sources=True, aliases=aliases)
    next_addresses = app.start_exploring(starting_addresses, explore_depth=4)
    app.render_transactions()


def get_aliases():
    endpoint = f"{NANO_NINJA_BASE_URL}/{ALIASES_ENDPOINT}"
    resp = requests.get(endpoint)
    resp_json = resp.json()
    aliases = {alias["account"]:alias["alias"] for alias in resp_json}
    return aliases

if __name__ == "__main__":
    main()
