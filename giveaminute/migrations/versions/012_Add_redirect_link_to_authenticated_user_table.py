from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    # ALTER TABLE `unauthenticated_user` ADD `redirect_link` VARCHAR( 255 ) AFTER `last_name`;
    meta = MetaData(migrate_engine)
    unauthenticated_users = Table('unauthenticated_user', meta, autoload=True)
    create_column(Column('redirect_link', String(255), nullable=True), unauthenticated_users)


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.

    meta = MetaData(migrate_engine)
    unauthenticated_users = Table('unauthenticated_user', meta, autoload=True)

    # Remove the column
    drop_column('redirect_link', unauthenticated_users)
