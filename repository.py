from fastapi import HTTPException
from sqlalchemy import select, update, delete

# from database import new_session, UserOrm
from database import new_session
from database import UserOrm, AccountOrm
from schemas import SUserAdd, SUser, SAccount, SAccountAdd

class UserRepository:
    @classmethod
    async def add_user(cls, data: SUserAdd) -> int:
        async with new_session() as session:
            user_dict = data.model_dump()

            user = UserOrm(name=data.name, email=data.email, login=data.login, balance=data.balance, password=data.password, code=data.code)
            session.add(user)
            await session.flush()
            await session.commit()
            # Преобразование объекта пользователя в словарь
            user_data = {
                "name": user.name,
                "login": user.login,
                "email": user.email,
                "password": user.password,
                "balance": user.balance,
                "code": user.code
            }

            return user_data

    @classmethod
    async def get_users(cls) -> list[SUser]:
        async with new_session() as session:
            query = select(UserOrm)
            result = await session.execute(query)
            user_models = result.scalars().all()
            user_schemas = [SUser.model_validate(user_model) for user_model in user_models]
            return user_schemas

    @classmethod
    async def get_user_by_email(cls, email):
        async with new_session() as session:
            query = select(UserOrm).where(UserOrm.email == email)
            result = await session.execute(query)
            user_model = result.scalar()
            if user_model:
                user_schema = SUser.model_validate(user_model)
                return user_schema
            else:
                return None

    @classmethod
    async def get_user_by_login(cls, login):
        async with new_session() as session:
            query = select(UserOrm).where(UserOrm.login == login)
            result = await session.execute(query)
            user_model = result.scalar()
            if user_model:
                user_schema = SUser.model_validate(user_model)
                return user_schema
            else:
                return None

    @classmethod
    async def update_password(cls, email: str, new_password: str):
        async with new_session() as session:
            query = select(UserOrm).where(UserOrm.email == email)
            result = await session.execute(query)
            user_model = result.scalar()
            if user_model:
                user_model.password = new_password
                await session.commit()
                return True
            else:
                return False

    @classmethod
    async def update_verification_code(cls, email: str, new_code: str):
        async with new_session() as session:
            query = select(UserOrm).where(UserOrm.email == email)
            result = await session.execute(query)
            user_model = result.scalar()
            if user_model:
                user_model.code = new_code
                await session.commit()
                return True
            else:
                return False

class AccountRepository:
    @classmethod
    async def add_account(cls, data: SAccountAdd) -> dict:
        async with new_session() as session:
            account = AccountOrm(**data.dict())
            session.add(account)
            await session.flush()
            await session.commit()
            return account

    @classmethod
    async def update_account(cls, account_id: int, data: SAccountAdd) -> bool:
        async with new_session() as session:
            query = update(AccountOrm).where(AccountOrm.id == account_id).values(**data.dict())
            result = await session.execute(query)
            await session.commit()
            return result.rowcount > 0

    @classmethod
    async def delete_account(cls, account_id: int) -> bool:
        async with new_session() as session:
            query = delete(AccountOrm).where(AccountOrm.id == account_id)
            result = await session.execute(query)
            await session.commit()
            return result.rowcount > 0

    @classmethod
    async def get_accounts_by_user_id(cls, user_id: int) -> list[AccountOrm]:
        async with new_session() as session:
            query = select(AccountOrm).where(AccountOrm.user_id == user_id)
            result = await session.execute(query)
            accounts = result.scalars().all()
            return accounts

    @classmethod
    async def get_accounts(cls) -> list[SAccount]:
        async with new_session() as session:
            query = select(AccountOrm)
            result = await session.execute(query)
            accounts_models = result.scalars().all()
            account_schemas = [SAccount.model_validate(account_models) for account_models in accounts_models]
            return account_schemas
