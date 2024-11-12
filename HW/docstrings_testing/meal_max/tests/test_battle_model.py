import pytest

from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal


@pytest.fixture()
def battle_model():
    """Fixture to provide a new instance of BattleModel for each test."""
    return BattleModel()

@pytest.fixture
def mock_update_meal_stats(mocker):
    """Mock the update_meal_stats function for testing purposes."""
    return mocker.patch("meal_max.models.battle_model.update_meal_stats")

"""Fixtures providing sample songs for the tests."""
@pytest.fixture
def sample_meal1():
    return Meal(1, 'Meal 1', 'Cuisine 1', 19.99, 'LOW')

@pytest.fixture
def sample_meal2():
    return Meal(2, 'Meal 2', 'Cuisine 2', 19.99, 'LOW')

@pytest.fixture
def sample_meal3():
    return Meal(3, 'Meal 3', 'Cuisine 3', 19.97, 'HIGH')

@pytest.fixture
def sample_battle(sample_meal1, sample_meal2):
    return [sample_meal1, sample_meal2]


##################################################
# Add Meal Management Test Cases
##################################################

def test_prep_combatant(battle_model, sample_meal1):
    """Test adding a meal to the leaderboard."""
    battle_model.prep_combatant(sample_meal1)
    assert len(battle_model.combatants) == 1
    assert battle_model.combatants[0].meal == 'Meal 1'

def test_prep_combatant_several(sample_battle, sample_meal3):
    """Test error when adding a meal to a leaderboard with two combatants."""
    sample_battle.prep_combatant(sample_meal3)
    with pytest.raises(ValueError, match="Combatant list is full, cannot add more combatants."):
        sample_battle.prep_combatant(sample_meal3)

##################################################
# Clear Combatants Management Test Cases
##################################################

def test_clear_combatants(battle_model, sample_meal1):
    """Test clearing the entire leaderboard."""
    battle_model.prep_combatant(sample_meal1)

    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0, "Leaderboard should be empty after clearing"

##################################################
# Song Retrieval Test Cases
##################################################

def test_get_battle_score(battle_model, sample_battle, sample_meal1):
    """Test successfully retrieving a battle score from the leaderboard."""
    battle_model.combatants.extend(sample_battle)

    retrieved_meal = battle_model.get_battle_score(sample_meal1)
    assert retrieved_meal == 116.94

def test_get_combatants(battle_model, sample_battle):
    """Test successfully retrieving all combatants from the battle."""
    battle_model.combatants.extend(sample_battle)

    all_meals = battle_model.get_combatants()
    assert len(all_meals) == 2
    assert all_meals[0].id == 1
    assert all_meals[1].id == 2

##################################################
# Battle Function Test Cases
##################################################

def test_battle_less_than_two_meals(battle_model, sample_meal1):
    """Test if battle raises error when there are less than two combatants."""
    battle_model.prep_combatant(sample_meal1)
    with pytest.raises(ValueError, match="Two combatants must be prepped for a battle."):
        battle_model.battle()  # Start a battle with one combatant

def test_battle_error(battle_model, sample_battle):
    """Test if battle raises error when there are two combatants."""
    battle_model.combatants.extend(sample_battle)
    try:
        battle_model.battle()
    except ValueError:
        pytest.fail("battle raised ValueError unexpectedly on two combatants")

def test_battle(battle_model, sample_battle):
    """Test if battle raises error when there are two combatants."""
    battle_model.combatants.extend(sample_battle)
    battle_winner = battle_model.battle()
    assert battle_winner == "Meal 2"
