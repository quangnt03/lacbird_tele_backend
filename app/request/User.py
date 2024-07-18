from pydantic import BaseModel

class NewUser(BaseModel):
    telegram_id: str
    referred_by: str = 'null'