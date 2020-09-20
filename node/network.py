import json

import requests

from node.blockchain import Block


class NetworkHandler(object):

    def __init__(self):
        self.peers = set()

    def announce_new_block(self, block: Block):
        """
        A function to announce to the network once a block has been mined.
        Other blocks can simply verify the proof of work and add it to their
        respective chains.
        """
        for peer in self.peers:
            url = "{}add_block".format(peer)
            headers = {'Content-Type': "application/json"}
            requests.post(url,
                          data=json.dumps(block.__dict__, sort_keys=True),
                          headers=headers)
