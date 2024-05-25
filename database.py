from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column, relationship
from sqlalchemy import ForeignKey
from typing import List, Optional

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
    code: Mapped[str]

    accounts: Mapped[List["AccountOrm"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    financial_goals: Mapped[List["FinancialGoalOrm"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    budgets: Mapped[List["BudgetOrm"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

class AccountOrm(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    balance: Mapped[float]
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    user = relationship("UserOrm", back_populates="accounts")

    transactions: Mapped[List["TransactionOrm"]] = relationship(
        back_populates="account", cascade="all, delete-orphan"
    )
    budgets: Mapped[List["BudgetOrm"]] = relationship(
        back_populates="account", cascade="all, delete-orphan"
    )

class TransactionOrm(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[str]
    amount: Mapped[float]
    date: Mapped[str]
    income: Mapped[bool]
    account_id: Mapped[int] = mapped_column(ForeignKey('accounts.id'))
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'))

    account = relationship("AccountOrm", back_populates="transactions")
    category = relationship("CategoryOrm", back_populates="transactions")

class CategoryOrm(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    transactions: Mapped[List["TransactionOrm"]] = relationship(
        back_populates="category", cascade="all, delete-orphan"
    )

class FinancialGoalOrm(Base):
    __tablename__ = "financial_goals"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    desc: Mapped[Optional[str]] = mapped_column(nullable=True)
    amount: Mapped[float]
    target_amount: Mapped[float]
    target_date: Mapped[Optional[str]] = mapped_column(nullable=True)
    is_done: Mapped[bool]
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    user = relationship("UserOrm", back_populates="financial_goals")

class BudgetOrm(Base):
    __tablename__ = "budgets"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    amount: Mapped[float]
    wasted: Mapped[float]
    date: Mapped[str]
    target_date: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    account_id: Mapped[int] = mapped_column(ForeignKey('accounts.id'))

    user = relationship("UserOrm", back_populates="budgets")
    account = relationship("AccountOrm", back_populates="budgets")

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