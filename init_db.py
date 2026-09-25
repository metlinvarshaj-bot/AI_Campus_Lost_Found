from database.db import engine, Base
from database import schema

Base.metadata.create_all(bind=engine)

print("Database tables created successfully!")