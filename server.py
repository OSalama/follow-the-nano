import logging
from nano_explorer import FollowTheNano
import requests
from flask import Flask, request

app = Flask(__name__)

IS_TESTING_MODE = False
NANO_NINJA_BASE_URL = "https://mynano.ninja/api"
ALIASES_ENDPOINT = "accounts/aliases"
API_KEY = ""
SEPARATOR = "-"


logger = logging.getLogger("follow_the_nano")  # TODO: Refactor
logger.setLevel(logging.INFO)


def handle_request(starting_addresses, direction, show_all_transactions=False, explore_depth=6):
    with app.app_context():
        explore_request = FollowTheNano(starting_addresses,
                                        direction,
                                        show_all_transactions=show_all_transactions,
                                        aliases=nano_aliases)
        explore_count = 0
        next_addresses = set(starting_addresses)
        while explore_count < explore_depth:
            next_addresses = explore_request.explore(next_addresses)
            if not next_addresses:
                logger.warning("No more addresses to explore, we done here!")
                break  # Set a flag when breaking so we can let user know this is complete
            explore_count += 1
        logger.info(
            f"Graph cost {explore_request.history_requestor.call_counter} RPC calls")
        explore_request.render_transactions()
        # At this point prompt for either exploring more (if not complete) or start a new graph

@app.route("/explore/<address>")
def explore_address(address):
    starting_addresses = request.args.get("starting_addresses")
    direction = request.args.get("direction")
    show_all_transactions = request.args.get("show_all_transactions")
    explore_depth = request.args.get("explore_depth")
    handle_request(starting_addresses, direction, show_all_transactions=show_all_transactions, explore_depth=explore_depth)


def get_aliases():
    endpoint = f"{NANO_NINJA_BASE_URL}/{ALIASES_ENDPOINT}"
    resp = requests.get(endpoint)
    resp_json = resp.json()
    # TODO: Error handling
    aliases = {alias["account"]: alias["alias"] for alias in resp_json}
    return aliases

nano_aliases = get_aliases() # FIXME: Feels horribly wrong to do this
