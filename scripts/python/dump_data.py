#!/usr/bin/env python3
import requests

from config import br_client, BASEROW_DB_ID


def yield_rows(br_table_id, filters={}):
    # Baserow returns "next" links with http://, which fail behind the https proxy
    url = f"{br_client.br_base_url}database/rows/table/{br_table_id}/?user_field_names=true"
    for key, value in filters.items():
        url += f"&{key}={value}"
    while url:
        print(url)
        response = requests.get(url, headers=br_client.headers)
        response.raise_for_status()
        result = response.json()
        url = result["next"]
        if url and url.startswith("http://"):
            url = "https://" + url[len("http://"):]
        yield from result["results"]


br_client.yield_rows = yield_rows

files = br_client.dump_tables_as_json(BASEROW_DB_ID, folder_name="json_dumps", indent=2)
print(files)
