from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base
# SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
SQLALCHEMY_DATABASE_URL = "postgresql://tododb_sjgb_user:4jtxKUK1fY0N4npgfagK8PL1j1L7MakK@dpg-d6qoeo7afjfc73es4p7g-a.oregon-postgres.render.com/tododb_sjgb"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
