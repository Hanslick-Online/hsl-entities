from baserow_utils import denormalize_json
from config import (MAPPING_PERSONS, MAPPING_WORKS)


denormalize_json("Personen", "json_dumps", MAPPING_PERSONS)
denormalize_json("Werke", "json_dumps", MAPPING_WORKS)
