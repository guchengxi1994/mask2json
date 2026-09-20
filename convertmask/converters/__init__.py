"""Converter dispatch: one entry point for CLI and web server."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from convertmask import METHOD_ALIASES
from convertmask.converters.json_converters import json_to_mask, json_to_xml
from convertmask.converters.mask_converters import mask_to_json, mask_to_xml
from convertmask.converters.xml_converters import xml_to_json, xml_to_mask, xml_to_yolo
from convertmask.converters.yolo_converters import yolo_to_xml

CONVERTERS: dict[str, Callable[..., list[Path]]] = {
    "mask2json": mask_to_json,
    "mask2xml": mask_to_xml,
    "json2mask": json_to_mask,
    "json2xml": json_to_xml,
    "xml2json": xml_to_json,
    "xml2yolo": xml_to_yolo,
    "yolo2xml": yolo_to_xml,
    "xml2mask": xml_to_mask,
}

# which kwarg names each method accepts (for CLI/server validation)
CONVERTER_ARGS: dict[str, list[str]] = {
    "mask2json": ["imgs", "masks", "out", "classes"],
    "mask2xml": ["imgs", "masks", "out", "classes"],
    "json2mask": ["jsons", "out", "classes"],
    "json2xml": ["jsons", "out"],
    "xml2json": ["xmls", "imgs", "out"],
    "xml2yolo": ["xmls", "out", "classes"],
    "yolo2xml": ["txts", "imgs", "classes", "out"],
    "xml2mask": ["xmls", "out", "classes"],
}


def normalize_method(method: str) -> str:
    """Resolve full names and aliases (m2j, x2y, ...) to a canonical name."""
    alias_to_full = {v: k for k, v in METHOD_ALIASES.items()}
    if method in CONVERTERS:
        return method
    full = alias_to_full.get(method)
    if full:
        return full
    raise ValueError(
        f"unknown method {method!r}; supported: {sorted(CONVERTERS)} "
        f"or aliases {sorted(alias_to_full)}"
    )


def convert(method: str, /, **kwargs) -> list[Path]:
    """Run a conversion by method name or alias; returns output file paths."""
    full = normalize_method(method)
    unexpected = set(kwargs) - set(CONVERTER_ARGS[full])
    if unexpected:
        raise TypeError(f"{full}: unexpected arguments {sorted(unexpected)}")
    return CONVERTERS[full](**kwargs)
