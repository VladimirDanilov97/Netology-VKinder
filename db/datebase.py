from sqlalchemy import create_engine, insert, MetaData
from db.model import users, blacklist, favorite


class DataBaseConnection():
    def __init__(self, db_name='db.db'):
        self.engine = create_engine(f'sqlite:///{db_name}')


    def is_user_registered(self, user_id: int) -> bool:
        stmt = users.select().where(users.c.user_id == user_id)
        response = []
        with self.engine.connect() as con:
            response = list(con.execute(stmt))
        if response:
            return True
        else:
            return False


    def register_user(self, user_id, city_id, sex_id) -> None:
        stmt = users.insert().values(
            user_id=user_id, 
            city_id=city_id, 
            sex=sex_id
            )
        with self.engine.connect() as con:
            con.execute(stmt)
