# database.py
# Database connection setup.
# Replace the contents of this file with your actual DB connection.
#
# ── PostgreSQL (SQLAlchemy) ───────────────────────────────────
#
#   from sqlalchemy import create_engine
#   from sqlalchemy.orm import sessionmaker
#   import os
#
#   DATABASE_URL = os.getenv("DATABASE_URL")
#   engine = create_engine(DATABASE_URL)
#   SessionLocal = sessionmaker(bind=engine)
#
#   def get_db():
#       db = SessionLocal()
#       try:
#           yield db
#       finally:
#           db.close()
#
# ── MongoDB (Motor — async) ───────────────────────────────────
#
#   from motor.motor_asyncio import AsyncIOMotorClient
#   import os
#
#   client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
#   db = client["plandb"]
#
# ─────────────────────────────────────────────────────────────

# Placeholder — swap this out when you connect a real database.
def get_db():
    pass
