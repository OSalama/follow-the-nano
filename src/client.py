

import server
from models import TransactionDirection
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def main():
    # TODO: Obviously insert layer between client/server
    # test with dodgy guy from reddit https://www.reddit.com/r/WeNano/comments/lcp64f/suspected_gps_spoofer/
    starting_addresses = [
        "nano_37dbf38k93neasof139tzscgusfu18aximrawisntqxhuc1hjjw4mxnu4o7u",
"nano_1u4kyg96eo3b3i1a5x4bdm74praexzhrrimjnsa5sfneya4fhgugr7qj685j",
"nano_1pzityfyshuca135sdn95yuzhzqg189c9kki6w6j9c9z8me7u584fbgo3g6t",
"nano_1qhwjwmb7qei4bijx85wus5ipa9rgyfiqywkdmog8kn7t911y5ytm9a7c6dk",
"nano_3c8c38nsu4cp511dyj7p7qu4ctectdwb8nxmcm3cijpunfj5rpdb9jqubpdc",
"nano_1yj1mj68iaaewu57ki1za1pghwsc37jnmg4zdhaaju8g4yuzz7koexdtioqh"]  # TODO: Take as input
    # spam: nano_3qt7yt39jnzq516npbiicqy4oijoez3icpgbfbqxeayfgazyzrnk8qd4bdtf

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
    server.handle_request(starting_addresses, TransactionDirection.SEND, show_all_transactions=False)
    # At this point prompt for either exploring more (if not complete) or start a new graph


if __name__ == "__main__":
    main()
