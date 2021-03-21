import logging
from typing import List
from nano_explorer import FollowTheNano
from models import TransactionDirection, RAW_TO_MNANO
import requests

IS_TESTING_MODE = False
NANO_NINJA_BASE_URL = "https://mynano.ninja/api"
ALIASES_ENDPOINT = "accounts/aliases"
API_KEY = ""
SEPARATOR = "-"


logger = logging.getLogger("follow_the_nano")  # TODO: Refactor
logger.setLevel(logging.INFO)


class FollowTheNanoServer:

    def __init__(self):
        self.aliases = get_aliases()

    def new_request(self, starting_addresses, direction, explore_depth=4, show_all_transactions=False):
        explore_request = FollowTheNano(starting_addresses,
                                        direction,
                                        show_all_transactions=show_all_transactions,
                                        aliases=self.aliases)
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


def get_aliases():
    endpoint = f"{NANO_NINJA_BASE_URL}/{ALIASES_ENDPOINT}"
    resp = requests.get(endpoint)
    resp_json = resp.json()
    # TODO: Error handling
    aliases = {alias["account"]: alias["alias"] for alias in resp_json}
    return aliases
