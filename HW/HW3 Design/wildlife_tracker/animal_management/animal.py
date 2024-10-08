from typing import Any, Optional


class Animal:
    def __init__(self,
                 animal_id: int,
                 environment_type: str,
                 species: str,
                 health_status: Optional[str] = None,
                 age: Optional[int] = None):
        self.animal_id = animal_id
        self.species = species
        self.environment_type = environment_type
        self.health_status = health_status
        self.age = age


    def get_animal_details(self) -> dict[str, Any]:
        pass


    def update_animal_details(self, **kwargs: Any) -> None:
        pass
