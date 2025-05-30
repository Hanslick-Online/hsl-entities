import requests
import geocoder
import json
from time import sleep
from acdh_id_reconciler import geonames_to_gnd, geonames_to_wikidata, gnd_to_wikidata_custom
from AcdhArcheAssets.uri_norm_rules import get_normalized_uri
from acdh_obj2xml_pyutils import ObjectToXml

from config import (BASEROW_URL, BASEROW_TOKEN, br_client)


def enrich_data(br_table_id, uri, field_name_input, field_name_update):
    table = [x for x in br_client.yield_rows(br_table_id=br_table_id)]
    br_rows_url = f"{BASEROW_URL}database/rows/table/{br_table_id}/"
    v_wd = 0
    v_geo = 0
    v_pmb = 0
    v_oebl = 0
    v_oeml = 0
    for x in table:
        update = {}
        if uri == "gnd":
            if (len(x[field_name_input["gnd"]]) > 0):
                norm_id = get_normalized_uri(x[field_name_input["gnd"]])
                print(norm_id)
                try:
                    # custom = oeml
                    wd = gnd_to_wikidata_custom(norm_id, "P8432")
                    wd_id = wd["wikidata"]
                    update[field_name_update["wikidata"]] = wd_id
                    v_wd += 1
                    print(f"gnd id matched with wikidata: {wd_id}")
                    if len(wd["custom"]) > 0:
                        oeml = f'https://www.musiklexikon.ac.at/ml/musik_{wd["custom"]}.xml'
                        update[field_name_update["oeml"]] = oeml
                        v_oeml += 1
                        print(f"gnd id matched with oeml: {oeml}")
                except Exception as err:
                    print(err)
                    print(f"no match for {norm_id} found.")
                try:
                    # custom = oebl
                    wd = gnd_to_wikidata_custom(norm_id, "P6194")
                    if len(wd["custom"]) > 0:
                        oebl = f'https://www.biographien.ac.at/oebl/oebl_{wd["custom"]}.xml'
                        update[field_name_update["oebl"]] = oebl
                        v_oebl += 1
                        print(f"gnd id matched with oebl: {oebl}")
                except Exception as err:
                    print(err)
                    print(f"no oebl match for {norm_id} found.")
                try:
                    wd = gnd_to_wikidata_custom(norm_id, "P12483")
                    if len(wd["custom"]) > 0:
                        pmb = wd["custom"]
                        update[field_name_update["pmb"]] = f"https://pmb.acdh.oeaw.ac.at/entity/{pmb}"
                        v_pmb += 1
                        print(f"gnd id matched with pmb: https://pmb.acdh.oeaw.ac.at/entity/{pmb}")
                except Exception as err:
                    print(err)
                    print(f"no pmb match for {norm_id} found.")
        if uri == "geonames":
            if (len(x[field_name_input["geonames"]]) and len(x[field_name_input["wikidata"]]) == 0):
                norm_id = get_normalized_uri(x[field_name_input["geonames"]])
                print(norm_id)
                update[field_name_update["geonames"]] = norm_id
                try:
                    geo = geonames_to_gnd(norm_id)
                    gnd = geo["gnd"]
                    update[field_name_update["gnd"]] = f"https://d-nb.info/gnd/{gnd}"
                    wd = geo["wikidata"]
                    update[field_name_update["wikidata"]] = wd
                    v_geo += 1
                    print(f"geonames id matched with gnd: {gnd} and wikidata: {wd}")
                except Exception:
                    try:
                        wd = geonames_to_wikidata(norm_id)
                        wd = wd["wikidata"]
                        update[field_name_update["wikidata"]] = wd
                    except Exception:
                        print(f"no wikidata match for {norm_id} found.")
                    print(f"no gnd match for {norm_id} found.")
        if update:
            row_id = x["id"]
            url = f"{br_rows_url}{row_id}/?user_field_names=true"
            try:
                requests.patch(
                    url,
                    headers={
                        "Authorization": f"Token {BASEROW_TOKEN}",
                        "Content-Type": "application/json"
                    },
                    json=update
                )
                print(f"{url} : updated")
            except Exception as err:
                print(err)
        sleep(0.25)
    print(f"{v_wd} wikidata uri and {v_geo} geonames uri of {len(table)} table rows matched")


def geonames_to_location(br_table_id, user, field_name_input, field_name_update):
    table = [x for x in br_client.yield_rows(br_table_id=br_table_id)]
    br_rows_url = f"{BASEROW_URL}database/rows/table/{br_table_id}/"
    geo_u = 0
    for x in table:
        update = {}
        if (len(x[field_name_input["geonames"]]) > 0 and x["updated"] is False):
            norm_id = get_normalized_uri(x[field_name_input["geonames"]])
            print(norm_id)
            geo_id = norm_id.split('/')[-2]
            try:
                g = geocoder.geonames(geo_id, method='details', key=user)
            except Exception as err:
                print(f"no match for {norm_id} found. Error {err}")
            if g:
                lat = g.lat
                lng = g.lng
                typ = g.class_description
                typ_c = g.feature_class
                ctry_c = g.country_code
                ctry = g.country
                if lat and lng:
                    update[field_name_update["coordinates"]] = f"{lat}, {lng}"
                if typ:
                    update[field_name_update["place_type"]] = typ
                if typ_c:
                    update[field_name_update["place_type_class"]] = typ_c
                if ctry:
                    update[field_name_update["country"]] = ctry
                if ctry_c:
                    update[field_name_update["country_code"]] = ctry_c
                print(f"geonames id {geo_id} found. Updating lat: {lat} and lng: {lng}")
                geo_u += 1
        if update:
            update["updated"] = True
            row_id = x["id"]
            url = f"{br_rows_url}{row_id}/?user_field_names=true"
            try:
                requests.patch(
                    url,
                    headers={
                        "Authorization": f"Token {BASEROW_TOKEN}",
                        "Content-Type": "application/json"
                    },
                    json=update
                )
                print(f"{url} : updated")
            except Exception as err:
                print(err)
        sleep(0.25)
    print(f"{geo_u} geonames uri and of {len(table)} table rows matched")


