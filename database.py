from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column, relationship
from sqlalchemy import ForeignKey
from typing import List

engine = create_async_engine(
    "sqlite+aiosqlite:///finance.db"
)

# mapper_registry = registry()
new_session = async_sessionmaker(engine, expire_on_commit=False)
# Base = declarative_base(metadata=mapper_registry.metadata)

# class Model(DeclarativeBase):
#     pass

class Base(DeclarativeBase):
    pass

class UserOrm(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    login: Mapped[str]
    email: Mapped[str]
    password: Mapped[str]
    balance: Mapped[float]
    code: Mapped[str]

    accounts: Mapped[List["AccountOrm"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

class AccountOrm(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    balance: Mapped[float]
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    user = relationship("UserOrm", back_populates="accounts")

    # transactions: Mapped[List["TransactionOrm"]] = relationship(
    #     back_populates="transaction", cascade="all, delete-orphan"
    # )

# class TransactionOrm(Base):
#     __tablename__ = "transactions"
#
#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str]
#     description: Mapped[str]
#     amount: Mapped[float]
#     date: Mapped[str]
#     transaction_type: Mapped[str]
#     category: Mapped[str]
#     account_id: Mapped[int] = mapped_column(ForeignKey('accounts.id'))
#
#     account = relationship("AccountOrm", back_populates="transactions")

# user_table = Table(
#     "users",
#     mapper_registry.metadata,
#     Column("id", Integer, primary_key=True),
#     Column("name", String(50)),
#     Column("login", String(50)),
#     Column("email", String(50)),
#     Column("password", String(50)),
#     Column("balance", float(50))
# )

# mapper_registry.map_imperatively(User, user_table)

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def delete_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)