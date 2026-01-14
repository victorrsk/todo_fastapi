from jwt import decode

from security import ALGORITHM, SECRET_KEY, create_access_token


def test_token_creation():
    data = {'test': 'test'}
    token = create_access_token(data)
    decoded = decode(jwt=token, key=SECRET_KEY, algorithms=ALGORITHM)

    assert decoded['test'] == data['test']
    assert 'exp' in decoded.keys()
