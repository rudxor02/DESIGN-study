import logging

from cats.module import CatsModule
from nestpy.core import NestFactory

# week2 base dir is not root
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(process)d:%(name)s:%(lineno)s] [%(levelname)s] %(message)s",
)


def bootstrap():
    app = NestFactory.create(CatsModule)
    app.serve()


bootstrap()
