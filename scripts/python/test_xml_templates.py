import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from jinja2 import Environment, FileSystemLoader


class XmlTemplateTests(unittest.TestCase):
    def test_bibl_template_escapes_markup_in_work_data(self):
        template_dir = Path(__file__).resolve().parents[2] / "templates"
        template = Environment(
            loader=FileSystemLoader(template_dir)
        ).get_template("bibl.xml")
        name = 'Hob <example> & "quotes"'
        xml = template.render(objects=[{
            "hsl_id": 'work"&<1',
            "Ueberprueft": False,
            "name": name,
            "Alternativtitel": "",
            "titel_original": "",
            "titel_de": "",
            "titel_en": "",
            "titel_sonstige": "",
            "Werkbezug": [],
            "schoepfer": [],
            "figur": [],
            "gnd": "",
            "wikidata": "",
            "Digitalisat": "",
        }])

        root = ET.fromstring(xml)
        namespace = "{http://www.tei-c.org/ns/1.0}"
        self.assertEqual(
            root.find(f".//{namespace}bibl/{namespace}title").text,
            name,
        )
        self.assertEqual(
            root.find(f".//{namespace}bibl").attrib[
                "{http://www.w3.org/XML/1998/namespace}id"
            ],
            'work"&<1',
        )


if __name__ == "__main__":
    unittest.main()
