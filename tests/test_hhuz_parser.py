"""Tests for the HH.UZ parser fallback."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "jobhunter_crm"))

from parsers.base import ParserError
from parsers.uzbekistan.hhuz import HHUZParser, QUERIES


class FakeResponse:
    def __init__(self, text):
        self.text = text


def test_falls_back_to_web_search_when_api_is_blocked():
    html = """
    <div data-qa="vacancy-serp__vacancy">
      <a data-qa="serp-item__title"
         href="https://tashkent.hh.uz/vacancy/123?query=python">
        Python Developer
      </a>
      <a data-qa="vacancy-serp__vacancy-employer">Example LLC</a>
      <span data-qa="vacancy-serp__vacancy-address">Tashkent</span>
      Python Django PostgreSQL
    </div>
    """
    parser = HHUZParser()
    calls = []

    def fake_get(url, **kwargs):
        calls.append(url)
        if url.endswith("/vacancies"):
            raise ParserError("HH.UZ: HTTP 403")
        return FakeResponse(html)

    parser.get = fake_get

    items = parser.parse()

    assert len(items) == 1
    assert items[0]["title"] == "Python Developer"
    assert items[0]["company"] == "Example LLC"
    assert items[0]["city"] == "Tashkent"
    assert items[0]["url"] == "https://tashkent.hh.uz/vacancy/123"
    assert calls.count("https://tashkent.hh.uz/search/vacancy") == len(QUERIES)
