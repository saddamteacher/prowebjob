"""Tests for the HH.UZ web search parser."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "jobhunter_crm"))

from parsers.base import ParserError
from parsers.uzbekistan.hhuz import HHUZParser, CATEGORY_QUERIES

SEARCH_URL = "https://tashkent.hh.uz/search/vacancy"

CARD_HTML = """
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


class FakeResponse:
    def __init__(self, text):
        self.text = text


def test_parses_search_cards_and_dedupes_across_queries():
    parser = HHUZParser()
    calls = []

    def fake_get(url, **kwargs):
        calls.append(url)
        return FakeResponse(CARD_HTML)

    parser.get = fake_get

    items = parser.parse()

    assert len(items) == 1
    assert items[0]["title"] == "Python Developer"
    assert items[0]["company"] == "Example LLC"
    assert items[0]["city"] == "Tashkent"
    assert items[0]["url"] == "https://tashkent.hh.uz/vacancy/123"
    assert set(calls) == {SEARCH_URL}
    # First query reads page 0 (new card) and page 1 (no new cards -> stop);
    # every other query stops after page 0.
    assert len(calls) == len(CATEGORY_QUERIES) + 1


def test_blocked_query_is_skipped():
    parser = HHUZParser()

    def fake_get(url, **kwargs):
        if kwargs["params"]["text"] == CATEGORY_QUERIES[0]:
            raise ParserError("HH.UZ: HTTP 403")
        return FakeResponse(CARD_HTML)

    parser.get = fake_get

    items = parser.parse()

    assert [i["url"] for i in items] == ["https://tashkent.hh.uz/vacancy/123"]
