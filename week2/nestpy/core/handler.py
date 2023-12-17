import logging
from http.server import BaseHTTPRequestHandler
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


def match_path(path: str, nestpy_path: str) -> Optional[dict[str, str]]:
    splitted_path = path.strip("/").split("/")
    splitted_nestpy_path = nestpy_path.strip("/").split("/")
    if len(splitted_path) != len(splitted_nestpy_path):
        return None
    path_params: dict[str, str] = {}
    for i in range(len(splitted_path)):
        if splitted_nestpy_path[i].startswith(":"):
            path_params[splitted_nestpy_path[i][1:]] = splitted_path[i]
        elif splitted_nestpy_path[i] != splitted_path[i]:
            return None
    return path_params


class NestPyHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """
        This will be replace by NestPyHTTPRequestHandlerBuilder
        """
        pass

    def do_POST(self):
        """
        This will be replace by NestPyHTTPRequestHandlerBuilder
        """
        pass


class NestPyHTTPRequestHandlerBuilder:
    def __init__(self, root_module_cls: Class):
        self._handler = NestPyHTTPRequestHandler
        self._instance_initiator = InstanceInitiator()
        self._instance_initiator.register_cls(root_module_cls)
        self._instance_initiator.get_or_init_instance(root_module_cls)

        controllers = self._instance_initiator.get_controllers()
        self.api_info_with_instance_list: list[tuple[APIInfo, Instance]] = []
        for controller in controllers:
            for api_info in get_api_info_list(controller):
                self.api_info_with_instance_list.append((api_info, controller))

    def build_path_param_inputs(
        self,
        path_param_info_dict: dict[str, ParameterInfo],
        path_params: dict[str, str],
    ) -> dict[str, Param[Any]]:
        return_val: dict[str, Param[Any]] = {}
        for param_name, _param_info in path_param_info_dict.items():
            return_val[param_name] = Param(path_params[param_name])
        return return_val

    def build_body_param_inputs(
        self, body_param_info_dict: dict[str, ParameterInfo], body: dict[str, Any]
    ) -> dict[str, Body[Any]]:
        return_val: dict[str, Body[Any]] = {}
        for param_name, param_info in body_param_info_dict.items():
            if BaseModel in param_info.type.__bases__:
                print(body)
                return_val[param_name] = Body(param_info.type(**body))
                continue
            return_val[param_name] = Body(body)
        return return_val

    def build_query_param_inputs(
        self,
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
                        f"missing value for query param: {param_name} {param_info}"
                    )
                return_val[param_name] = Query(param_info.default)
        return return_val

    def _nestpy_process_request(self, handler: NestPyHTTPRequestHandler):
        for api_info, instance in self.api_info_with_instance_list:
            if (
                handler.command == api_info.request_method
                and (path_params := match_path(handler.path, api_info.path)) is not None
            ):
                if handler.headers.get("Content-Length") is None:
                    post_body: dict[str, Any] = {}
                else:
                    content_len = int(handler.headers.get("Content-Length"))
                    post_body = handler.rfile.read(content_len)
                    post_body = post_body.decode("utf-8")
                    post_body = loads(post_body)

                func = getattr(instance, api_info.func_name)
                res = func(
                    **self.build_body_param_inputs(
                        api_info.body_param_info_dict, post_body
                    ),
                    **self.build_query_param_inputs(
                        api_info.query_param_info_dict,
                        parse_qs(urlparse(handler.path).query),
                    ),
                    **self.build_path_param_inputs(
                        api_info.path_param_info_dict, path_params
                    ),
                )
                handler.send_response(200)
                handler.send_header("Content-type", "application/json")
                handler.end_headers()
                if isinstance(res, BaseModel):
                    res = res.json()
                if isinstance(res, dict):
                    res = dumps(res)
                if isinstance(res, list):
                    res = [x.dict() for x in res]
                    res = dumps(res)
                if isinstance(res, str):
                    res = res.encode()
                if isinstance(res, int):
                    res = res.to_bytes()
                if not isinstance(res, bytes):
                    raise Exception(f"unsupported type: {type(res)}")
                handler.wfile.write(res)
                return
        handler.send_response(404)
        handler.end_headers()
        handler.wfile.write(b'{"message": "path not found"}')

    def build_handler(self) -> type[NestPyHTTPRequestHandler]:
        builder = self
        self._handler._nestpy_process_request = builder._nestpy_process_request

        def do_GET(self: NestPyHTTPRequestHandler):
            builder._nestpy_process_request(self)

        self._handler.do_GET = do_GET

        def do_POST(self: NestPyHTTPRequestHandler):
            builder._nestpy_process_request(self)

        self._handler.do_POST = do_POST
        return self._handler
