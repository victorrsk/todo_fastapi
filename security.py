from pwdlib import PasswordHash

pwd_context = PasswordHash.recommended()


def get_pwd_hash(pwd: str):
    return pwd_context.hash(pwd)


def verify_pwd(plain_pwd: str, hashed_pwd: str):
    return pwd_context.verify(plain_pwd, hashed_pwd)
