from http import HTTPStatus

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from schema.schemas import HTML_HELLO, Message

app = FastAPI(title='MINHA API')


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Hello world!'}


@app.get('/hello', status_code=HTTPStatus.OK, response_class=HTMLResponse)
def hello():
    return HTML_HELLO
