from sqlalchemy import *
from migrate import *
import sqlalchemy.types as types



def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    meta = MetaData(migrate_engine)
    project_table = Table('project', meta, autoload=True)
    #Add Latitude and Longitude to Project table
    create_column(Column('lat', types.DECIMAL(9, 6), nullable=True), project_table)
    create_column(Column('lon', types.DECIMAL(9, 6), nullable=True), project_table)

    #Add column to hold the GeoJSON data for Location table
    location_table = Table('location', meta, autoload=True)
    create_column(Column('geometry', Text, nullable=True), location_table)


def downgrade(migrate_engine):
    meta = MetaData(migrate_engine)
    project_table = Table('project', meta, autoload=True)
    location_table = Table('location', meta, autoload=True)

    #Drop columns
    drop_column('lat', project_table)
    drop_column('lon', project_table)
    drop_column('geometry', location_table)
