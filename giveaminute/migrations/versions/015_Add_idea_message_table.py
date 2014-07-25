import datetime
from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    meta = MetaData(migrate_engine)
    users = Table('user', meta, autoload=True)
    ideas = Table('idea', meta, autoload=True)
    # Create the events table
    idea_message = Table('idea_message', meta,
        Column('idea_message_id', Integer, primary_key=True),
        Column('message_type', String(20)),
        Column('message', Text),
        Column('idea_id', Integer, ForeignKey('idea.idea_id')),
        Column('user_id', Integer, ForeignKey('user.user_id')),
        Column('is_active', SmallInteger, default=1),
        Column('created_datetime', TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP')),
        Column('file_id', Integer),
        mysql_engine='MyISAM',
    )

    idea_message.create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta = MetaData(migrate_engine)

    try:
        idea_message = Table('idea_message', meta, autoload=True)
        idea_message.drop()
    except Exception, e:
        print "Error when dropping table idea_message: %s. Ignoring" % e
