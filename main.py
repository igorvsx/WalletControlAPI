from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn

from database import create_tables, delete_tables
from router import router as user_router
from router import accountRouter as account_router
from router import transactionRouter as transaction_router
from router import categoryRouter as category_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # await delete_tables()
    # print("База очищена")
    # await create_tables()
    # print("База готова")
    yield
    print("Выключение")

app = FastAPI(lifespan=lifespan)
app.include_router(user_router)
app.include_router(account_router)
app.include_router(transaction_router)
app.include_router(category_router)

if __name__ == "__main__":
    uvicorn.run(app, host="192.168.0.115", port=8000)

