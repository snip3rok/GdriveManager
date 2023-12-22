import databases
import sqlalchemy

metadata = sqlalchemy.MetaData()
database = databases.Database("sqlite:///test.db")
engine = sqlalchemy.create_engine("sqlite:///test.db")