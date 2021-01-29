import requests
import logging
logging.basicConfig()
root_logger = logging.getLogger()

# new logger for this script
logger = logging.getLogger('http-app')

# Sets logging level for every single app, the "parent" logger
root_logger.setLevel(logging.DEBUG)

logger.info("About to send a request to example.com")
requests.get('http://example.com')

# fine tune the urllib logger:
urllib_logger = logging.getLogger('urllib3')
urllib_logger.setLevel(logging.ERROR)

logger.info("About to send another request to example.com")
requests.get('http://example.com')
