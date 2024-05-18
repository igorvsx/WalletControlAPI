from fastapi import HTTPException
from sqlalchemy import select, update, delete, func
from sqlalchemy.exc import NoResultFound

# from database import new_session, UserOrm
from database import new_session
from database import UserOrm, AccountOrm, TransactionOrm, CategoryOrm
from schemas import SUserAdd, SUser, SAccount, SAccountAdd, STransaction, STransactionAdd, SCategoryAdd, SCategory

class UserRepository:
    @classmethod
    async def add_user(cls, data: SUserAdd) -> int:
        async with new_session() as session:
            user_dict = data.model_dump()

            user = UserOrm(name=data.name, email=data.email, login=data.login, password=data.password, code=data.code)
            session.add(user)
            await session.flush()
            await session.commit()
            # Преобразование объекта пользователя в словарь
            user_data = {
                "name": user.name,
                "login": user.login,
                "email": user.email,
                "password": user.password,
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

    @classmethod
    async def get_total_balance(cls, user_id: int) -> float:
        async with new_session() as session:
            query = select(func.sum(AccountOrm.balance)).where(AccountOrm.user_id == user_id)
            result = await session.execute(query)
            total_balance = result.scalar()
            return total_balance if total_balance is not None else 0.0

class TransactionRepository:
    @classmethod
    async def add_transaction(cls, data: STransactionAdd) -> dict:
        async with new_session() as session:
            # Создание объекта транзакции
            transaction = TransactionOrm(**data.dict())
            session.add(transaction)

            # Получение счета, связанного с транзакцией
            query = select(AccountOrm).where(AccountOrm.id == data.account_id)
            result = await session.execute(query)
            account = result.scalar()

            if not account:
                raise HTTPException(status_code=404, detail="Account not found")

            # Обновление баланса счета
            if data.income:
                account.balance += data.amount
            else:
                account.balance -= data.amount

            # Сохранение изменений в базе данных
            await session.flush()
            await session.commit()

            return transaction
    # async def add_transaction(cls, data: STransactionAdd) -> dict:
    #     async with new_session() as session:
    #         transaction = TransactionOrm(**data.dict())
    #         session.add(transaction)
    #         await session.flush()
    #         await session.commit()
    #         return transaction

    @classmethod
    async def get_transactions_by_account_id(cls, account_id: int) -> list[TransactionOrm]:
        async with new_session() as session:
            query = select(TransactionOrm).where(TransactionOrm.account_id == account_id)
            result = await session.execute(query)
            transactions = result.scalars().all()
            return transactions

    @classmethod
    async def get_transactions_income(cls, account_id: int, income: bool) -> list[TransactionOrm]:
        async with new_session() as session:
            query = select(TransactionOrm).where(TransactionOrm.account_id == account_id)
            if income:
                query = query.where(TransactionOrm.income == True)  # True для явного указания на поле income == True
            else:
                query = query.where(TransactionOrm.income == False)  # False для явного указания на поле income == False

            result = await session.execute(query)
            transactions_models = result.scalars().all()
            transaction_schemas = [STransaction.model_validate(transaction_models) for transaction_models in
                                   transactions_models]
            return transaction_schemas

    @classmethod
    async def get_transactions(cls) -> list[STransaction]:
        async with new_session() as session:
            query = select(TransactionOrm)
            result = await session.execute(query)
            transactions_models = result.scalars().all()
            transaction_schemas = [STransaction.model_validate(transaction_models) for transaction_models in transactions_models]
            return transaction_schemas

    @classmethod
    async def get_transaction_by_id(cls, transaction_id: int) -> STransactionAdd:
        async with new_session() as session:
            query = select(TransactionOrm).where(TransactionOrm.id == transaction_id)
            result = await session.execute(query)
            transaction = result.scalar()
            return transaction

    @classmethod
    async def delete_transaction_by_id(cls, transaction_id: int):
        async with new_session() as session:
            query = select(TransactionOrm).where(TransactionOrm.id == transaction_id)
            result = await session.execute(query)
            transaction = result.scalar()

            if not transaction:
                raise HTTPException(status_code=404, detail="Transaction not found")

            # Получение счёта, связанного с транзакцией
            query_account = select(AccountOrm).where(AccountOrm.id == transaction.account_id)
            result_account = await session.execute(query_account)
            account = result_account.scalar()

            if not account:
                raise HTTPException(status_code=404, detail="Account not found")

            # Обновление баланса счёта в зависимости от значения income транзакции
            if transaction.income:
                account.balance -= transaction.amount  # Вычитаем сумму транзакции из баланса
            else:
                account.balance += transaction.amount  # Прибавляем сумму транзакции к балансу

            # Удаление транзакции из базы данных
            session.delete(transaction)

            # Сохранение изменений в базе данных
            await session.commit()

    @classmethod
    async def update_transaction(cls, transaction_id: int, updated_data: STransactionAdd) -> dict:
        async with new_session() as session:
            query = select(TransactionOrm).where(TransactionOrm.id == transaction_id)
            result = await session.execute(query)
            transaction = result.scalar()

            if not transaction:
                raise HTTPException(status_code=404, detail="Transaction not found")

            # Получение счёта, связанного с транзакцией
            query_account = select(AccountOrm).where(AccountOrm.id == transaction.account_id)
            result_account = await session.execute(query_account)
            account = result_account.scalar()

            if not account:
                raise HTTPException(status_code=404, detail="Account not found")

            # Вычисление изменения суммы транзакции
            old_amount = transaction.amount
            new_amount = updated_data.amount
            amount_difference = new_amount - old_amount

            # Обновление баланса счёта в зависимости от значения поля income
            if transaction.income:
                # Если доходная транзакция, вычитаем старую сумму и прибавляем новую
                account.balance -= old_amount
                account.balance += new_amount
            else:
                # Если расходная транзакция, прибавляем старую сумму и вычитаем новую
                account.balance += old_amount
                account.balance -= new_amount

            # Обновляем данные транзакции на основе переданных данных
            for field, value in updated_data.dict().items():
                setattr(transaction, field, value)

            # Сохраняем изменения в балансе счёта и транзакции в базе данных
            await session.commit()

            return transaction

class CategoryRepository:
    @classmethod
    async def add_category(cls, data: SCategoryAdd) -> dict:
        async with new_session() as session:
            category = CategoryOrm(**data.dict())
            session.add(category)
            await session.flush()
            await session.commit()
            return category

    @classmethod
    async def get_categories(cls) -> list[SCategory]:
        async with new_session() as session:
            query = select(CategoryOrm)
            result = await session.execute(query)
            categories_models = result.scalars().all()
            category_schemas = [SCategory.model_validate(category_models) for category_models in
                                   categories_models]
            return category_schemas

    @classmethod
    async def delete_category(cls, category_id: int) -> dict:
        async with new_session() as session:
            query = select(CategoryOrm).where(CategoryOrm.id == category_id)
            result = await session.execute(query)
            category = result.scalars().first()

            if category is None:
                raise NoResultFound(f"Category with id {category_id} not found")

            await session.delete(category)
            await session.commit()
            return {"message": "Category deleted successfully", "category_id": category_id}
