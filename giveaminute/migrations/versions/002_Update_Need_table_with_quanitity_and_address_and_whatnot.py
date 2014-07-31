"""
    :copyright: (c) 2011 Local Projects, all rights reserved
    :license: Affero GNU GPL v3, see LICENSE for more details.
"""

from sqlalchemy import *
from migrate import *

def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind migrate_engine
    # to your metadata
    
    meta = MetaData(migrate_engine)

    # Create the project place table
    place = Table('project_place', meta,
        Column('id', Integer, nullable=False, primary_key=True),
        Column('name', String(256)),
        Column('street', String(256)),
        Column('city', String(256)),
        mysql_engine='MyISAM',
    )
    place.create()

    # Rename the project_needs table to project_need
    need = Table('project_needs', meta, autoload=True)
    need.rename('project_need')
    
    # Rename the project_need_volunteers table to project_need_volunteer
    volunteer = Table('project_need_volunteers', meta, autoload=True)
    volunteer.rename('project_need_volunteer')
    
    # The above renames are to be consistent with the other table naming. We're
    # using singular nouns for tables. The table is the schema for the table
    # (the model of what's in the table) more than it is the rows, in this view.
    
    # Modify/add columns

    sql_update_needs_request = "alter table project_need CHANGE item_needed request VARCHAR(64) "
    sql_update_needs_quantity = "alter table project_need CHANGE num_needed quantity INTEGER(11) "
    migrate_engine.execute(sql_update_needs_request)
    migrate_engine.execute(sql_update_needs_quantity)


    create_column(Column('address_id', Integer, ForeignKey('project_place.id')), need)
    create_column(Column('date', Date), need)
    create_column(Column('time', String(32)), need)
    create_column(Column('duration', String(64)), need)


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    
    meta = MetaData(migrate_engine)
    
    # Rename the project_need_volunteer table back to project_need_volunteers
    volunteer = Table('project_need_volunteer', meta, autoload=True)
    volunteer.rename('project_need_volunteers')
    
    # Rename the project_need table back to project_needs
    need = Table('project_need', meta, autoload=True)
    need.rename('project_needs')
    
    # Modify/remove columns
    sql_update_needs_request = "alter table project_need CHANGE request item_needed VARCHAR(64) "
    sql_update_needs_quantity = "alter table project_need CHANGE quantity num_needed INTEGER(11) "
    migrate_engine.execute(sql_update_needs_request)
    migrate_engine.execute(sql_update_needs_quantity)
    drop_column('address_id', need)
    drop_column('date', need)
    drop_column('time', need)
    drop_column('duration', need)
    
    # Get rid of the project place table
    place = Table('project_place', meta, autoload=True)
    place.drop()
