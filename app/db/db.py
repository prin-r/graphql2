import json
import random
import string

from decimal import Decimal
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database, drop_database

from app.db import Base


def random_db_name():
    return f"pricer_{int(datetime.utcnow().timestamp())}_{''.join(random.choice(string.ascii_lowercase) for i in range(5))}"


def _default(val):
    if isinstance(val, Decimal):
        return str(val)
    raise TypeError()


def dumps(d):
    return json.dumps(d, default=_default)


class Database(object):
    def __init__(self, dburi, dbname, reset):
        if dbname is None:
            dbname = random_db_name()

        if not dburi.endswith("/"):
            dburi = dburi + "/"

        engine = create_engine(
            dburi + dbname, json_serializer=dumps, echo=False
        )
        if database_exists(engine.url) and reset:
            drop_database(engine.url)

        if not database_exists(engine.url):
            create_database(engine.url)
            Base.metadata.create_all(engine)

        self.Session = sessionmaker(bind=engine)

    def get_session(self):
        return self.Session()

