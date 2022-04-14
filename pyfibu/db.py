import datetime
import sqlalchemy

from sqlalchemy import (
        MetaData,
        Table,
        Column,
        Integer,
        Numeric,
        String,
        DateTime,
        Date,
        Boolean,
        Text
)
from sqlalchemy import UniqueConstraint, PrimaryKeyConstraint
from sqlalchemy import insert

import click
from flask import current_app, g
from flask.cli import with_appcontext

from werkzeug.security import generate_password_hash

metadata = MetaData()

user_table = Table(
    "fibuuser",
    metadata,
    Column("email", String(255), primary_key=True),
    Column("name", String(255), nullable=False),
    Column("password", String(255), nullable=False),
    Column("locale", String(20)),
    Column("timezone", String(20)),
)

mandate_table = Table(
    "fibumandate",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(255), nullable=False),
    Column("description", Text),
)

period_table = Table(
    "fibuperiod",
    metadata,
    Column("period", String(100), primary_key=True),
    Column("startdate", Date, nullable=False),
    Column("enddate", Date, nullable=False),
    Column("accounts", Text, nullable=False),
)

entry_table = Table(
    "fibuentry",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("period", String(100), nullable=False),
    Column("number", Integer, nullable=False),
    Column("text", String(255), nullable=False),
    Column("debit", Integer, nullable=False),
    Column("credit", Integer, nullable=False),
    Column("amount", Numeric(10, 2), nullable=False),
)

def get_db():
    if 'engine' not in g:
        g.engine = sqlalchemy.create_engine(current_app.config['DATABASE'], client_encoding="utf8")
    return g.engine

def close_db(e=None):
    engine = g.pop('engine', None)
    if engine is not None:
        engine.dispose()

def init_db():
    engine = get_db()

    metadata.drop_all(engine)
    metadata.create_all(engine)

    with engine.begin() as conn:
        conn.execute(
            insert(user_table).values(
                email="admin@pyfibu.ch",
                name="admin",
                locale="en",
                timezone="CET",
                password=generate_password_hash(current_app.config['ADMIN_PASSWORD']))
        )

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables"""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
