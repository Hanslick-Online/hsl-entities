from baserow_utils import enrich_data


TABLE_ID = "1498"
enrich_data(br_table_id=TABLE_ID, uri="gnd",
            field_name_input={"gnd": "gnd", "wikidata": "wikidata"},
            field_name_update={"wikidata": "wikidata", "gnd": "gnd",
                               "oeml": "oeml", "oebl": "oebl", "pmb": "pmb"})

TABLE_ID = "1500"
enrich_data(br_table_id=TABLE_ID,
            uri="geonames",
            field_name_input={"gnd": "gnd", "geonames": "geonames_id", "wikidata": "wikidata"},
            field_name_update={"wikidata": "wikidata", "gnd": "gnd", "geonames": "geonames_id"})
