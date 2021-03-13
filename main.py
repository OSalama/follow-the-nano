import logging
from graph import NanoGraph
from typing import Dict, List, Set
from collections import defaultdict
from decimal import Decimal
from models import TransactionSummary, TransactionDirection, RAW_TO_MNANO
from rpc import HistoryRequestor

MAX_DEPTH = 4  # TODO: Input

API_KEY = ""

IGNORE_LIST = [
    "nano_3jwrszth46rk1mu7rmb4rhm54us8yg1gw3ipodftqtikf5yqdyr7471nsg1k"  # Binance
]  # Possible TODO: hook into mynano.ninja for aliases


class FollowTheNano:

    def __init__(self, starting_addresses, traversal_direction, show_all_balance_sources=False):
        self.starting_addresses = starting_addresses
        self.traversal_direction = traversal_direction
        self.show_all_balance_sources = show_all_balance_sources
        self.all_transactions: Dict[Dict[TransactionSummary]] = {}
        self.explored_nodes = set()
        self.graph = NanoGraph(starting_addresses)
        self.depth_counter = 0
        self.history_requestor = HistoryRequestor(
            use_real_rpc=True)  # TODO: Input

    def start_exploring(self):
        return self.explore(set(self.starting_addresses))

    def explore(self, addresses_to_explore: Set[str]):
        if self.depth_counter >= MAX_DEPTH:
            logging.error("Reached max depth, no longer exploring")
            return
        next_addresses_to_explore = set()
        for address in addresses_to_explore:
            if address in self.explored_nodes:
                logging.warning("Skipping already explored")
                continue
            if address in IGNORE_LIST:
                logging.info("Skipping address %s in ignore list", address)
                continue
            transaction_history = self.history_requestor.get_account_history(address)
            next_nodes = self.summarise_transactions(address, transaction_history)

            self.explored_nodes.add(address)
            for next_node in next_nodes:
                if next_node not in self.explored_nodes:
                    next_addresses_to_explore.add(next_node)
        self.depth_counter += 1
        return next_addresses_to_explore

    def summarise_transactions(self, address: str, transaction_history: Dict) -> Dict[str, TransactionSummary]:
        next_nodes = set()
        node_transactions = {}
        for transaction in transaction_history:
            raw_amount = transaction["amount"]
            mnano_amount = (Decimal(raw_amount) / RAW_TO_MNANO)
            target_address = transaction["account"]
            if TransactionDirection(transaction["type"]) == self.traversal_direction:
                key = f"{address}-{target_address}"
                txn = node_transactions.get(key)
                if not txn:
                    txn = TransactionSummary(address, target_address)
                    node_transactions[key] = txn
                txn.add(mnano_amount)
                next_nodes.add(target_address)
            elif self.show_all_balance_sources:
                key = f"{target_address}-{address}"
                txn = node_transactions.get(key)
                if not txn:
                    txn = TransactionSummary(target_address, address)
                    node_transactions[key] = txn
                txn.add(mnano_amount)
        self.add_transactions_to_master_list(node_transactions)
        return next_nodes

    def add_transactions_to_master_list(self, transactions: Dict[str, TransactionSummary]):
        for k,transaction_summary in transactions.items():
            source = k.split("-")[0]
            target = k.split("-")[1]
            source_txns = self.all_transactions.get(source)
            if source_txns:
                target_txn = source_txns.get(target)
                if target_txn:
                    # Should check if the target is equal to incoming first
                    # If so, can just ignore, else log the error
                    logging.error("Already processed this transaction summary")
                    continue
            else:
                self.all_transactions[source] = {}
            self.all_transactions[source][target] = transaction_summary

    def draw(self):
        for source_address, targets in self.all_transactions.items():
            self.graph.add_node(source_address)
            for target_address, transaction in targets.items():
                self.graph.add_node(target_address)
                self.graph.connect(source_address,
                                   target_address,
                                   transaction.make_label())


def main():
    # test with dodgy guy from reddit https://www.reddit.com/r/WeNano/comments/lcp64f/suspected_gps_spoofer/
    starting_addresses = [
        "nano_3qt7yt39jnzq516npbiicqy4oijoez3icpgbfbqxeayfgazyzrnk8qd4bdtf"]  # TODO: Take as input
    app = FollowTheNano(starting_addresses, TransactionDirection.SEND, show_all_balance_sources=True)
    next_addrs = app.start_exploring()
    more_addrs = app.explore(next_addrs)
    most_addrs = app.explore(more_addrs)
    max_addrs = app.explore(most_addrs)
    app.draw()
    app.graph.render()  # TODO: Tighten


if __name__ == "__main__":
    main()
