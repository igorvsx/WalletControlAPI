from fastapi import APIRouter, Depends, Request, Body, HTTPException, Path
from schemas import (SUserAdd, SUser, SAccountAdd, SAccount, STransactionAdd, STransaction, SCategoryAdd, SCategory,
                     SFinancialGoalAdd, SFinancialGoal)
from repository import (UserRepository, AccountRepository, TransactionRepository, CategoryRepository,
                        FinancialGoalRepository)
from typing import Annotated, Dict
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Функция генерации случайного кода из 4 цифр
def generate_verification_code():
    return ''.join(random.choices(string.digits, k=4))

# Функция отправки письма с кодом на почту
async def send_verification_code(email: str, code: str):
    smtp_server = 'smtp.yandex.ru'
    port = 587
    sender_email = 'walletcontrol@yandex.ru'
    password = 'muchygfsxratlrny'

    server = smtplib.SMTP(smtp_server, port)
    server.starttls()

    server.login(sender_email, password)

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = email
    message['Subject'] = 'Запрос на восстановление пароля'

    body = f'Ваш код подтверждения: {code}'
    message.attach(MIMEText(body, 'plain'))

    server.sendmail(sender_email, email, message.as_string())

    server.quit()

router = APIRouter(
    prefix="/users",
    tags=["Пользователи"],
)

accountRouter = APIRouter(
    prefix="/accounts",
    tags=["Аккаунты"],
)

transactionRouter = APIRouter(
    prefix="/transactions",
    tags=["Транзакции"],
)

categoryRouter = APIRouter(
    prefix="/categories",
    tags=["Категории"],
)

financialGoalRouter = APIRouter(
    prefix="/financial-goals",
    tags=["Финансовые цели"],
)

@router.post("/add")
async def add_user(
        # user: Annotated[SUserAdd, Depends()],
        data: SUserAdd = Body(...)
):
    userEmail = await UserRepository.get_user_by_email(data.email)
    userLogin = await UserRepository.get_user_by_login(data.login)
    if userEmail:
        raise HTTPException(status_code=400, detail="Пользователь с почтой " + userEmail.email + " зарегистрирован")
    if userLogin:
        raise HTTPException(status_code=400, detail="Пользователь с логином " + userLogin.login + " зарегистрирован")

    user = await UserRepository.add_user(data)

    return user

@router.get("")
async def get_users() -> list[SUser]:
    users = await UserRepository.get_users()
    return users

# Эндпоинт для запроса восстановления пароля
@router.post("/password/recovery")
async def request_password_recovery(data: SUserAdd = Body(...)):
    # Проверяем, есть ли пользователь с такой почтой в базе данных
    user = await UserRepository.get_user_by_email(data.email)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь с такой почтой не найден")

    # Генерируем код и отправляем его на почту пользователя
    verification_code = generate_verification_code()
    user.code = verification_code
    await UserRepository.update_verification_code(user.email, user.code)

    await send_verification_code(data.email, verification_code)

    # Возвращаем код для последующей проверки
    # return {"verification_code": verification_code}
    return {
        "name": user.name,
        "login": user.login,
        "email": user.email,
        "password": user.password,
        "code": user.code
    }

# Эндпоинт для сброса пароля
@router.post("/password/reset")
async def reset_password(data: SUserAdd = Body(...)):
    # # Проверяем, есть ли пользователь с такой почтой в базе данных
    user = await UserRepository.get_user_by_email(data.email)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь с такой почтой не найден")

    # Проверяем, совпадает ли код пользователя с тем, который был отправлен на почту
    if data.code != user.code:
        raise HTTPException(status_code=400, detail="Неверный код верификации")

    # Обновляем пароль пользователя
    await UserRepository.update_password(data.email, data.password)

    return {"message": "Пароль успешно изменен"}

