from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    meta = MetaData(migrate_engine)
    users = Table('user', meta, autoload=True)
    ideas = Table('idea', meta, autoload=True)
    # Create the events table
    idea_user = Table('idea__user', meta,
        Column('idea_id', Integer, ForeignKey('idea.idea_id')),
        Column('user_id', Integer, ForeignKey('user.user_id')),
        Column('vote', SmallInteger, default=0),
        mysql_engine='MyISAM',
    )
    idea_user.create()
    unique_idea_user = UniqueConstraint('idea_id', 'user_id')
    idea_user.constraints.add(unique_idea_user)
    pass


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta = MetaData(migrate_engine)

    # Drop the idea__user table
    idea_user = Table('idea__user', meta, autoload=True)
    idea_user.drop()

    pass
