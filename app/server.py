from fastapi import FastAPI, status, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())

from app.db import game_collection, user_collection
from app.request.User import NewUser

app = FastAPI()
async def custom_404_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return JSONResponse(
            status_code=404,
            content={"message": "The requested resource was not found"},
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )

app.add_exception_handler(StarletteHTTPException, custom_404_handler)

@app.get('/')
async def index():
    return JSONResponse(
        status_code=200,
        content={"message": "Server is online"},
    )

@app.get("/user/")
def get_all_users():
    users = list(user_collection.find({}))
    for user in users:
        del user["_id"]
    return JSONResponse(
        content=users,
        status_code=status.HTTP_200_OK
    )

@app.get("/user/{id}")
def get_user_by_id(id: str):
    user = user_collection.find_one({ "telegram_id": id })
    if user == None:
        return JSONResponse(
            content={ "err": "User not existed" }, 
            status_code=status.HTTP_404_NOT_FOUND
        )
    else:
        del user["_id"]
        return JSONResponse(
            content=user,
            status_code=status.HTTP_200_OK
        )

@app.post("/user")
async def add_user(new_user: NewUser):
    try:
        existing_user = user_collection.find_one({
            'telegram_id': new_user.telegram_id
        }) or None

        if existing_user != None:
            return JSONResponse(
                { 'err': 'user already existed'}, 
                status_code=status.HTTP_400_BAD_REQUEST
            )
        added_user = {
            "telegram_id": new_user.telegram_id,
            "referred_by": "null",
            "sp": 0
        }
        if new_user.referred_by != 'null':
            referrence_user = user_collection.find_one({
                'telegram_id': new_user.referred_by
            }) or None
            if referrence_user == None:
                return JSONResponse(            
                    { 'err': 'referrence user not existed'}, 
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            else:
                added_user['referred_by'] = new_user.referred_by 

        user_collection.insert_one(added_user)

        return JSONResponse(content={
            "telegram_id": new_user.telegram_id,
            "referred_by": new_user.referred_by,
            "sp": 0
        }, status_code=status.HTTP_201_CREATED)

    except Exception as e:
        print(e.__dict__)
        return JSONResponse("Server corrupted", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.get("/save/{id}")
def get_user_by_id(id: str):
    save = game_collection.find_one({ "user": id })
    if save == None:
        return JSONResponse(
            content={ "err": "User not existed" }, 
            status_code=status.HTTP_404_NOT_FOUND
        )
    else:
        del save["_id"]
        return JSONResponse(
            content=save,
            status_code=status.HTTP_200_OK
        )


@app.put('/save')
async def save_game(request: Request):
    body = await request.json()
    if not body['user']:
        return JSONResponse({
            "err": "user id is required"
        }, status_code=status.HTTP_400_BAD_REQUEST)
    
    user = user_collection.find_one({
        'telegram_id': body["user"]
    }) or None
    
    if user == None:
        return JSONResponse({
            "err": "user not existed"
        }, status_code=status.HTTP_400_BAD_REQUEST)
        
    game_save = game_collection.find_one({ 
        'user': user['telegram_id']
    })

    if game_save == None:
        game_collection.insert_one(body).inserted_id
    else:
        game_collection.replace_one(
            filter={ 'user': body["user"] },
            replacement=body
        )
    
    new_record = game_collection.find_one({ 'user': user['telegram_id'] })
    
    del new_record['_id']
    
    return JSONResponse(content=new_record, status_code=status.HTTP_201_CREATED)

# Custom exception handler middleware
@app.middleware("http")
async def custom_exception_handler(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": "An unexpected error occurred.", "details": str(e)},
        )