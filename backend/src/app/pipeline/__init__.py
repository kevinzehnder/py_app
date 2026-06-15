"""Kaufvertrag pipeline — filesystem job store + orchestration.

Thin glue around pi-tools: ingest source docs, LLM-extract structured data,
fetch/clean GBA, render ODT/PDF. State lives on disk (one directory per job);
no database. See ``jobs`` for the store and ``service`` for the steps.
"""
