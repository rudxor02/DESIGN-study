import logging

# week2 base dir is not root
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(process)d:%(name)s:%(lineno)s] [%(levelname)s] %(message)s",
)

pytest_plugins = ["tests.fixtures"]
