import os

from app.base import Application
from app.utils import Config, get_logger

logger = get_logger(__name__)

application = Application(__name__, Config)

from app import routes

if application.config['ON_HEROKU']:
    logger.info("running on HEROKU")
    application.run(host="0.0.0.0", port=os.environ.get('PORT', 5000))
else:
    logger.info("running on local")
    application.run()
