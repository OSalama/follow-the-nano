

from graphviz import Digraph


NANOCRAWLER_ACCOUNT_URL = "https://nanocrawler.cc/explorer/account/{address}/history"


class NanoGraph:

    def __init__(self, root_nodes) -> None:
        self.graph = Digraph(graph_attr={"rankdir": "LR"})
        self.root_nodes = root_nodes
        for node in self.root_nodes:
            self.graph.node(
                node, URL=NANOCRAWLER_ACCOUNT_URL.format(address=node))

    def add_node(self, address: str) -> None:
        if address not in self.root_nodes:
            self.graph.node(address,
                            # Limit address length for easier viewing of graph
                            label=address[:10],
                            URL=NANOCRAWLER_ACCOUNT_URL.format(address=address))

    def connect(self, from_address: str, to_address: str, transaction_label: str):
        self.graph.edge(from_address, to_address, label=transaction_label)

    def render(self):
        self.graph.render("test.gv", view=True, format="svg")
