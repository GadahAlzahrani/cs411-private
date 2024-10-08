from typing import Optional, List, Any
from migration import Migration
from migration_path import MigrationPath
from habitat_management.habitat import Habitat


class MigrationManager:
    def __init__(self) -> None:
        migrations: dict[int, Migration] = {}

    def get_migrations_by_migration_path(self, migration_path_id: int) -> List[Migration]:
        pass

    def get_migrations_by_start_date(self, start_date: str) -> List[Migration]:
        pass

    def get_migrations_by_current_location(self, current_location: str) -> List[Migration]:
        pass

    def get_migrations_by_status(self, status: str) -> List[Migration]:
        pass

    def get_migrations(self) -> List[Migration]:
        pass

    def get_migration_by_id(self, migration_id: int) -> Migration:
        pass

    def cancel_migration(self, migration_id: int) -> None:
        pass

    def schedule_migration(self, migration_path: MigrationPath) -> None:
        pass

    def update_migration_details(self, migration_id: int, **kwargs: Any) -> None:
        pass

    def remove_migration(self, migration_id: int) -> None:
        pass

    def create_migration_path(self, species: str, start_location: Habitat, destination: Habitat, duration: Optional[int] = None) -> None:
        pass

    def get_migration_path_by_id(self, path_id: int) -> MigrationPath:
        pass

    def get_migration_paths_by_destination(self, destination: Habitat) -> list[MigrationPath]:
        pass

    def get_migration_paths_by_species(self, species: str) -> list[MigrationPath]:
        pass

    def get_migration_paths_by_start_location(self, start_location: Habitat) -> list[MigrationPath]:
        pass

    def get_migration_paths(self) -> list[MigrationPath]:
        pass

    def remove_migration_path(self, path_id: int) -> None:
        pass