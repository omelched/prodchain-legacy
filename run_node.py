import os

import node

if node.application.config['ON_HEROKU']:
    node.logger.info("running on HEROKU")
    node.application.run(host="0.0.0.0", port=os.environ.get('PORT', 5000))
else:
    node.logger.info("running on local")
    node.application.run()
