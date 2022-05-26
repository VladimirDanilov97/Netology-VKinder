from curses import meta
from email.policy import default
from sqlalchemy import ForeignKey, MetaData, PrimaryKeyConstraint, Table, Column, Integer, String, Date, create_engine

metadata = MetaData()
engine = create_engine('sqlite:///db.db')


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
    Column('user_id', Integer, ForeignKey('users.user_id')),
    Column('favorite_user_id', Integer)
    )

user_state_machine = Table('user_state_machine', metadata,
    Column('user_id', Integer, primary_key=True),
    Column('state', String(80), default='None')
    )

user_search_index = Table('user_search_index', metadata,
    Column('user_id', Integer, primary_key=True),
    Column('search_index', Integer),
    )

user_search_index = Table('last_search_params', metadata,
    Column('user_id', Integer, primary_key=True),
    Column('city_id', Integer),
    Column('sex_id', Integer),
    Column('age_from', Integer),
    Column('age_to', Integer),
    )
    
list_of_user_to_send = Table('list_of_user_to_send', metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', Integer),
    Column('user_id_to_send', Integer),
    )

if __name__ == '__main__':
    metadata.create_all(engine)