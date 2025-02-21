from baserow_utils import make_xml, make_geojson


data = {
    "persons": "json_dumps/Personen.json",
    "places": "json_dumps/Orte.json",
    "works": "json_dumps/Werke.json"
}

listperson = make_xml(data["persons"], "listperson", "gnd", "persons")
listplace = make_xml(data["places"], "listplace", "geonames_id", "places")
listbibl = make_xml(data["works"], "listbibl", "hsl_id", "bibl")

placejson = make_geojson(data["places"], "listplace", "geonames_coordinates", "google_maps_coordinates", "not-relevant")
