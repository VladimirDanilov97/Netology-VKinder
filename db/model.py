from curses import meta
from sqlalchemy import ForeignKey, MetaData, Table, Column, Integer, String, Date, create_engine

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


if __name__ == '__main__':
    metadata.create_all(engine)