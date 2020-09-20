from node.base import Application
from node.utils import Config, get_logger

logger = get_logger(__name__)

application = Application(__name__, Config)

from node import routes
