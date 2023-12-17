import logging

import pytest
from httpx import Client
from pydantic import BaseModel

_logger = logging.getLogger(__name__)

host, port = "localhost", 3000

url = f"http://{host}:{port}"


class Cat(BaseModel):
    id: str
    name: str
    gender: str


cats: list[Cat] = [
    Cat(id="1", name="Garfield", gender="M"),
    Cat(id="2", name="Tom", gender="F"),
]


@pytest.mark.cats
class TestCats:
    """
    Turn on server and test cats module
    """

    def test_list_cats(self, test_http_client: Client):
        res = test_http_client.get(f"{url}/cats")
        assert res.status_code == 200
        for idx, cat_json in enumerate(res.json()):
            assert cat_json["id"] == cats[idx].id
            assert cat_json["name"] == cats[idx].name
            assert cat_json["gender"] == cats[idx].gender

    def test_create_cat(self, test_http_client: Client):
        res = test_http_client.post(
            f"{url}/cats/", json={"id": "3", "name": "asdf", "gender": "M"}
        )
        assert res.status_code == 200
        res_json = res.json()

        assert res_json["id"] == "3"
        assert res_json["name"] == "asdf"
        assert res_json["gender"] == "M"

    def test_retrieve_cat(self, test_http_client: Client):
        res = test_http_client.get(f"{url}/cats/{cats[0].id}")
        assert res.status_code == 200
        res_json = res.json()

        assert res_json["id"] == cats[0].id
        assert res_json["name"] == cats[0].name
        assert res_json["gender"] == cats[0].gender
