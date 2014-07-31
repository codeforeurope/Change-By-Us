"""
    :copyright: (c) 2011 Local Projects, all rights reserved
    :license: Affero GNU GPL v3, see LICENSE for more details.
"""

from sqlalchemy import *
from sqlalchemy.dialects import mysql
from migrate import *

def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind migrate_engine
    # to your metadata

    import os
    with open(os.path.join(os.path.dirname(__file__), 'Initial_models_asof_2.0.3.sql')) as initial_file:
        sql = initial_file.read()
        migrate_engine.execute(sql)

    with open(os.path.join(os.path.dirname(__file__), 'Initial_models_original_migrations.sql')) as old_migrations_file:
        sql = old_migrations_file.read()
        migrate_engine.execute(sql)

    meta = MetaData(migrate_engine)

    # Load the project and user tables (for the foreign keys)
    project = Table('project', meta, autoload=True)
    user = Table('user', meta, autoload=True)

    # Create the project place table
    needs = Table('project_needs', meta,
        Column('id', mysql.INTEGER(11), primary_key=True, nullable=False),
        Column('type', String(10)),
        Column('item_needed', String(64)),
        Column('num_needed', Integer),
        Column('description', Text),
        Column('project_id', mysql.INTEGER(11), ForeignKey('project.project_id'), nullable=False),
        mysql_engine='MyISAM',
    )
    needs.create()

    volunteers = Table('project_need_volunteers', meta,
        Column('need_id', mysql.INTEGER(11), ForeignKey('project_needs.id'), primary_key=True),
        Column('member_id', Integer, ForeignKey('user.user_id'), primary_key=True),
        mysql_engine='MyISAM',
    )
    volunteers.create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta = MetaData(migrate_engine)

    # Get rid of the created tables.
    volunteers = Table('project_need_volunteers', meta, autoload=True)
    volunteers.drop()

    needs = Table('project_needs', meta, autoload=True)
    needs.drop()

    # The SQL schema isn't as important.  It'll get overwritten anyway.
