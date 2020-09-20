from flask import Flask

from node.blockchain import BlockchainHandler
from node.network import NetworkHandler
from node.utils import get_logger, ApplicationInitializationException

logger = get_logger(__name__)


class Application(Flask, BlockchainHandler, NetworkHandler):
    def __init__(self, name, config_class, **kwargs):
        if not name or not config_class:
            raise ApplicationInitializationException

        Flask.__init__(self, name, **kwargs)
        BlockchainHandler.__init__(self)
        NetworkHandler.__init__(self)

        self.config.from_object(config_class)




