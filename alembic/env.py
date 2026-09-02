import importlib
import pkgutil
import sys
from os.path import abspath, dirname

sys.path.insert(0, dirname(dirname(abspath(__file__))) + "/src")

from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

from agrisim.core.config import settings
from agrisim.core.database import Base
from agrisim import models

from geoalchemy2 import alembic_helpers
from typing import Callable, Optional, cast, Union, Literal, Any
from sqlalchemy.sql.schema import SchemaItem
from geoalchemy2.types import Geometry

for _, module_name, _ in pkgutil.walk_packages(models.__path__, models.__name__ + "."):
    importlib.import_module(module_name)

config = context.config
config.set_main_option("sqlalchemy.url", settings.SQLALCHEMY_DATABASE_URI)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Comprehensive list of PostGIS & Tiger Geocoder system tables to always ignore
POSTGIS_SYSTEM_TABLES = {
    "spatial_ref_sys",
    "place",
    "county",
    "addr",
    "addrfeat",
    "bg",
    "cousub",
    "edges",
    "faces",
    "featnames",
    "layer",
    "loader_lookuptables",
    "loader_platform",
    "loader_variables",
    "pagc_gaz",
    "pagc_lex",
    "pagc_rules",
    "place_lookup",
    "secondary_unit_lookup",
    "state",
    "state_lookup",
    "street_type_lookup",
    "tabblock",
    "tabblock20",
    "topology",
    "tract",
    "zcta5",
    "zip_lookup",
    "zip_lookup_all",
    "zip_lookup_base",
    "zip_state",
    "zip_state_loc",
    "county_lookup",
    "countysub_lookup",
    "direction_lookup",
    "geocode_settings",
    "geocode_settings_default",
}


def custom_include_object(
    object: SchemaItem,
    name: Optional[str],
    type_: str,
    reflected: bool,
    compare_to: Optional[SchemaItem],
) -> bool:
    # 1. Ignore all PostGIS system tables so Alembic never tries to drop them
    if type_ == "table" and name in POSTGIS_SYSTEM_TABLES:
        return False
    # 2. Defer to GeoAlchemy2's helper logic for everything else
    include_object: Callable[[SchemaItem, Optional[str], str, bool, Optional[SchemaItem]], bool] = alembic_helpers.include_object  # type: ignore[assignment]
    return include_object(object, name, type_, reflected, compare_to)


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=custom_include_object,
        process_revision_directives=alembic_helpers.writer,
        render_item=alembic_helpers.render_item,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=custom_include_object,  # Uses our robust custom filter
            process_revision_directives=alembic_helpers.writer,  # Auto-injects geoalchemy2 import
            render_item=alembic_helpers.render_item,  # Renders geometry types properly
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
