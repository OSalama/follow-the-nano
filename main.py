
import logging
from typing import DefaultDict, Dict, List
from graphviz import Digraph
import nano
from decimal import Decimal

MAX_DEPTH = 4
SEND_OR_RECEIVE = "send"
#NODE_URL = "https://mynano.ninja/api/node"
NODE_URL = "https://proxy.nanos.cc/proxy"
API_KEY = ""
RAW_TO_MNANO = Decimal(10 ** 30)
RPC = nano.rpc.Client(NODE_URL)
TRANSACTION_HISTORY_LIMIT = 100


def main():
    dot = Digraph(graph_attr={"rankdir": "LR"})
    # test with dodgy guy from reddit https://www.reddit.com/r/WeNano/comments/lcp64f/suspected_gps_spoofer/
    starting_addresses = [
        "nano_3qt7yt39jnzq516npbiicqy4oijoez3icpgbfbqxeayfgazyzrnk8qd4bdtf"]  # TODO: Take as input
    explore_addresses(dot, starting_addresses)
    dot.render("test.gv", view=True, format="svg")


def rpc_account_history(nano_address: str) -> Dict:
    logging.info("Requesting account history for %s", nano_address)
    response = RPC.account_history(
        account=nano_address, count=TRANSACTION_HISTORY_LIMIT)
    return response


def get_transactions(transactions: Dict) -> Dict[str, Decimal]:
    recipients = DefaultDict(int)
    for transaction in transactions:
        if transaction["type"] == SEND_OR_RECEIVE:
            recipients[transaction["account"]] += (Decimal(transaction["amount"]) / RAW_TO_MNANO)
    return recipients


def explore_addresses(dot: Digraph, starting_addresses: List[str]):
    for address in starting_addresses:
        dot.node(address)
    addresses_to_explore = set(starting_addresses)
    explored_nodes = set()
    depth_counter = 0
    while depth_counter < MAX_DEPTH and addresses_to_explore:
        next_addresses_to_explore = set()
        for address in addresses_to_explore:
            if address in explored_nodes:
                continue
            resp = rpc_account_history(address)
            transactions = get_transactions(resp)
            for recipient, amount in transactions.items():
                if recipient not in explored_nodes:
                    next_addresses_to_explore.add(recipient)
                dot.node(recipient,
                         label=recipient[:10], # Limit addresses for easier viewing of graph
                         link=f"https://nanocrawler.cc/explorer/account/{recipient}/history")
                dot.edge(address, recipient, label=str(amount))
            explored_nodes.add(address)
        depth_counter += 1
        addresses_to_explore = next_addresses_to_explore


if __name__ == "__main__":
    main()
