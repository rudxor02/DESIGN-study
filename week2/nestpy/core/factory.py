import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from inspect import _empty
from json import dumps, loads
from typing import Any, Optional
from urllib.parse import parse_qs, urlparse

from nestpy.common import (
    APIInfo,
    Body,
    Class,
    Instance,
    InstanceInitiator,
    Param,
    ParameterInfo,
    Query,
    get_api_info_list,
)
from pydantic import BaseModel

_logger = logging.getLogger(__name__)


class NestPyHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """
        This will be replace by NestPyHTTPRequestHandlerBuilder
        """
        parsed_path = urlparse(self.path)
        query = parse_qs(parsed_path.query)
        _logger.info(parsed_path.path)
        _logger.info(parsed_path.params)
        _logger.info(f"query: {query}")
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"message": "hello world"}')

    def do_POST(self):
        """
        This will be replace by NestPyHTTPRequestHandlerBuilder
        """
        self.send_response(200)
        content_len = int(self.headers.get("Content-Length"))
        post_body = self.rfile.read(content_len)
        post_body = loads(post_body)
        _logger.info(f"post_body: {post_body}")
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"message": "hello world"}')


class NestPyHTTPRequestHandlerBuilder:
    def __init__(self, root_module_cls: Class):
        self._handler = NestPyHTTPRequestHandler
        self._instance_initiator = InstanceInitiator()
        self._instance_initiator.register_cls(root_module_cls)
        self._instance_initiator.get_or_init_instance(root_module_cls)

    def match_path(self, path: str, nestpy_path: str) -> Optional[dict[str, str]]:
        splitted_path = path.strip("/").split("/")
        splitted_nestpy_path = nestpy_path.split("/")
        if len(splitted_path) != len(splitted_nestpy_path):
            return None
        path_params: dict[str, str] = {}
        for i in range(len(splitted_path)):
            if splitted_nestpy_path[i].startswith(":"):
                path_params[splitted_nestpy_path[i][1:]] = splitted_path[i]
            elif splitted_nestpy_path[i] != splitted_path[i]:
                return None
        return path_params

    def build(self) -> type[NestPyHTTPRequestHandler]:
        controllers = self._instance_initiator.get_controllers()
        api_info_with_instance_list: list[tuple[APIInfo, Instance]] = []
        for controller in controllers:
            for api_info in get_api_info_list(controller):
                api_info_with_instance_list.append((api_info, controller))

        builder = self

        def build_path_param_inputs(
            path_param_info_dict: dict[str, ParameterInfo], path_params: dict[str, str]
        ) -> dict[str, Param[Any]]:
            return_val: dict[str, Param[Any]] = {}
            for param_name, _param_info in path_param_info_dict.items():
                return_val[param_name] = Param(path_params[param_name])
            return return_val

        def build_body_param_inputs(
            body_param_info_dict: dict[str, ParameterInfo], body: dict[str, Any]
        ) -> dict[str, Body[Any]]:
            return_val: dict[str, Body[Any]] = {}
            for param_name, _param_info in body_param_info_dict.items():
                return_val[param_name] = Body(body)
            return return_val

        def build_query_param_inputs(
            query_param_info_dict: dict[str, ParameterInfo],
            query_params: dict[str, Any],
        ) -> dict[str, Query[Any]]:
            return_val: dict[str, Query[Any]] = {}
            for param_name, param_info in query_param_info_dict.items():
                try:
                    return_val[param_name] = Query(query_params[param_name][0])
                except KeyError:
                    if param_info.required:
                        raise ValueError(f"missing required query param: {param_name}")
                    if param_info.default is _empty:
                        raise Exception(
                            f"missing default value for query param: {param_name}"
                        )
            return return_val

        def _nestpy_process_request(self: NestPyHTTPRequestHandler):
            for api_info, instance in api_info_with_instance_list:
                if (
                    self.command == api_info.request_method
                    and (path_params := builder.match_path(self.path, api_info.path))
                    is not None
                ):
                    if self.headers.get("Content-Length") is None:
                        post_body: dict[str, Any] = {}
                    else:
                        content_len = int(self.headers.get("Content-Length"))
                        post_body = self.rfile.read(content_len)
                        post_body = loads(post_body)

                    func = getattr(instance, api_info.func_name)
                    res = func(
                        **build_body_param_inputs(
                            api_info.body_param_info_dict, post_body
                        ),
                        **build_query_param_inputs(
                            api_info.query_param_info_dict,
                            parse_qs(urlparse(self.path).query),
                        ),
                        **build_path_param_inputs(
                            api_info.path_param_info_dict, path_params
                        ),
                    )
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    if isinstance(res, BaseModel):
                        res = res.json()
                    if isinstance(res, dict):
                        res = dumps(res)
                    if isinstance(res, str):
                        res = res.encode()
                    if isinstance(res, int):
                        res = res.to_bytes()
                    if not isinstance(res, bytes):
                        raise Exception(f"unsupported type: {type(res)}")
                    self.wfile.write(res)
                    return
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"message": "path not found"}')

        self._handler._nestpy_process_request = _nestpy_process_request

        def do_GET(self: NestPyHTTPRequestHandler):
            self._nestpy_process_request()

        self._handler.do_GET = do_GET

        def do_POST(self: NestPyHTTPRequestHandler):
            self._nestpy_process_request()

        self._handler.do_POST = do_POST
        return self._handler


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
        httpd = NestFactory(server_address, handler_builder.build())
        return httpd
