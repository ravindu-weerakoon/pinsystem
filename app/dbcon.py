from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv
import asyncio
import aiomysql
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from tenacity import retry, stop_after_attempt, wait_fixed


# from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
# from sqlalchemy.ext.declarative import declarative_base
# import os
# from dotenv import load_dotenv
# import aiomysql

# # Load environment variables from .env file
# load_dotenv()


# Base = declarative_base()


# async def connect_to_db(app):
#     db_user = os.environ.get('MYSQL_USER')
#     db_password = os.environ.get('MYSQL_PASSWORD')
#     db_host = os.environ.get('MYSQL_HOST', 'localhost')
#     db_port = os.environ.get('MYSQL_PORT', '3306')
#     db_name = os.environ.get('MYSQL_DATABASE')

#     async_engine = create_async_engine(
#         f'mysql+aiomysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}', future=True, echo=True)
#     async with async_engine.connect() as conn:
#         async with conn.begin():
#             await conn.run_sync(Base.metadata.create_all)
#     db = async_sessionmaker(
#         async_engine, class_=AsyncSession, expire_on_commit=False)

#     # try:
#     #     yield db
#     # finally:
#     #     await db.close()

#     return db

async def connect_to_db(app):
    db_user = os.environ.get('MYSQL_USER')
    db_password = os.environ.get('MYSQL_PASSWORD')
    db_host = os.environ.get('MYSQL_HOST', 'localhost')
    db_port = os.environ.get('MYSQL_PORT', '3306')
    db_name = os.environ.get('MYSQL_DATABASE')

    async with aiomysql.create_pool(host=db_host, port=int(db_port), user=db_user, password=db_password, db=db_name) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('SELECT 1')
                result = await cursor.fetchone()
                print(result)

        async_engine = create_async_engine(
            f'mysql+aiomysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}', pool_size=10, max_overflow=0)
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        db = async_sessionmaker(
            async_engine, class_=AsyncSession, expire_on_commit=False)
        return db


# import create_engine from sqlalchemy


# Load environment variables from .env file
load_dotenv()


Base = declarative_base()


# class AsyncDatabaseSession:
#     def __init__(self):
#         self._session = None
#         self._engine = None

#     def __getattr__(self, name):
#         return getattr(self._session, name)

#     async def init(self):
#         db_user = os.environ.get('MYSQL_USER')
#         db_password = os.environ.get('MYSQL_PASSWORD')
#         db_host = os.environ.get('MYSQL_HOST', 'localhost')
#         db_port = os.environ.get('MYSQL_PORT', '3306')
#         db_name = os.environ.get('MYSQL_DATABASE')

#         self._engine = create_async_engine(
#             f'mysql+aiomysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}',
#             echo=True,
#         )

#         async with self._engine.begin() as conn:
#             await conn.run_sync(Base.metadata.create_all)

#         self._session = async_sessionmaker(
#             self._engine, class_=AsyncSession, expire_on_commit=False
#         )()
#         return self._session





@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def create_pool():

    db_user = os.environ.get('MYSQL_USER')
    db_password = os.environ.get('MYSQL_PASSWORD')
    db_host = os.environ.get('MYSQL_HOST', 'localhost')
    db_port = os.environ.get('MYSQL_PORT', '3306')
    db_name = os.environ.get('MYSQL_DATABASE')
    pool = await aiomysql.create_pool(host=db_host, port=int(db_port),
                                      user=db_user, password=db_password,
                                      db=db_name, autocommit=False)
    return pool


# async def get_async_db_session():
#     if not async_db_session._session:
#         await async_db_session.init()
#     return async_db_session._session


# print(type(get_async_db_session()))
