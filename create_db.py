from database import Base, engine
# It's crucial to import the models here, even though the linter
# might say 'models' is an unused import. This step is what registers
# your tables with SQLAlchemy's metadata.
import models

print("Creating database tables...")

# Create all tables
Base.metadata.create_all(bind=engine)

print("Database tables created successfully.")

