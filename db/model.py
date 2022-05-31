from curses import meta
from email.policy import default
from sqlalchemy import MetaData, Table, Column, Integer, String, create_engine

metadata = MetaData()
engine = create_engine('postgresql://vkinder:vkinder@localhost:5432/vkinder')

users = Table('users', metadata,
    Column('user_id', Integer, primary_key=True),
    Column('city_id', Integer),
    Column('sex', Integer)
    )

blacklist = Table('black_list', metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', Integer),
    Column('blocked_user_id', Integer)
    )

favorite = Table('favorite_list', metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', Integer),
    Column('favorite_user_id', Integer)
    )

user_state_machine = Table('user_state_machine', metadata,
    Column('user_id', Integer, primary_key=True),
    Column('state', String(80), default='None'),
    Column('offset', Integer)
    )

user_search_params = Table('user_search_params', metadata,
    Column('user_id', Integer, primary_key=True),
    Column('city_id', Integer, default=1),
    Column('sex_id', Integer, default=1),
    Column('age', Integer, default=20)
)

if __name__ == '__main__':
    metadata.create_all(engine)