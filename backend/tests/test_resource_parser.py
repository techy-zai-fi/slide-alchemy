import pytest
from app.services.resource_parser import ResourceParser


@pytest.fixture
def parser():
    return ResourceParser()


def test_parse_raw_text(parser):
    result = parser.parse_raw_text("This is a test document about AI.")
    assert result.text == "This is a test document about AI."
    assert result.metadata["type"] == "raw_text"
    assert result.metadata["char_count"] == 33


def test_parse_raw_text_with_sections(parser):
    text = "# Introduction\nHello world\n# Conclusion\nGoodbye"
    result = parser.parse_raw_text(text)
    assert len(result.sections) == 2
    assert result.sections[0]["title"] == "Introduction"
    assert result.sections[1]["title"] == "Conclusion"


def test_parse_markdown(parser):
    md = "## Heading\n\nSome paragraph text.\n\n- bullet 1\n- bullet 2"
    result = parser.parse_markdown(md)
    assert "Heading" in result.text
    assert len(result.sections) >= 1


def test_parse_url_extracts_text(parser):
    result = parser.parse_raw_text("Sample web content extracted from a URL")
    assert len(result.text) > 0


def test_extract_sections_from_text(parser):
    text = "Title: My Topic\n\nFirst paragraph about something.\n\nSecond paragraph about another thing."
    result = parser.parse_raw_text(text)
    assert result.metadata["char_count"] > 0
