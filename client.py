

import server
from models import TransactionDirection
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def main():
    # TODO: Obviously insert layer between client/server
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
    server.handle_request(starting_addresses, TransactionDirection.SEND)
    # At this point prompt for either exploring more (if not complete) or start a new graph


if __name__ == "__main__":
    main()
