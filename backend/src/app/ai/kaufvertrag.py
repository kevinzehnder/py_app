"""Kaufvertrag structured data model + LLM extraction.

``KaufvertragData`` mirrors the variables consumed by pi-tools'
``template_kaufvertrag.md.j2`` (rendered via ``pi_tools.kaufvertrag.fill_template``).

The template is rendered with Jinja2 ``StrictUndefined``: any *missing* key raises.
Therefore **every field carries a default** so ``model_dump()`` always yields a
complete dict. Empty strings are fine (defined, just blank) — only missing keys
break rendering. ``tests/test_pipeline_render.py`` is the guard that this model
covers every unconditionally-referenced template variable.

The same model doubles as the pydantic-ai extraction ``output_type``: the LLM
fills the fields it can find in the source document and leaves the rest at default.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import BaseModel, Field

# ── party building blocks ────────────────────────────────────────────────────


class Person(BaseModel):
    """One natural person (used for Erbengemeinschaft members)."""

    vorname: str = ""
    name: str = ""
    geburtsname: str = ""
    zivilstand: str = ""
    heimatort: str = ""
    wohnort: str = ""
    adresse: str = ""


class Ehepartner(BaseModel):
    vorname: str = ""
    name: str = ""
    geburtsname: str = ""
    heimatort: str = ""


class Eheleute(BaseModel):
    frau: Ehepartner = Field(default_factory=Ehepartner)
    herr: Ehepartner = Field(default_factory=Ehepartner)
    beide_in: str = ""
    adresse: str = ""


class Erben(BaseModel):
    vorname: str = ""
    name: str = ""
    geburtsname: str = ""
    sterbedatum: str = ""
    heimatort: str = ""
    personen: list[Person] = Field(default_factory=list)


class AG(BaseModel):
    name: str = ""
    uid: str = ""
    sitz: str = ""
    adresse: str = ""


class Einzel(BaseModel):
    vorname: str = ""
    name: str = ""
    geburtsname: str = ""
    heimatort: str = ""
    wohnort: str = ""
    adresse: str = ""


class Eigentumsart(BaseModel):
    miteigentuemer_je_halb: bool = False
    alleineigentuemer: bool = False
    gesamteigentuemer_einfach: bool = False
    gesamteigentuemer_erben: bool = False


class Party(BaseModel):
    """Verkäufer- or Käuferschaft. ``typ`` selects which variant block renders.

    ``typ`` one of: "eheleute" | "erben" | "ag" | "einzel" (empty = render nothing).
    """

    typ: str = ""
    eheleute: Eheleute = Field(default_factory=Eheleute)
    erben: Erben = Field(default_factory=Erben)
    ag: AG = Field(default_factory=AG)
    einzel: Einzel = Field(default_factory=Einzel)
    eigentumsart: Eigentumsart = Field(default_factory=Eigentumsart)


# ── Kaufobjekt / Kaufpreis ───────────────────────────────────────────────────


class Kaufobjekt(BaseModel):
    egrid: str = ""
    grundstueck_nr: str = ""
    gemeinde: str = ""
    grundbuchauszug: str = ""
    lage: str = ""
    flaeche: str = ""
    stockwerkeigentum_beschrieb: str = ""
    auto_einstellplatz_nr: str = ""
    miteigentum_beschrieb: str = ""
    vormerkungen: str = ""
    anmerkungen: str = ""
    dienstbarkeiten: str = ""
    nutzen_gefahr_termin: str = ""


class Aufteilung(BaseModel):
    beschreibung: str = ""
    betrag: str = ""


class Zahlung(BaseModel):
    anzahlung_betrag: str = ""
    anzahlung_ausgeschrieben: str = ""
    anzahlung_valuta: str = ""
    anzahlung_konto: str = ""
    anzahlung_lautend: str = ""
    steuer_betrag: str = ""
    steuer_ausgeschrieben: str = ""
    steuer_konto: str = ""
    steuer_gemeinde: str = ""
    steuer_vermerk: str = ""
    steuer_uid: str = ""
    steuer_firma: str = ""
    steuer_datum_beurkundung: str = ""
    steuer_3prozent: str = ""
    uebertrag: str = ""
    schuldbrief_art: str = ""
    hypothek_nominell_chf: str = ""
    hypothek_bank: str = ""
    hypothek_betrag: str = ""
    hypothek_ausgeschrieben: str = ""
    hypothek_valuta: str = ""
    hypothek_effektiv_chf: str = ""
    rest_betrag: str = ""
    rest_ausgeschrieben: str = ""
    rest_valuta: str = ""
    rest_konto: str = ""
    rest_lautend: str = ""
    mietzins_ab: str = ""


class Kaufpreis(BaseModel):
    betrag: str = ""
    betrag_ausgeschrieben: str = ""
    aufteilung: list[Aufteilung] = Field(default_factory=list)
    total: str = ""
    total_ausgeschrieben: str = ""
    zahlung: Zahlung = Field(default_factory=Zahlung)


# ── options / Grundbuch / Notariat ───────────────────────────────────────────


class ObergaWahl(BaseModel):
    """Template ``obera_wahl`` — option switches. Each value is a short code.

    nutzen_gefahr: "a" = Antrittstermin, else Eigentumsübertragung.
    gewaerleistung: "b" = übernimmt geräumt/gereinigt.
    reinigung: "a" = besenrein, else gereinigt.
    mietverhaeltnisse: "a" = Mietverträge bestehen, else keine.
    elektrokontrolle: "a" = vor Übergang ausgeführt, else nachher.
    auslaender: "a" = Aufenthaltsbewilligung-Block, else BewG-frei.
    """

    nutzen_gefahr: str = ""
    gewaerleistung: str = ""
    reinigung: str = ""
    mietverhaeltnisse: str = ""
    elektrokontrolle: str = ""
    auslaender: str = ""


class GrundbuchPerson(BaseModel):
    name: str = ""
    geboren: str = ""
    heimatort: str = ""


class Grundbuch(BaseModel):
    grundbuchamt: str = ""
    eintragungsart: str = ""
    nummer: str = ""
    eigentumsart: str = ""
    kbs_option: str = "nicht"  # "nicht" = not in KBS register (the common case)
    zweiteintrag_namensaenderung: str = ""
    verkaeufer: GrundbuchPerson = Field(default_factory=GrundbuchPerson)
    kaeufer: GrundbuchPerson = Field(default_factory=GrundbuchPerson)


class Notariat(BaseModel):
    firma_handelsregister_kanton: str = ""
    firma_sitz: str = ""
    vr_funktion: str = ""
    vr_name: str = ""
    vr_geboren: str = ""
    vr_heimatort: str = ""
    vr_wohnort: str = ""
    vr_zeichnungsart: str = ""
    familienwohnung_pruefung: str = ""


class Urkundsperson(BaseModel):
    name: str = ""
    kanon: str = ""  # template uses ``urkundsperson.kanon`` (Kanton)


# ── root ─────────────────────────────────────────────────────────────────────


class KaufvertragData(BaseModel):
    """Complete data set for one Kaufvertrag, matching the Jinja2 template."""

    urkundsperson: Urkundsperson = Field(default_factory=Urkundsperson)
    ort: str = ""
    datum: str = ""
    protokoll_nr: str = ""

    verkaeufer: Party = Field(default_factory=Party)
    kaeufer: Party = Field(default_factory=Party)
    kaufobjekt: Kaufobjekt = Field(default_factory=Kaufobjekt)
    kaufpreis: Kaufpreis = Field(default_factory=Kaufpreis)
    obera_wahl: ObergaWahl = Field(default_factory=ObergaWahl)
    grundbuch: Grundbuch = Field(default_factory=Grundbuch)
    notariat: Notariat = Field(default_factory=Notariat)

    # Auslaender block (only referenced when obera_wahl.auslaender == "a").
    aufenthaltsbewilligung: str = ""
    zemis_nummer: str = ""
    ablaufdatum: str = ""
    wohnort: str = ""


# ── extraction agent ─────────────────────────────────────────────────────────

INSTRUCTIONS = (
    "You extract structured data for a Swiss real-estate purchase contract "
    "(Kaufvertrag) from the provided source document text. Fill only the fields "
    "you can find explicit evidence for; leave everything else at its default "
    "(empty string / false / empty list). Do not invent values. For party `typ`, "
    "use one of: eheleute, erben, ag, einzel. Dates as written in the source. "
    "Money amounts as plain numbers/strings without currency symbols."
)


@lru_cache
def get_extraction_agent():
    """Return the cached Kaufvertrag extraction agent.

    Imported lazily (pydantic-ai is the optional ``ai`` extra). Reuses the Azure
    model builder from ``app.ai.agent``.
    """
    from pydantic_ai import Agent

    from app.ai.agent import _build_model

    return Agent(
        _build_model(),
        output_type=KaufvertragData,
        instructions=INSTRUCTIONS,
    )


async def extract_kaufvertrag(source_markdown: str) -> KaufvertragData:
    """Extract structured Kaufvertrag data from source document Markdown/text."""
    result = await get_extraction_agent().run(
        f"Source document:\n\n{source_markdown}"
    )
    return result.output
