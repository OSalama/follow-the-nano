
import logging
from typing import DefaultDict, Dict, List
from graphviz import Digraph
import nano
from decimal import Decimal
from random import randint

MAX_DEPTH = 4

#TODO: Enum
SEND = "send"
RECEIVE = "receive"
TESTING = False
BIG_PICTURE = True

TRAVERSAL_DIRECTION = SEND # TODO: Take input

NODE_URL = "" # Put your node URL in here. Public nodes available at https://publicnodes.somenano.com/
NANOCRAWLER_ACCOUNT_URL = "https://nanocrawler.cc/explorer/account/{address}/history"
API_KEY = ""
RAW_TO_MNANO = Decimal(10 ** 30)
TRANSACTION_HISTORY_LIMIT = 100 # TODO: Input
IGNORE_LIST = [
                "nano_3jwrszth46rk1mu7rmb4rhm54us8yg1gw3ipodftqtikf5yqdyr7471nsg1k" #Binance
              ] # Possible TODO: hook into mynano.ninja for aliases


class TransactionSummary:

    def __init__(self):
        self.amount_received = Decimal()
        self.total_num_receives = 0
        self.amount_sent = Decimal()
        self.total_num_sends = 0

    def make_label(self, reverse=False):
        if not reverse:
            if TRAVERSAL_DIRECTION == SEND:
                return f"{self.amount_sent}/{self.total_num_sends}"
            elif TRAVERSAL_DIRECTION == RECEIVE:
                return f"{self.amount_received}/{self.total_num_receives}"
        else:
            if TRAVERSAL_DIRECTION == SEND:
                return f"{self.amount_received}/{self.total_num_receives}"
            elif TRAVERSAL_DIRECTION == RECEIVE:
                return f"{self.amount_sent}/{self.total_num_sends}"

    def process_send(self, mnano_amount):
        self.total_num_sends += 1
        self.amount_sent += mnano_amount

    def process_receive(self, mnano_amount):
        self.total_num_receives += 1
        self.amount_received += mnano_amount


def main():
    rpc_client = nano.rpc.Client(NODE_URL)
    dot = Digraph(graph_attr={"rankdir": "LR"})
    # test with dodgy guy from reddit https://www.reddit.com/r/WeNano/comments/lcp64f/suspected_gps_spoofer/
    starting_addresses = [
        "nano_3qt7yt39jnzq516npbiicqy4oijoez3icpgbfbqxeayfgazyzrnk8qd4bdtf"]  # TODO: Take as input
    explore_addresses(dot, starting_addresses, rpc_client)
    dot.render("test.gv", view=True, format="svg")


def explore_addresses(dot: Digraph, starting_addresses: List[str], rpc_client: nano.rpc.Client):
    for address in starting_addresses:
        dot.node(address, URL=NANOCRAWLER_ACCOUNT_URL.format(address=address))
    addresses_to_explore = set(starting_addresses)
    explored_nodes = set()
    depth_counter = 0
    while depth_counter < MAX_DEPTH and addresses_to_explore:
        next_addresses_to_explore = set()
        # FUXME: all the duplication...
        for address in addresses_to_explore:
            if address in explored_nodes or address in IGNORE_LIST:
                continue
            transaction_history = get_account_history(address, rpc_client)
            sends, receives = summarise_transactions(transaction_history)
            if TRAVERSAL_DIRECTION == SEND:
                follows = sends
                aux = receives
            elif TRAVERSAL_DIRECTION == RECEIVE:
                follows = receives
                aux = sends

            for next_node, transaction_summary in follows.items():
                if next_node not in explored_nodes:
                    next_addresses_to_explore.add(next_node)
                dot.node(next_node,
                         label=next_node[:10], # Limit address length for easier viewing of graph
                         URL=NANOCRAWLER_ACCOUNT_URL.format(address=next_node))
                dot.edge(address, next_node, label=transaction_summary.make_label())
            if BIG_PICTURE:
                for aux_node, aux_summary in aux.items():
                    dot.node(aux_node,
                            label=aux_node[:10], # Limit address length for easier viewing of graph
                            URL=NANOCRAWLER_ACCOUNT_URL.format(address=aux_node))
                    dot.edge(aux_node, address, label=aux_summary.make_label(reverse=True))
            explored_nodes.add(address)
        depth_counter += 1
        addresses_to_explore = next_addresses_to_explore

def rpc_account_history(nano_address: str, rpc_client: nano.rpc.Client) -> Dict:
    logging.info("Requesting account history for %s", nano_address)
    response = rpc_client.account_history(
        account=nano_address, count=TRANSACTION_HISTORY_LIMIT)
    return response

def get_account_history(nano_address: str, rpc_client: nano.rpc.Client) -> Dict:
    # FIXME: Refactor
    if TESTING:
        return random_history(nano_address)
    else:
        return rpc_account_history(nano_address, rpc_client)

def random_history(nano_address: str) -> Dict:
    logging.info("Faking account history for %s", nano_address)
    numtx = randint(1, 2)
    transactions = []
    for _ in range(numtx):
        account = f"nano_{randint(1000, 9999)}"
        transactions.append(
            {"type": "send", "account": account, "amount": randint(1, 10) * RAW_TO_MNANO})
    return transactions

def summarise_transactions(transactions: Dict) -> Dict[str, TransactionSummary]:
    sends = DefaultDict(TransactionSummary)
    receives = DefaultDict(TransactionSummary)
    for transaction in transactions:
        raw_amount = transaction["amount"]
        mnano_amount = (Decimal(raw_amount) / RAW_TO_MNANO)
        if transaction["type"] == SEND:
            sends[transaction["account"]].process_send(mnano_amount)
        elif transaction["type"] == RECEIVE:
            receives[transaction["account"]].process_receive(mnano_amount)
    return sends, receives


if __name__ == "__main__":
    main()
