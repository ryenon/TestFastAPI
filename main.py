from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel
from fastapi import Header
from fastapi import HTTPException
from fastapi import Request
from fastapi.responses import JSONResponse
import datetime
import asyncio
import time

api = FastAPI(
    title = "My API",
    description="My own API powered by FastAPI",
    version="1.0.1",
    openapi_tags=[
        {
            'name':'home',
            'description': 'default functions'
        },
        {
            'name': 'items',
            'description': 'functions that are used to deal with items'
        }
    ]
)

users_db = [
    {
        'user_id': 1,
        'name': 'Alice',
        'subscription': 'free tier'
    },
    {
        'user_id': 2,
        'name': 'Bob',
        'subscription': 'premium tier'
    },
    {
        'user_id': 3,
        'name': 'Clementine',
        'subscription': 'free tier'
    }
]

data = [1, 2, 3, 4, 5]

@api.get('/data', name='Data access')
def get_data(index):
    try:
        return {
            'data': data[int(index)]
        }
    except IndexError:
        raise HTTPException(
            status_code = 404,
            detail = 'Unknow Index'
        )
    except ValueError:
        raise HTTPException(
            status_code = 400,
            detail = 'Bad Type'
        )

@api.get("/", name="API Endpoint home users")
def get_users():
    return {'data': 'Bienvenue API Users'}

@api.get('/users')
def get_users_all():
    return users_db

@api.get('/users/{userid:int}')
def get_users_userid(userid):
    try:
        user = list(filter(lambda x: x.get('user_id') == userid, users_db))[0]
        return user
    except IndexError:
        return {}
    
@api.get('/users/{userid:int}/name')
def get_user_name(userid):
    try:
        user = list(filter(lambda x: x.get('user_id') == userid, users_db))[0]
        return {'name': user['name']}
    except IndexError:
        return {}
    
@api.get('/users/{userid:int}/description')
def get_user_description(userid):
    try:
        user = list(filter(lambda x: x.get('user_id') == userid, users_db))[0]
        return {'Description': user['description']}
    except IndexError:
        return {}

@api.get("/", tags=['home'])
def get_index():
    """
    Docstring pour get_index
    return greetings
    """
    return {'greetings': 'Hello World!'}

@api.get("/item/{itemid}/description/{language}")
def get_item_language(itemid, language):
    if language == 'fr':
        return {'itemid': itemid, 
            'description': 'un objet',
            'language': 'fr'}
    else:
        return {'itemid': itemid,
                'description': 'an objet',
                'language': 'en'}
    
@api.get("/item/{itemid:int}")
def get_item(itemid):
    return {
        'route': 'dynamic',
        'itemid': itemid
    }

@api.get('/item/{itemid:float}')
def get_item_float(itemid):
    return {
        'route': 'dynamic',
        'itemid': itemid,
        'source': 'float'
    }

@api.get('/item/{itemid}')
def get_item_default(itemid):
    return {
        'route': 'dynamic',
        'itemid': itemid,
        'source': 'string'
    }

#  Chaine de requete
@api.get('/typed')
def get_typed(argument1: int):
    return {'data': argument1 + 1}

@api.get('/addition')
def get_addition(a: int, b: Optional[int]=None):
    if b:
        result = a + b
    else:
        result = a + 1
    return {
        'Addition_result': result
    }

# Corps de la requête
class Item(BaseModel):
    itemid: int
    description: str
    owner: Optional[str] = None

@api.get('/items', tags=['home', 'items'])
def get_items():
    """
    Docstring pour get_items
    returns an item
    """
    return {
        'item': 'some item'
    }

@api.post('/item')
def post_item(item: Item):
    return {'itemid': item.itemid}

class User(BaseModel):
    userid: Optional[int]
    name: str
    subcription: str

@api.put('/users')
def put_users(user: User):
    new_id = max(users_db, key=lambda u: u.get('user_id'))['user_id']
    new_user = {
        'user_id': new_id + 1,
        'name': user.name,
        'subscription': user.subcription
    }
    users_db.append(new_user)
    return new_user

@api.post('/users/{userid:int}')
def post_users(user: User, userid):
    try:
        old_user = list(
            filter(lambda x: x.get('user_id') == userid, users_db)
        )[0]
        users_db.remove(old_user)

        old_user['name'] = user.name
        old_user['description'] = user.subcription

        users_db.append(old_user)
        return old_user
    except IndexError:
        return {}

@api.delete('/users/{userid:int}')
def delete_users(userid):
    try:
        old_user = list(
            filter(lambda x: x.get('user_id') == userid, users_db)
        )[0]
        users_db.remove(old_user)
        return {
            'userid': userid,
            'deleted': True
        }
    except IndexError:
        return {}
    
# Les entêtes
@api.get('/headers')
def get_headers(user_agent=Header(None)):
    return {
        'User-Agent': user_agent
    }

# Documentation des corps des fonctions
class Computer(BaseModel):
    """
    Docstring pour Computer
    A computer that is available in the store
    """
    computerid: int
    cpu: Optional[str]
    gpu: Optional[str]
    price: float

@api.put('/computer', name='Create a new computer')
def get_computer(computer: Computer):
    """
    Docstring pour get_computer
    Create a new computer within the database

    :param computer: Description
    :type computer: Computer
    """
    return computer

@api.get('/custom', name='Get custom header')
def get_content(custom_header: Optional[str] = Header(None, description='My own personal header')):
    return {
        'Custom_header': custom_header
    }

# Organiser la documentation

# Gestion des erreurs
class MyException(Exception):
    def __init__(self, name: str, date: str):
        self.name = name
        self.date = date

@api.exception_handler(Exception)
def MyExceptionHandler(request: Request, exception: MyException):
    return JSONResponse(
        status_code=418,
        content={
            'url': str(request.url),
            'name': exception.name,
            'message': 'This error is my own',
            'date': exception.date
        }
    )

@api.get('/my_custom_exception')
def get_my_custom_exception():
    raise MyException(
        name='my error',
        date=str(datetime.datetime.now())
    )

responses = {
    200: {'description': 'ok'},
    404: {'description': 'Item not found'},
    302: {'description': 'The item was moved'},
    403: {'description': 'Not enough privilege'},
}    

@api.get('/thing', responses=responses)
def get_thing():
    return {
        'data': 'Bonjour tout le monde!!'
    }

# Gestion de la concurence
def wait_sync():
    time.sleep(10)
    return True

async def wait_async():
    await asyncio.sleep(10)
    return True

@api.get('/sync')
def get_sync():
    wait_sync()
    return {
        'message': 'synchronous'
    }

@api.get('/async')
async def get_async():
    wait_async()
    return {
        'message': 'asynchronous'
    }
