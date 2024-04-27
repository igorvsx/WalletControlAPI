from fastapi import APIRouter, Depends, Request, Body, HTTPException, Path
from schemas import SUserAdd, SUser, SAccountAdd, SAccount, STransactionAdd, STransaction
from repository import UserRepository, AccountRepository, TransactionRepository
from typing import Annotated
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
        "balance": user.balance,
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
        "balance": user.balance,
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
        "balance": user.balance,
        "code": user.code,
        "id": user.id
    }

@accountRouter.get("/user/{user_id}")
async def get_accounts_by_user_id(user_id: int) -> list[SAccount]:
    accounts = await AccountRepository.get_accounts_by_user_id(user_id)
    if not accounts:
        raise HTTPException(status_code=404, detail="Счета для пользователя с данным идентификатором не найдены")
    return accounts

@accountRouter.post("/add")
async def add_account(
        data: SAccountAdd = Body(...)
):
    account = await AccountRepository.add_account(data)

@accountRouter.get("")
async def get_accounts() -> list[SAccount]:
    accounts = await AccountRepository.get_accounts()
    return accounts

@transactionRouter.get("")
async def get_transactions() -> list[STransaction]:
    transactions = await TransactionRepository.get_transactions()
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