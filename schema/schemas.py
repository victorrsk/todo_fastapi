from pydantic import BaseModel, EmailStr


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
