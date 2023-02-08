import os
import json

persons = "json_dumps/Personen.json"
save_fn = "out/beacon.txt"

try:
    os.remove(save_fn)
except FileNotFoundError as err:
    print(err)


def beacon_generator(file, save_fn):
    with open(file, "r") as f:
        dta = json.load(f)
    with open(save_fn, "a") as f:
        f.writelines("#FORMAT: BEACON\n")
        f.writelines("#NAME: Hanslick Online\n")
    for x in dta:
        dta_id = dta[x]["hsl_id"]
        dta_name = dta[x]["name"]
        dta_gnd = dta[x]["gnd"]
        if len(dta_gnd) > 0:
            with open(save_fn, "a") as f:
                f.writelines(f"{dta_gnd}|{dta_name}|https://hanslick.acdh.oeaw.ac.at/{dta_id}.html\n")
    return [f"{dta[x]['gnd']}|{dta[x]['name']}|{dta[x]['hsl_id']}.html" for x in dta if len(dta[x]['gnd']) > 0]


beacon_generator(persons, save_fn)
