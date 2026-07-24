"""
Database setup for HealthyEye.
Uses SQLite for zero-cost local development. Swap DATABASE_URL to a
Postgres connection string later without changing any other code,
since SQLAlchemy abstracts the engine.
"""

from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json

DATABASE_URL = "sqlite:///./healthyeye.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Medicine(Base):
    __tablename__ = "medicines"

    id = Column(Integer, primary_key=True, index=True)
    salt_name = Column(String, index=True, nullable=False)
    aliases = Column(Text)  # stored as JSON list
    common_brands = Column(String)
    used_for = Column(Text, nullable=False)
    category = Column(String)
    timing = Column(Text)
    avoid = Column(Text)
    precautions = Column(Text)
    home_remedy = Column(Text, nullable=True)

    def to_dict(self):
        return {
            "salt_name": self.salt_name,
            "aliases": json.loads(self.aliases) if self.aliases else [],
            "common_brands": self.common_brands,
            "used_for": self.used_for,
            "category": self.category,
            "timing": self.timing,
            "avoid": self.avoid,
            "precautions": self.precautions,
            "home_remedy": self.home_remedy,
        }


def init_db():
    Base.metadata.create_all(bind=engine)


def seed_db():
    from seed_data import MEDICINES

    db = SessionLocal()
    try:
        # Only seed if empty, so re-running the app doesn't duplicate rows
        if db.query(Medicine).count() == 0:
            for m in MEDICINES:
                db.add(
                    Medicine(
                        salt_name=m["salt_name"],
                        aliases=json.dumps(m["aliases"]),
                        common_brands=m["common_brands"],
                        used_for=m["used_for"],
                        category=m["category"],
                        timing=m["timing"],
                        avoid=m["avoid"],
                        precautions=m["precautions"],
                        home_remedy=m["home_remedy"],
                    )
                )
            db.commit()
            print(f"Seeded {len(MEDICINES)} medicines into the database.")
    finally:
        db.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
