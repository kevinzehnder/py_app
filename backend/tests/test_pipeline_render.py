"""Guard tests for the Kaufvertrag pipeline.

The template renders with Jinja2 StrictUndefined, so a default-constructed
``KaufvertragData`` must contain every unconditionally-referenced template
variable. ``fill_template`` raising here means a field is missing from the schema.
"""

from __future__ import annotations

from app.ai.kaufvertrag import KaufvertragData


def test_default_data_renders_without_strict_undefined() -> None:
    from pi_tools.kaufvertrag import DEFAULT_TEMPLATE, fill_template

    data = KaufvertragData().model_dump()
    markdown = fill_template(DEFAULT_TEMPLATE, data)

    assert markdown.strip()
    assert "# Kaufvertrag" in markdown


def test_populated_party_renders() -> None:
    from pi_tools.kaufvertrag import DEFAULT_TEMPLATE, fill_template

    data = KaufvertragData()
    data.verkaeufer.typ = "einzel"
    data.verkaeufer.einzel.vorname = "Anna"
    data.verkaeufer.einzel.name = "Muster"
    data.kaeufer.typ = "ag"
    data.kaeufer.ag.name = "Bau AG"
    data.kaufobjekt.gemeinde = "Neuenhof"
    data.kaufobjekt.grundstueck_nr = "119"
    data.kaufpreis.betrag = "500000"

    markdown = fill_template(DEFAULT_TEMPLATE, data.model_dump())

    assert "Anna" in markdown
    assert "Muster" in markdown
    assert "Bau AG" in markdown
    assert "Neuenhof" in markdown
