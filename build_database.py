import os
import pathlib
import sqlite_utils
import sys
import yaml


def flatten(d):
    for key, value in d.items():
        if isinstance(value, dict):
            for key2, value2 in flatten(value):
                yield key + "_" + key2, value2
        else:
            yield key, value


def add_legislators(db, root):
    db["legislator_terms"].drop(ignore=True)
    db["legislators"].drop(ignore=True)
    for filename in ("legislators-historical.yaml", "legislators-current.yaml"):
        data = yaml.safe_load(pathlib.Path(root / filename).read_text())
    for item in data:
        terms = item.pop("terms")
        flattened = dict(flatten(item))
        flattened["id"] = flattened["id_bioguide"]
        flattened["name"] = flattened["name_first"] + " " + flattened["name_last"]
        pk = (
            db["legislators"]
            .insert(flattened, alter=True, pk="id", column_order=("id", "name"))
            .last_pk
        )
        for term in terms:
            term["legislator_id"] = pk
        db["legislator_terms"].insert_all(
            terms,
            alter=True,
            foreign_keys=(("legislator_id", "legislators", "id"),),
        )


def add_district_offices(db, root):
    db["offices"].drop(ignore=True)
    offices = yaml.safe_load(
        pathlib.Path(root / "legislators-district-offices.yaml").read_text()
    )
    for legislator in offices:
        legislator_id = legislator["id"]["bioguide"]
        locations = legislator["offices"]
        for office in locations:
            office["legislator_id"] = legislator_id
        db["offices"].insert_all(
            locations,
            pk="id",
            column_order=("id", "legislator_id"),
            alter=True,
            foreign_keys=(("legislator_id", "legislators", "id"),),
        )


def add_social_media(db, root):
    db["social_media"].drop(ignore=True)
    socials = yaml.safe_load(
        pathlib.Path(root / "legislators-social-media.yaml").read_text()
    )

    def fixed_socials():
        for social in socials:
            social_media = social["social"]
            social_media["id"] = social["id"]["bioguide"]
            social_media["legislator_id"] = social["id"]["bioguide"]
            yield social_media

    db["social_media"].insert_all(
        fixed_socials(),
        pk="id",
        foreign_keys=(("legislator_id", "legislators", "id"),),
        column_order=("id", "legislator_id"),
    )


def add_executives(db, root):
    db["executives"].drop(ignore=True)
    db["executive_terms"].drop(ignore=True)

    for item in yaml.safe_load(
        pathlib.Path(root / "executive.yaml").read_text()
    ):
        terms = item.pop("terms")
        flattened = dict(flatten(item))
        # Add 'name' foreign key display
        flattened["name"] = flattened["name_first"] + ' ' + flattened["name_last"]
        pk = db["executives"].insert(flattened, alter=True, pk="id", column_order=("id", "name")).last_pk
        for term in terms:
            term["executive_id"] = pk
        db["executive_terms"].insert_all(
            terms, alter=True, foreign_keys=(
                ("executive_id", "executives", "id"),
            )
        )

if __name__ == "__main__":
    try:
        db_file, congress_legislators_path = sys.argv[-2:]
        if not db_file.endswith(".db"):
            raise ValueError
        if not os.path.exists(congress_legislators_path) and os.path.isdir(congress_legislators_path):
            raise ValueError
    except ValueError:
        print("Usage: ... legislators.db ../path/to/congress-legislators")
        sys.exit(1)
    db = sqlite_utils.Database("legislators.db")
    root = pathlib.Path("../congress-legislators")
    add_legislators(db, root)
    add_district_offices(db, root)
    add_social_media(db, root)
    add_executives(db, root)
