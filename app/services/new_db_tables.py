from sqlalchemy import create_engine, Column, Integer, BigInteger, Text, JSON
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

db_password = os.getenv("POSTGRES_PASSWORD")
db_user = os.getenv("POSTGRES_USER")

Base = declarative_base()

class Client(Base):
    __tablename__ = 'clients'

    id = Column(BigInteger, primary_key=True, nullable=False)
    first_name = Column(Text)
    username = Column(Text)
    cityandcoords = Column(JSON)
    currency = Column(Text)
    weather_daily_count = Column(Integer, default=0)
    weatherweek_daily_count = Column(Integer, default=0)
    currency_count = Column(Integer, default=0)

class CurrencyTable(Base):
    __tablename__ = 'currency_table'
    id = Column(BigInteger, primary_key=True)
    currency_value = Column(JSON)
    currency_key = Column(Text)

engine = create_engine(f'postgresql://{db_user}:{db_password}@postgres:5432/mydb', echo=True)


def create_tables():
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    create_tables()