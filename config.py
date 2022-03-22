
from pydantic import BaseSettings
from pydantic.main import BaseModel

class DB(BaseModel):
    id : str = "root"
    password : str = "PASSWORD"
    url : str = "mariadb"
    name : str = "idclab"
    port : int = 3306
    
db = DB()

class Config(BaseSettings):
    DB_URL: str = f"mysql+pymysql://{db.id}:{db.password}@{db.url}:{db.port}/{db.name}"
    
def get_config():
    config_type = {
        "production" : Config(),
    }
    return config_type['production']

config = get_config()