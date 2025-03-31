from sqlalchemy.orm import DeclarativeBase

# Base model for sonsit model behaviour
class Base(DeclarativeBase):

    pass

# User -> Books (One-to-Many)
# User -> Orders (One-to-Many)
# User -> Addresses (One-to-Many)
# User -> Reviews (One-to-Many)
# Order -> Books (Many-to-Many)
# Book -> Orders (Many-to-Many)
