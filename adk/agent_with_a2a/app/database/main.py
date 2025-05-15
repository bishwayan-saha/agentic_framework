
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from app.models.db_model import Credentials_Master, Base
from dotenv import load_dotenv
from urllib.parse import urlparse
import os
load_dotenv()
 
class Database:

    def __init__(self):   
        

        tmpPostgres = urlparse(os.getenv("DATABASE_URL")) 
        self._engine = create_async_engine(f"postgresql+asyncpg://{tmpPostgres.username}:{tmpPostgres.password}@{tmpPostgres.hostname}{tmpPostgres.path}?ssl=require", echo=True)
        # Base.metadata.create_all(bind=self._engine)
        Session = sessionmaker(bind=self._engine, class_=AsyncSession)
        self._session = Session()

    
    async def get_all_credentials(self):
        result = await self._session.execute(select(Credentials_Master))
        return result.scalars().all()
    



    
