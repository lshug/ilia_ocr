from databases import Database
from sqlalchemy import create_engine, Column, Integer, String, LargeBinary, MetaData, Table
from .settings import settings

SQLALCHEMY_DATABASE_URL = settings.database_url

database = Database(SQLALCHEMY_DATABASE_URL)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

metadata = MetaData()

raw_files = Table(
    "raw_files",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("filename", String),
    Column("mime_type", String),
    Column("contents", LargeBinary)
)

metadata.create_all(engine)
