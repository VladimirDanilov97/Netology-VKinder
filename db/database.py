from sqlalchemy import create_engine, select
from db.model import *


class DataBaseConnection():


    def __init__(self, db_name='vkinder', password='vkinder', user='vkinder'):
        self.engine = create_engine(f'postgresql://vkinder:vkinder@localhost:5432/{db_name}')


    def is_user_registered(self, user_id: int) -> bool:
        stmt = users.select().where(users.c.user_id == user_id)
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
        stmt_2 = user_state_machine.insert().values(
            user_id=user_id, 
            )
        stmt_3 = user_search_params.insert().values(
            user_id=user_id,
        )
        with self.engine.connect() as con:
            con.execute(stmt)
            con.execute(stmt_2)
            con.execute(stmt_3)


    def add_to_black_list(self, user_id, blocked_user_id):
        stmt = blacklist.insert().values(
            user_id=user_id, 
            blocked_user_id=blocked_user_id, 
            )
        with self.engine.connect() as con:
            con.execute(stmt)
    

    def is_user_in_black_list(self, user_id, blocked_user_id): 
        stmt = blacklist.select().where(blacklist.c.user_id == user_id, blacklist.c.blocked_user_id == blocked_user_id)
        with self.engine.connect() as con:
            response = list(con.execute(stmt))
            if response:
                return True
            return False


    def add_to_favorite_list(self, user_id, favorite_user_id):
        stmt = favorite.insert().values(
            user_id=user_id, 
            favorite_user_id=favorite_user_id, 
            )
        with self.engine.connect() as con:
            con.execute(stmt)
    

    def get_favorite_list(self, user_id):
        stmt = select(favorite.c.favorite_user_id).where(
            user_id == user_id, 
            )
        with self.engine.connect() as con:
            response = list(con.execute(stmt))
            favorite_list = [i[0] for i in response]
            return favorite_list


    def get_user_state(self, user_id):
        stmt = select(user_state_machine.c.state).where(user_state_machine.c.user_id == user_id)
        with self.engine.connect() as con:
            response = list(con.execute(stmt))
            if response:
                return response[0][0]
            else:
                return 'None'


    def update_user_state(self, user_id, new_state:str):
        stmt = user_state_machine.update().where(user_state_machine.c.user_id==user_id).values(state=new_state)
        with self.engine.connect() as con:
            response = con.execute(stmt)
            return new_state
    

    def get_user_offset(self, user_id):
        stmt = select(user_state_machine.c.offset).where(user_state_machine.c.user_id==user_id)
        with self.engine.connect() as con:
            response = list(con.execute(stmt))
            return response[0][0]


    def update_user_offset(self, user_id, new_offset):
        stmt = user_state_machine.update().where(user_state_machine.c.user_id==user_id).values(offset=new_offset)
        with self.engine.connect() as con:
            response = con.execute(stmt)
            return response
    
    def get_search_params(self, user_id):
        stmt = user_search_params.select().where(user_search_params.c.user_id==user_id)
        with self.engine.connect() as con:
            response = list(con.execute(stmt))
            search_params = {
                'city_id': int(response[0][1]),
                'sex_id': int(response[0][2]),
                'age': int(response[0][3]),
            }
            return search_params
    

    def update_search_params(self, user_id, city_id, sex_id, age: dict):
        stmt = user_search_params.update().where(user_search_params.c.user_id==user_id).values(
            city_id=city_id,
            sex_id=sex_id,
            age=age,
        )
        with self.engine.connect() as con:
            response = con.execute(stmt)
            return response


if __name__ == '__main__':
    db = DataBaseConnection()
   