from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    meta = MetaData(migrate_engine)
    resource_table = Table('project_resource', meta, autoload=True)

    # Add column
    try:
        create_column(Column('message', Text, nullable=True), resource_table)
    except Exception, e:
        # The column may already exist
        print "Error when adding column project_resource.message: %s. Ignoring" % e



def downgrade(migrate_engine):
    meta = MetaData(migrate_engine)
    resource_table = Table('project_resource', meta, autoload=True)

    # Remove the column
    try:
        drop_column('message', resource_table)
    except Exception, e:
        print "Error when removing column project_resource.message: %s. Ignoring" % e
