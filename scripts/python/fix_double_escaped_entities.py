#!/usr/bin/env python3
"""Detect and repair double-escaped XML character/entity references.

``ObjectToXml.make_xml_single()`` (acdh_obj2xml_pyutils) runs
``xml.replace("&", "&amp;")`` on the full rendered XML *after* the Jinja2
templates already escaped special characters (e.g. "'" -> "&#39;",
'"' -> "&#34;", "&" -> "&amp;"). This blindly re-escapes the "&" that is
already part of a valid character/entity reference, e.g. turning
"&#39;" into "&amp;#39;" or "&amp;" (a literal "&") into "&amp;amp;".

This script scans the generated out/*.xml files for such over-escaping
and collapses it back to the intended single level of escaping, so the
affected characters (apostrophes, quotes, ampersands, ...) render
correctly once more.
"""
import glob
import re
import sys

import lxml.etree as ET

OUT_DIR = "out"
OVER_ESCAPED = re.compile(r"&amp;(#\d+;|#x[0-9A-Fa-f]+;|amp;|lt;|gt;|quot;|apos;)")


def unescape_overescaping(text):
    """Collapse any number of redundant '&' -> '&amp;' escaping layers."""
    count = 0
    while True:
        fixed, n = OVER_ESCAPED.subn(r"&\1", text)
        if n == 0:
            return text, count
        text = fixed
        count += n


def main():
    files = sorted(glob.glob(f"{OUT_DIR}/*.xml"))
    if not files:
        print(f"No .xml files found in {OUT_DIR}/")
        return 0

    had_errors = False
    for path in files:
        with open(path, "r", encoding="utf-8") as f:
            original = f.read()

        fixed, count = unescape_overescaping(original)

        if count == 0:
            print(f"{path}: OK, no double-escaped entities found")
            continue

        try:
            ET.fromstring(fixed.encode("utf-8"))
        except ET.XMLSyntaxError as err:
            had_errors = True
            print(f"{path}: found {count} double-escaped entities, but the "
                  f"fix produced invalid XML, left file untouched: {err}")
            continue

        with open(path, "w", encoding="utf-8") as f:
            f.write(fixed)
        print(f"{path}: fixed {count} double-escaped entities")

    return 1 if had_errors else 0


if __name__ == "__main__":
    sys.exit(main())
