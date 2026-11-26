#!/usr/bin/env python3
import argparse

from baserow_utils import fill_person_dates


TABLE_ID = "1499"

parser = argparse.ArgumentParser()
parser.add_argument(
    "--overwrite",
    action="store_true",
    help="Overwrite existing birth and death dates."
)

args = parser.parse_args()

fill_person_dates(
    br_table_id=TABLE_ID,
    overwrite=args.overwrite
)
