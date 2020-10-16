import csv
import logging
import pathlib
import time
import urllib.request

import numpy as np
import pandas as pd
from pymongo import MongoClient

from data.labels.cow import dict_cow
from data.labels.edu import dict_schl
from data.labels.geo import dict_state, dict_region
from data.labels.ind import dict_sector, dict_industry
from data.labels.occ import dict_occupation, dict_field

import urllib.request
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


def create_dataset():
    # Start timer
    t0 = time.time()

    try:
        __file__
    except NameError:
        __file__ = "create_dataset.py"

    # set up logging
    log_file = pathlib.Path(__file__).parent.joinpath("logs/create_dataset.log")
    logging.basicConfig(
        filename=log_file,
        format="%(asctime)s %(message)s",
        level=logging.INFO,
    )
    logging.info("\n\n##### Begin creating dataset #####\n")

    # Connect to MongoDB
    client = MongoClient("mongodb://0.0.0.0:27017/")
    db = client.pums18
    logging.info(f"Connecting to database...")

    # Set API call
    d0 = time.time()
    base = "https://api.census.gov"
    dataset = "data/2018/acs/acs1/pums"
    unfiltered = "SCHL,OCCP,INDP,REGION,ST,PUMA,PWGTP,ADJINC"
    filtered = "COW=1:8&AGEP=20:80&WKHP=5:99&WAGP=400:400000"
    url = f"{base}/{dataset}?get={unfiltered}&{filtered}"
    logging.info(f"Pulling data from {url}")

    # Get API data as text DataFrame
    r = urllib.request.urlopen(url)
    df0 = pd.read_json(r.read())
    r.close()
    d1 = time.time()
    dd = round(d1 - d0, 2)
    logging.info(f"Download took {dd} seconds...")

    # Get column names then drop first row
    df0.columns = df0.iloc[0, :]
    df0 = df0.drop(index=0)
    shape0 = df0.shape

    # Cast all columns as numeric
    for c in df0.columns:
        df0[c] = pd.to_numeric(df0[c])

    # Define hourly wage based on 12mo avg
    df0["WAGE"] = (df0["WAGP"] * df0["ADJINC"]) / (df0["WKHP"] * 52)

    # Calculate log of wage for modeling
    df0["WLOG"] = np.log10(df0["WAGE"])

    logging.info("Adding labels to dataset...")

    # Do updates on a copy of the original
    df = df0.copy()

    # Merge PUMA labels dataframe
    df_pumas = pd.read_csv(
        pathlib.Path(__file__).parent.joinpath("labels/PUMA_2010_Labels.csv")
    )
    df = df.merge(
        df_pumas, left_on=["ST", "PUMA"], right_on=["STATEFP", "PUMA5CE"], how="left"
    )
    df = df.drop(columns=["STATEFP", "PUMA5CE"])

    # Rename columns
    mapper = {
        "PUMA NAME": "LOCATION",
        "AGEP": "AGE",
        "PWGTP": "WGHT",
        "WAGP": "SALARY",
        "WKHP": "HOURS",
        "REGION": "REGION_CD",
    }
    df = df.rename(columns=mapper)

    # Label coded values
    df["SCHOOLING"] = df["SCHL"].map(dict_schl)
    df["OCCUPATION"] = df["OCCP"].map(dict_occupation)
    df["INDUSTRY"] = df["INDP"].map(dict_industry)
    df["FIELD"] = df["OCCP"].map(dict_field)
    df["SECTOR"] = df["INDP"].map(dict_sector)
    df["STATE"] = df["ST"].map(dict_state)
    df["REGION"] = df["REGION_CD"].map(dict_region)
    df["WORKERTYPE"] = df["COW"].map(dict_cow)

    # Add custom bins for age group and weekly hours
    df["AGEGROUP"] = pd.cut(
        df["AGE"], [0, 29, 39, 49, 100], labels=["20s", "30s", "40s", "50s and up"]
    )
    df["WORKHOURS"] = pd.cut(
        df["HOURS"],
        [0, 39, 40, 50, 100],
        labels=["39 hours or less", "40 hours", "41 to 50 hours", "50 hours or more"],
    )
    shape = df.shape
    logging.info(f"Dataset has {shape[0]} rows and {shape[1]} columns")

    logging.info("Creating auxilliary datasets...")
    locs = (
        df[["STATE", "LOCATION", "ST", "PUMA"]]
            .drop_duplicates()
            .sort_values(["ST", "PUMA"])
            .reset_index(drop=True)
    )
    inds = (
        df[["INDP", "SECTOR", "INDUSTRY"]]
            .drop_duplicates()
            .sort_values(["INDP"])
            .reset_index(drop=True)
    )
    occs = (
        df[["OCCP", "FIELD", "OCCUPATION"]]
            .drop_duplicates()
            .sort_values(["OCCP"])
            .reset_index(drop=True)
    )
    educ = (
        df[["SCHL", "SCHOOLING"]]
            .drop_duplicates()
            .sort_values(["SCHL"])
            .reset_index(drop=True)
    )

    # Save data

    logging.info("Writing data to CSV files...")
    df.to_csv(
        pathlib.Path(__file__).parent.joinpath("csv/pums18_lab.csv"),
        index=False,
        quoting=csv.QUOTE_NONNUMERIC,
    )
    locs.to_csv(
        pathlib.Path(__file__).parent.joinpath("csv/pums18_loc.csv"),
        index=False,
        quoting=csv.QUOTE_NONNUMERIC,
    )
    inds.to_csv(
        pathlib.Path(__file__).parent.joinpath("csv/pums18_ind.csv"),
        index=False,
        quoting=csv.QUOTE_NONNUMERIC,
    )
    occs.to_csv(
        pathlib.Path(__file__).parent.joinpath("csv/pums18_occ.csv"),
        index=False,
        quoting=csv.QUOTE_NONNUMERIC,
    )
    educ.to_csv(
        pathlib.Path(__file__).parent.joinpath("csv/pums18_edu.csv"),
        index=False,
        quoting=csv.QUOTE_NONNUMERIC,
    )

    logging.info("Writing data to MongoDB...")
    db.lab.drop()
    db.loc.drop()
    db.ind.drop()
    db.occ.drop()
    db.edu.drop()
    db.lab.insert_many(df.to_dict("records"))
    db.loc.insert_many(locs.to_dict("records"))
    db.ind.insert_many(inds.to_dict("records"))
    db.occ.insert_many(occs.to_dict("records"))
    db.edu.insert_many(educ.to_dict("records"))

    t1 = time.time()
    td = round(t1 - t0, 2)
    logging.info(f"\n\n##### DONE! ##### \nCreated dataset in {td} seconds\n")


if __name__ == "__main__":
    create_dataset()
