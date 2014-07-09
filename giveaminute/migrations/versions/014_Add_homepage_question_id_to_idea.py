from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    meta = MetaData(migrate_engine)
    idea = Table('idea', meta, autoload=True)

    # Add column
    try:
        create_column(Column('homepage_question_id', Integer, nullable=True), idea)
    except Exception, e:
        print "Error when adding column idea.homepage_question_id: %s. Ignoring" % e


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta = MetaData(migrate_engine)
    idea = Table('idea', meta, autoload=True)

    try:
        drop_column('homepage_question_id', idea)
    except Exception, e:
        print "Error when removing column idea.homepage_question_id: %s. Ignoring" % e
