from pydantic import BaseModel, ConfigDict

class SUserAdd(BaseModel):
    name: str
    login: str
    email: str
    password: str
    balance: float
    code: str

class SUser(SUserAdd):
    id: int

    model_config = ConfigDict(from_attributes=True)

class SAccountAdd(BaseModel):
    name: str
    balance: float
    user_id: int

class SAccount(SAccountAdd):
    id: int

    model_config = ConfigDict(from_attributes=True)

class STransactionAdd(BaseModel):
    name: str
    description: str
    amount: float
    date: str
    transaction_type: str
    category: str
    account_id: int

class STransaction(STransactionAdd):
    id: int

    model_config = ConfigDict(from_attributes=True)