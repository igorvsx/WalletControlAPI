from pydantic import BaseModel, ConfigDict
from typing import Optional

class SUserAdd(BaseModel):
    name: str
    login: str
    email: str
    password: str
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
    income: bool
    account_id: int
    category_id: int

class STransaction(STransactionAdd):
    id: int

    model_config = ConfigDict(from_attributes=True)

class SCategoryAdd(BaseModel):
    name: str

class SCategory(SCategoryAdd):
    id: int

    model_config = ConfigDict(from_attributes=True)

class SFinancialGoalAdd(BaseModel):
    name: str
    desc: Optional[str]
    amount: float
    target_amount: float
    target_date: Optional[str]
    is_done: bool
    user_id: int

class SFinancialGoal(SFinancialGoalAdd):
    id: int

    model_config = ConfigDict(from_attributes=True)

class SBudgetAdd(BaseModel):
    name: str
    amount: float
    wasted: float
    date: str
    target_date: str
    user_id: int
    account_id: int

class SBudget(SBudgetAdd):
    id: int

    model_config = ConfigDict(from_attributes=True)