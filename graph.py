


from graphviz import Digraph


NANOCRAWLER_ACCOUNT_URL = "https://nanocrawler.cc/explorer/account/{address}/history"


class NanoGraph:

    def __init__(self) -> None:
        self.graph = Digraph(graph_attr={"rankdir": "LR"})

    def add_starting_node(self, address: str) -> None:
        self.graph.node(address, URL=NANOCRAWLER_ACCOUNT_URL.format(address=address))

    def add_node(self, address: str) -> None:
        self.graph.node(address,
                        label=address[:10], # Limit address length for easier viewing of graph
                        URL=NANOCRAWLER_ACCOUNT_URL.format(address=address))
    
    def connect(self, from_address: str, to_address: str, transaction_label: str):
        self.graph.edge(from_address, to_address, label=transaction_label)

    def render(self):
        self.graph.render("test.gv", view=True, format="svg")