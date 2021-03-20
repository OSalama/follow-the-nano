

from models import TransactionSummary
from graphviz import Digraph


NANOCRAWLER_ACCOUNT_URL = "https://nanocrawler.cc/explorer/account/{address}/history"


class NanoGraph:

    def __init__(self, root_nodes, aliases) -> None:
        self.graph = Digraph(graph_attr={"rankdir": "LR"})
        self.root_nodes = root_nodes
        self.aliases = aliases
        for node in self.root_nodes:
            self.graph.node(
                node, URL=NANOCRAWLER_ACCOUNT_URL.format(address=node))

    def add_node(self, address: str) -> None:
        if address not in self.root_nodes:
            if address in self.aliases:
                label = self.aliases[address]
            else:
                label = address[:10] # Limit address length for easier viewing of graph
            self.graph.node(address,
                            label=label,
                            URL=NANOCRAWLER_ACCOUNT_URL.format(address=address))

    def connect(self, transaction_summary: TransactionSummary) -> None:
        self.graph.edge(transaction_summary.source_address,
                        transaction_summary.target_address,
                        label=f"{transaction_summary.total_amount}/{transaction_summary.total_num_transactions}"
                        )

    def render_graph(self):
        self.graph.render("test.gv", view=True, format="svg")

    def add_transaction(self, transaction_summary: TransactionSummary):
        self.add_node(transaction_summary.source_address)
        self.add_node(transaction_summary.target_address)
        self.connect(transaction_summary)