def make_xml(input, fn, clmn, temp):
    with open(input, "rb") as f:
        file = json.load(f)
    arr = []
    for f in file:
        obj = file[f]
        try:
            any_id = obj[clmn]
            norm_id = get_normalized_uri(any_id)
            obj[clmn] = norm_id
        except KeyError as err:
            print(err)
        arr.append(obj)
    filename = fn
    template_file = f"templates/{temp}.xml"
    obj_cl = ObjectToXml(br_input=arr, filename=filename, template_path=template_file)
    tei = obj_cl.make_xml_single(save=True)
    print(f"{fn}.xml created")
    return tei


def make_geojson(input, fn, clmn1, clmn2, clm3):
    geojson = {
        "type": "FeatureCollection",
        "features": []
    }
    with open(input, "rb") as f:
        file = json.load(f)
    for f in file:
        obj = file[f]
        try:
            loc = obj[clmn1]
        except KeyError as err:
            print(err)
            loc = False
        if loc:
            if len(loc) != 0:
                coords = loc
                coords = coords.split(", ")
                feature_point = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [float(coords[1]), float(coords[0])]
                    },
                    "properties": {
                        "title": obj["ortsname"],
                        "id": obj["hsl_id"],
                        "country_code": obj["country_code"]
                    }
                }
                geojson["features"].append(feature_point)
        try:
            loc = obj[clmn2]
        except KeyError as err:
            print(err)
            loc = False
        if loc:
            if len(loc) != 0:
                coords = loc
                coords = coords.split(", ")
                feature_point = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [float(coords[1]), float(coords[0])]
                    },
                    "properties": {
                        "title": obj["ortsname"],
                        "id": obj["hsl_id"],
                        "country_code": obj["country_code"]
                    }
                }
                geojson["features"].append(feature_point)
        try:
            loc = obj[clm3]
        except KeyError as err:
            print(err)
            loc = []
        if len(loc) > 0:
            nm = obj["ortsname"]
            o_id = obj["hsl_id"]
            for x in loc:
                try:
                    coords = x["data"][clmn1]
                except KeyError:
                    coords = {}
                if coords:
                    coords = coords.split(", ")
                    feature_point = {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [float(coords[1]), float(coords[0])]
                        },
                        "properties": {
                            "title": nm,
                            "id": o_id,
                            "title_plc": x["data"]["ortsname"],
                            "id_plc": x["data"]["hsl_id"],
                            "country_code": x["data"]["country_code"]
                        }
                    }
                    geojson["features"].append(feature_point)
                else:
                    try:
                        coords = x["data"][clmn2]
                    except KeyError:
                        coords = {}
                    if len(coords) > 0:
                        coords = coords.split(", ")
                        feature_point = {
                            "type": "Feature",
                            "geometry": {
                                "type": "Point",
                                "coordinates": [float(coords[1]), float(coords[0])]
                            },
                            "properties": {
                                "title": nm,
                                "id": o_id,
                                "title_plc": x["data"]["name"],
                                "id_plc": x["data"]["hsl_id"],
                                "country_code": x["data"]["country_code"]
                            }
                        }
                        geojson["features"].append(feature_point)
    with open(f"out/{fn}.geojson", "w") as f:
        json.dump(geojson, f)
    return geojson


def load_lockup(path, mapping):
    files = {}
    for x in mapping:
        ldn = mapping[x].split(".")[0]
        with open(f"{path}/{mapping[x]}", "rb") as fb:
            files[ldn] = json.load(fb)
    with open(f"{path}/test_{mapping[x]}", "w") as fb:
        json.dump(files, fb)
    return files


def load_base(fn):
    with open(fn, "rb") as fb:
        data = json.load(fb)
    return data


def denormalize_json(fn, path, mapping):
    save_and_open = f"{path}/{fn}.json"
    print(f"updating {save_and_open}")
    # load mapping file
    mpg = mapping
    # load lockup file to match with
    files = load_lockup(path, mpg)
    # load base json file for matching
    dta = load_base(save_and_open)
    for m in mpg:
        # if mapping key is found in base json
        for d in dta:
            if dta[d][m]:
                # get filename without ext
                ldn = mpg[m].split(".")[0]
                # get specific mapping from lockup file
                lockup = files[ldn]
                # iterate over mapping entity array
                for i in dta[d][m]:
                    i_id = i["id"]
                    # use id for lockup file
                    i_upt = lockup[str(i_id)]
                    # create normalized data
                    norm = {n: i_upt[n] for n in i_upt
                            if not isinstance(i_upt[n], list) and n != "id" and n != "order"}
                    i["data"] = norm
                    i["data"]["filename"] = mpg[m]
    with open(save_and_open, "w") as w:
        json.dump(dta, w)
    print(f"finished update of {save_and_open} and save as {save_and_open}.")
    return dta
