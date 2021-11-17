from databases import Database
from sqlalchemy import create_engine, Column, Integer, String, LargeBinary, MetaData, Table
from .settings import settings

SQLALCHEMY_DATABASE_URL = settings.database_url
connect_args = {}

if 'sqlite://' in SQLALCHEMY_DATABASE_URL:
    connect_args["check_same_thread"] = False

database = Database(SQLALCHEMY_DATABASE_URL)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args=connect_args
)

metadata = MetaData()

is_bootstrapping = not engine.dialect.has_table(engine, 'raw_files')

raw_files = Table(
    "raw_files_0",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("filename", String),
    Column("mime_type", String),
    Column("contents", LargeBinary)
)

metadata.create_all(engine)


