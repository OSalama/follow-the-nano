
from graph import NanoGraph
from typing import Dict, List
from collections import defaultdict
from decimal import Decimal
from models import TransactionSummary, TransactionDirection, RAW_TO_MNANO
from rpc import HistoryRequestor

MAX_DEPTH = 4 # TODO: Input

API_KEY = ""

IGNORE_LIST = [
                "nano_3jwrszth46rk1mu7rmb4rhm54us8yg1gw3ipodftqtikf5yqdyr7471nsg1k" #Binance
              ] # Possible TODO: hook into mynano.ninja for aliases

class FollowTheNano:

    def __init__(self, starting_addresses, traversal_direction, show_all_balance_sources=False):
        self.starting_addresses = starting_addresses
        self.traversal_direction = traversal_direction
        self.show_all_balance_sources = show_all_balance_sources
        self.graph = NanoGraph()
        self.history_requestor = HistoryRequestor(use_real_rpc=True) # TODO: Input
    
    def start_exploring(self):
        for address in self.starting_addresses:
            self.graph.add_starting_node(address)
        addresses_to_explore = set(self.starting_addresses)
        explored_nodes = set()
        depth_counter = 0
        balance_sources = []
        while depth_counter < MAX_DEPTH and addresses_to_explore:
            next_addresses_to_explore = set()
            # FUXME: all the duplication... (better but still needs work)
            for address in addresses_to_explore:
                if address in explored_nodes or address in IGNORE_LIST:
                    continue
                transaction_history = self.history_requestor.get_account_history(address)
                sends, receives = summarise_transactions(address, transaction_history)
                if self.traversal_direction == TransactionDirection.SEND:
                    transactions_to_follow = sends
                    balance_sources.append(receives)
                elif self.traversal_direction == TransactionDirection.RECEIVE:
                    transactions_to_follow = receives
                    balance_sources.append(sends)

                for next_node, transaction_summary in transactions_to_follow.items():
                    if next_node not in explored_nodes:
                        next_addresses_to_explore.add(next_node)
                    self.graph.add_node(next_node)
                    self.graph.connect(address, next_node, transaction_summary.make_label(self.traversal_direction))
                explored_nodes.add(address)
            depth_counter += 1
            addresses_to_explore = next_addresses_to_explore
        if self.show_all_balance_sources:
            for aux_tx in balance_sources:
                for aux_address, aux_summary in aux_tx.items():
                    if aux_address in explored_nodes:
                        continue
                    address = aux_summary.address
                    self.graph.add_node(aux_address)
                    self.graph.connect(aux_address, address, aux_summary.make_label(self.traversal_direction.invert()))

def summarise_transactions(address: str, transactions: Dict) -> Dict[str, TransactionSummary]:
    sends = defaultdict(lambda: TransactionSummary(address))
    receives = defaultdict(lambda: TransactionSummary(address))
    for transaction in transactions:
        raw_amount = transaction["amount"]
        mnano_amount = (Decimal(raw_amount) / RAW_TO_MNANO)
        direction = TransactionDirection(transaction["type"])
        if direction == TransactionDirection.SEND:
            sends[transaction["account"]].process_send(mnano_amount)
        elif direction == TransactionDirection.RECEIVE:
            receives[transaction["account"]].process_receive(mnano_amount)
    return sends, receives

def main():
    # test with dodgy guy from reddit https://www.reddit.com/r/WeNano/comments/lcp64f/suspected_gps_spoofer/
    starting_addresses = [
        "nano_3qt7yt39jnzq516npbiicqy4oijoez3icpgbfbqxeayfgazyzrnk8qd4bdtf"]  # TODO: Take as input
    app = FollowTheNano(starting_addresses, TransactionDirection.SEND)
    app.start_exploring()
    app.graph.render() # TODO: Tighten


if __name__ == "__main__":
    main()
