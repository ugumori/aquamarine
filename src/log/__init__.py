import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(levelname)s:%(filename)s:%(lineno)d: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
