import os
from acdh_tei_pyutils.tei import TeiReader
import re

file = os.path.join("out", "listperson.xml")

doc = TeiReader(file)
date_pattern = r'(\d{4})\s*\D+\s*(\d{4})'

for x in doc.any_xpath(".//tei:birth"):
    if x.text:
        matches = re.findall(date_pattern, x.text)
        for match in matches:
            birth_year, death_year = match
            if int(birth_year) < int(death_year):
                x.attrib["notBefore"] = f"{birth_year}-01-01"
                x.attrib["notAfter"] = f"{birth_year}-12-31"
doc.tree_to_file(file)

for x in doc.any_xpath(".//tei:death"):
    if x.text:
        matches = re.findall(date_pattern, x.text)
        for match in matches:
            birth_year, death_year = match
            if int(birth_year) < int(death_year):
                x.attrib["notBefore"] = f"{death_year}-01-01"
                x.attrib["notAfter"] = f"{death_year}-12-31"
doc.tree_to_file(file)
