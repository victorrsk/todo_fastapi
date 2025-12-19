from pydantic import BaseModel


class Message(BaseModel):
    message: str


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
