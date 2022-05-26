from curses import meta
from sqlalchemy import ForeignKey, MetaData, PrimaryKeyConstraint, Table, Column, Integer, String, create_engine, JSON

metadata = MetaData()
engine = create_engine('postgresql://vkinder:vkinder@localhost:5432/vkinder')

users = Table('users', metadata,
    Column('user_id', Integer, primary_key=True),
    Column('city_id', Integer),
    Column('sex', Integer)
    )

blacklist = Table('black_list', metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', Integer, ForeignKey('users.user_id')),
    Column('blocked_user_id', Integer)
    )

favorite = Table('favorite_list', metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', Integer),
    Column('favorite_user_id', Integer)
    )

user_state_machine = Table('user_state_machine', metadata,
    Column('user_id', Integer, primary_key=True),
    Column('state', String(80), default='None')
    )

user_search_params = Table('user_search_params', metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', Integer, ForeignKey('users.user_id')),
    Column('city_id', Integer),
    Column('sex_id', Integer),
    Column('age', Integer)
)

if __name__ == '__main__':
    metadata.create_all(engine)