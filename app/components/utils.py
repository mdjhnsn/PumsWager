from pymongo import MongoClient

url = "mongodb://localhost:27017/"
client = MongoClient(url)
db = client.pums18


def get_options(input_column):
    return [{"label": option, "value": option} for option in input_column]


def get_states():
    states = db.loc.distinct("STATE")
    return [{"label": state, "value": state} for state in states]


def get_sectors():
    sectors = db.ind.distinct("SECTOR")
    return get_options(sectors)


def get_fields():
    fields = db.occ.distinct("FIELD")
    return get_options(fields)


def get_schooling():
    schooling = db.edu.distinct("SCHOOLING")
    return get_options(schooling)


def get_columns():
    columns = [
        "SALARY",
        "HOURS",
        "AGE",
        "FIELD",
        "SECTOR",
    ]
    return get_options(columns)
