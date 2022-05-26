from matplotlib import use
from sqlalchemy import create_engine, insert
from db.model import users, blacklist, favorite, user_state_machine


class DataBaseConnection():
    def __init__(self, db_name='db.db'):
        self.engine = create_engine(f'sqlite:///{db_name}')


    def is_user_registered(self, user_id: int) -> bool:
        stmt = users.select().where(users.c.user_id == user_id)
        with self.engine.connect() as con:
            with con.begin():
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
        with self.engine.connect() as con:
            with con.begin():
                con.execute(stmt)
                con.execute(stmt_2)

    def add_to_black_list(self, user_id, blocked_user_id):
        stmt = blacklist.insert().values(
            user_id=user_id, 
            blocked_user_id=blocked_user_id, 
            )
        with self.engine.connect() as con:
            with con.begin():
                con.execute(stmt)
    
    def is_user_in_black_list(self, user_id, blocked_user_id):
        stmt = blacklist.select().where(blacklist.c.user_id == user_id, blacklist.c.blocked_user_id == blocked_user_id)
        with self.engine.connect() as con:
            with con.begin():
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
            with con.begin():
                con.execute(stmt)
    
    def get_user_state(self, user_id):
        stmt = user_state_machine.select().where(user_state_machine.c.user_id == user_id)
        with self.engine.connect() as con:
            with con.begin():
                response = con.execute(stmt)
                return list(response)[0][1]

    def update_user_state(self, user_id, new_state:str):
        stmt = user_state_machine.update().where(user_state_machine.c.user_id==user_id).values(state=new_state)
        with self.engine.connect() as con:
            with con.begin():
                response = con.execute(stmt)
        

if __name__ == '__main__':
    db = DataBaseConnection()
