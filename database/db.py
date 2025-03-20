from sqlmodel import create_engine, Session
from setup.settings import DATABASE_URL

engine = create_engine(f"{DATABASE_URL}", echo=True)

SessionLocal = Session(autocommit=True, autoflush=False, bind=engine)

def get_db():
    with Session(engine) as session:
        yield session