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
        UniqueConstraint('idea_id', 'user_id', name='uix_1'),
        mysql_engine='MyISAM',
    )
    try:
        idea_user.create()
    except Exception, e:
        print "Error when creating table idea__user: %s. Ignoring" % e


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta = MetaData(migrate_engine)

    # Drop the idea__user table
    try:
        idea_user = Table('idea__user', meta, autoload=True)
        idea_user.drop()
    except Exception, e:
        print "Error when dropping table idea__user: %s. Ignoring" % e
