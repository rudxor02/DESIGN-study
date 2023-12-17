import logging
from http.server import HTTPServer

from nestpy.common import Class

from .handler import NestPyHTTPRequestHandlerBuilder

_logger = logging.getLogger(__name__)


class NestFactory(HTTPServer):
    def serve(self):
        _logger.info(f"Server is running on {self.server_address}")
        self.serve_forever()

    @staticmethod
    def create(
        root_module_cls: Class, host: str = "localhost", port: int = 3000
    ) -> "NestFactory":
        server_address = (host, port)
        handler_builder = NestPyHTTPRequestHandlerBuilder(root_module_cls)
        httpd = NestFactory(server_address, handler_builder.build_handler())
        return httpd
