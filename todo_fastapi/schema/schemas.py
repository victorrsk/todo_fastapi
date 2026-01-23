from models.models_db import Todo, TodoState
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Message(BaseModel):
    message: str


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr
    # valida os dados via atributos
    model_config = ConfigDict(from_attributes=True)


class UserDB(UserSchema):
    id: int


class UserList(BaseModel):
    users: list[UserPublic]


# html do endpoint "/hello"
HTML_HELLO = """
    <html>
        <head>
            <title>Meu endpoint</title>
        </head>
        <body>
            <h3>Olá Mundo!</h3>
        </body>
    </html>
"""


class TokenSchema(BaseModel):
    access_token: str
    token_type: str


class FilterPage(BaseModel):
    # indica limite de registros por página e de onde começa
    limit: int = 10
    offset: int = 0


class TodoSchema(BaseModel):
    title: str
    description: str
    state: TodoState = Field(default=TodoState.todo)


class TodoPublic(TodoSchema):
    id: int


'''class TodosList(BaseModel):
    todos: list[Todo]
'''