@router.get("/info/{login}")
async def get_user_by_login(login: str) -> SUser:
    user = await UserRepository.get_user_by_login(login)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь с таким логином не найден")

    return {
        "name": user.name,
        "login": user.login,
        "email": user.email,
        "password": user.password,
        "code": user.code,
        "id": user.id
    }

@router.get("/info/email/{email}")
async def get_user_by_email(email: str) -> SUser:
    user = await UserRepository.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь с такой почтой не найден")

    return {
        "name": user.name,
        "login": user.login,
        "email": user.email,
        "password": user.password,
        "code": user.code,
        "id": user.id
    }

@accountRouter.get("/user/{user_id}")
async def get_accounts_by_user_id(user_id: int) -> list[SAccount]:
    accounts = await AccountRepository.get_accounts_by_user_id(user_id)
    if not accounts:
        raise HTTPException(status_code=404, detail="Счета для пользователя с данным идентификатором не найдены")
    return accounts
@accountRouter.get("/user/detail/{account_id}")
async def get_account_by_id(account_id: int) -> SAccount:
    account = await AccountRepository.get_account_by_id(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Счет для пользователя с данным идентификатором не найден")
    return account

@accountRouter.post("/add")
async def add_account(
        data: SAccountAdd = Body(...)
):
    account = await AccountRepository.add_account(data)

@accountRouter.get("")
async def get_accounts() -> list[SAccount]:
    accounts = await AccountRepository.get_accounts()
    return accounts

@accountRouter.get("/total_balance/user/{user_id}")
async def get_total_balance(user_id: int):
    total_balance = await AccountRepository.get_total_balance(user_id)
    return {"total_balance": total_balance}

@accountRouter.delete("/user/delete/{account_id}")
async def delete_account(account_id: int):
    try:
        result = await AccountRepository.delete_account(account_id)
        return result
    except NoResultFound as e:
        raise HTTPException(status_code=404, detail=str(e))

@accountRouter.put("/update/{account_id}")
async def update_account(account_id: int,
        data: SAccountAdd = Body(...)):
    try:
        updated_account = await AccountRepository.update_account(account_id, data)
        return {"message": "Account updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update transaction: {str(e)}")


@transactionRouter.get("")
async def get_transactions() -> list[STransaction]:
    transactions = await TransactionRepository.get_transactions()
    return transactions

@transactionRouter.get("/account/{account_id}/income/{income}")
async def get_transactions_by_account_id_and_income(account_id: int, income: bool):
    transactions = await TransactionRepository.get_transactions_income(account_id, income)
    if not transactions:
        raise HTTPException(status_code=404, detail="Транзакции для счета с данным идентификатором не найдены")
    return transactions

@transactionRouter.get("/account/{account_id}")
async def get_transactions_by_account_id(account_id: int) -> list[STransaction]:
    transactions = await TransactionRepository.get_transactions_by_account_id(account_id)
    if not transactions:
        raise HTTPException(status_code=404, detail="Транзакции для счета с данным идентификатором не найдены")
    return transactions

@transactionRouter.post("/add")
async def add_transactions(
        data: STransactionAdd = Body(...)
):
    transaction = await TransactionRepository.add_transaction(data)

@transactionRouter.get("/detail/{transaction_id}")
async def get_transaction_by_id(transaction_id: int) -> STransactionAdd:
    transaction = await TransactionRepository.get_transaction_by_id(transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Транзакция не найдена")
    return STransaction.model_validate(transaction)

@transactionRouter.delete("/delete/{transaction_id}")
async def delete_transaction(transaction_id: int):
    await TransactionRepository.delete_transaction_by_id(transaction_id)
    return {"message": "Transaction deleted successfully"}

@transactionRouter.put("/update/{transaction_id}")
async def update_transaction(transaction_id: int,
        data: STransactionAdd = Body(...)
):
    try:
        updated_transaction = await TransactionRepository.update_transaction(transaction_id, data)
        return {"message": "Transaction updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update transaction: {str(e)}")

# @transactionRouter.get("/user/{user_id}/income")
# async def get_all_income_transactions_by_user_id(user_id: int) -> list[STransaction]:
#     transactions = await TransactionRepository.get_income_transactions_sum_by_category(user_id)
#     if not transactions:
#         raise HTTPException(status_code=404, detail="Доходные транзакции для пользователя с данным идентификатором не найдены")
#     return transactions

@transactionRouter.get("/user/{user_id}/income/{day}", response_model=Dict[str, float])
async def get_income_transactions_sum_by_category(user_id: int, day: str):
    transactions_sum_by_category = await TransactionRepository.get_income_transactions_sum_by_category(user_id, day)
    if not transactions_sum_by_category:
        raise HTTPException(status_code=404,
                            detail="Доходные транзакции для пользователя с данным идентификатором не найдены")
    return transactions_sum_by_category

@transactionRouter.get("/user/{user_id}/expense/{day}", response_model=Dict[str, float])
async def get_expense_transactions_sum_by_category(user_id: int, day: str) -> list[STransaction]:
    transactions_sum_by_category = await TransactionRepository.get_expense_transactions_sum_by_category(user_id, day)
    if not transactions_sum_by_category:
        raise HTTPException(status_code=404,
                            detail="Расходные транзакции для пользователя с данным идентификатором не найдены")
    return transactions_sum_by_category



@categoryRouter.post("/add")
async def add_category(
        data: SCategoryAdd = Body(...)
):
    category = await CategoryRepository.add_category(data)

@categoryRouter.get("")
async def get_categories() -> list[SCategory]:
    categories = await CategoryRepository.get_categories()
    return categories

@categoryRouter.delete("/delete/{category_id}")
async def delete_category(category_id: int):
    try:
        result = await CategoryRepository.delete_category(category_id)
        return result
    except NoResultFound as e:
        raise HTTPException(status_code=404, detail=str(e))

@financialGoalRouter.post("/add")
async def add_financial_goal(
        data: SFinancialGoalAdd = Body(...)
):
    financial_goal = await FinancialGoalRepository.add_financial_goal(data)

@financialGoalRouter.get("")
async def get_financial_goals() -> list[SFinancialGoal]:
    financial_goals = await FinancialGoalRepository.get_financial_goals()
    return financial_goals

@financialGoalRouter.get("/{user_id}/{is_done}")
async def get_financial_goals_by_user_id(user_id: int, is_done: bool) -> list[SFinancialGoal]:
    financial_goals = await FinancialGoalRepository.get_financial_goals_by_user_id(user_id, is_done)
    return financial_goals


@financialGoalRouter.get("/detail/{financial_goal_id}", response_model=SFinancialGoal)
async def get_financial_goal_by_id(financial_goal_id: int) -> SFinancialGoal:
    print(f"Запрошенный ID финансовой цели: {financial_goal_id}")

    financial_goal = await FinancialGoalRepository.get_financial_goal_by_id(financial_goal_id)

    if not financial_goal:
        raise HTTPException(status_code=404, detail="Финансовая цель не найдена")

    print(f"Полученные данные: {financial_goal}")

    return SFinancialGoal.model_validate(financial_goal)

@financialGoalRouter.put("/update/{financial_goal_id}")
async def update_financial_goal(financial_goal_id: int,
        data: SFinancialGoalAdd = Body(...)):
    try:
        updated_financial_goal = await FinancialGoalRepository.update_financial_goal(financial_goal_id, data)
        return {"message": "Financial goal updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update financial goal: {str(e)}")

@financialGoalRouter.delete("/delete/{financial_goal_id}")
async def delete_financial_goal(financial_goal_id: int):
    try:
        result = await FinancialGoalRepository.delete_financial_goal(financial_goal_id)
        return result
    except NoResultFound as e:
        raise HTTPException(status_code=404, detail=str(e))

