from flask import Flask

from app.utils import get_logger, ApplicationInitializationException

logger = get_logger(__name__)


class Application(Flask):
    def __init__(self, name, config_class, **kwargs):
        if not name or not config_class:
            raise ApplicationInitializationException

        super(Application, self).__init__(name, **kwargs)
        self.config.from_object(config_class)
