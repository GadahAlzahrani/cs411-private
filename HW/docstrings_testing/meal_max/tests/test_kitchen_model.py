import pytest
from contextlib import contextmanager
import re
import sqlite3




from meal_max.models.kitchen_model import (
    Meal,
    create_meal,
    delete_meal,
    get_leaderboard,
    get_meal_by_id,
    get_meal_by_name,
    update_meal_stats,
    clear_meals,
)

def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

# Mocking the database connection for tests
@pytest.fixture
def mock_db(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None
    mock_cursor.fetchall.return_value = []
    mock_cursor.commit.return_value = None
    
     # Mock the get_db_connection context manager from sql_utils
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn # Yield the mocked connection object

    mocker.patch("meal_max.models.kitchen_model.get_db_connection", mock_get_db_connection)

    return mock_conn, mock_cursor # Return the mock cursor so we can set expectations per test


def test_create_meal(mock_db):
    """Verify creation of a new meal entry."""
    mock_conn, mock_cursor = mock_db
    create_meal(meal="Tacos", cuisine="Mexican", price=9.99, difficulty="MED")

   
    expected_sql_query = normalize_whitespace("""
        INSERT INTO meals (meal, cuisine, price, difficulty)
        VALUES (?, ?, ?, ?)
    """)
    
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

   # Assert that the SQL query was correct
    assert actual_query == expected_sql_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call (second element of call_args)
    actual_arguments = mock_cursor.execute.call_args[0][1]
    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = ("Tacos", "Mexican", 9.99, "MED")
    assert actual_arguments == expected_arguments, f"SQL arguments mismatch. Expected {expected_arguments}, got {actual_arguments}."

def test_create_meal_duplicate(mock_db):
    """Test creating a meal with a duplicate name (should raise an error)."""

    mock_conn, mock_cursor = mock_db

    # Simulate that the database will raise an IntegrityError due to a duplicate entry
    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: meals.meal")

    # Expect the function to raise a ValueError with a specific message when handling the IntegrityError
    with pytest.raises(ValueError, match="Meal with name 'Tacos' already exists"):
        create_meal(meal="Tacos", cuisine="Mexican", price=9.99, difficulty="MED")

def test_create_meal_with_invalid_price():
    """Test creating a meal with invalid price."""
    with pytest.raises(ValueError, match="Invalid price: -5.99. Price must be a positive number."):
        create_meal(meal="Tacos", cuisine="Mexican", price=-5.99, difficulty="MED")

    # Attempt with non-numeric price
    with pytest.raises(ValueError, match="Invalid price: WRONG. Price must be a positive number."):
        create_meal(meal="Tacos", cuisine="Mexican", price="WRONG", difficulty="MED")

def test_create_meal_with_invalid_difficulty():
    """Attempt to create a meal with invalid difficulty level."""
    with pytest.raises(ValueError, match="Invalid difficulty level: HARD. Must be 'LOW', 'MED', or 'HIGH'."):
        create_meal(meal="Tacos", cuisine="Mexican", price=9.99, difficulty="HARD")

    # Attempt with non-string difficulty
    with pytest.raises(ValueError, match="Invalid difficulty level: 123. Must be 'LOW', 'MED', or 'HIGH'."):
        create_meal(meal="Tacos", cuisine="Mexican", price=9.99, difficulty=123)

def test_delete_meal(mock_db):
    """Test soft deleting a meal."""
    mock_conn, mock_cursor = mock_db
    #Simulate that the meal exists
    mock_cursor.fetchone.return_value = ([False])

    delete_meal(1)

    expected_select_sql = normalize_whitespace("SELECT deleted FROM meals WHERE id = ?")
    expected_update_sql = normalize_whitespace("UPDATE meals SET deleted = TRUE WHERE id = ?")

    actual_select_sql = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    actual_update_sql = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    assert actual_select_sql == expected_select_sql, "The SELECT query did not match the expected structure."
    assert actual_update_sql == expected_update_sql, "The UPDATE query did not match the expected structure."

def test_delete_meal_bad_id(mock_db):
    """Test error when trying to delete a non-existent meal."""
    mock_conn, mock_cursor = mock_db
    

    # Simulate that no meal exists with the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when attempting to delete a non-existent meal
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        delete_meal(999)

def test_clear_meals(mock_db, mocker):
    """Test clearing the entire meal table (removes all meals)."""
    mock_conn, mock_cursor = mock_db  
    mocker.patch.dict('os.environ', {'SQL_CREATE_TABLE_PATH': 'sql/create_meal_table.sql'})
    mock_open = mocker.patch('builtins.open', mocker.mock_open(read_data="The body of the create statement"))

    clear_meals()

    mock_open.assert_called_once_with('sql/create_meal_table.sql', 'r')
    mock_cursor.executescript.assert_called_once()


def test_get_meal_by_id(mock_db):
    """Get a meal by its ID."""

    mock_conn, mock_cursor = mock_db
    mock_cursor.fetchone.return_value = (1, "Tacos", "Mexican", 9.99, "MED", False)

    result = get_meal_by_id(1)
    expected_result = Meal(1, "Tacos", "Mexican", 9.99, "MED")

    
    assert result == expected_result, f"Expected {expected_result}, got {result}."

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    
    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = (1,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_get_meal_by_name(mock_db):
    """Get meal by name."""
    mock_conn, mock_cursor = mock_db
    mock_cursor.fetchone.return_value = (1, "Tacos", "Mexican", 9.99, "MED", False)

    result = get_meal_by_name("Tacos")
    expected_result = Meal(1, "Tacos", "Mexican", 9.99, "MED")

    assert result == expected_result, f"Expected {expected_result}, got {result}."

    # Update expected_query to match 'WHERE meal = ?'
    expected_query = normalize_whitespace("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE meal = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

def test_get_meal_by_id_bad_id(mock_db):
    """Test retrieving a meal by a non-existent ID."""

    mock_conn, mock_cursor = mock_db

    # Simulate that no meal exists for the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when the meal is not found
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        get_meal_by_id(999)
        
def test_get_meal_by_id_deleted(mock_db):
    """Test retrieving a meal that has been marked as deleted."""

    mock_conn, mock_cursor = mock_db

    # Simulate that the meal exists but is marked as deleted
    mock_cursor.fetchone.return_value = (1, "Tacos", "Mexican", 9.99, "MED", True)

    # Expect a ValueError when the meal is found but marked as deleted
    with pytest.raises(ValueError, match="Meal with ID 1 has been deleted"):
        get_meal_by_id(1)

def test_update_meal_stats_win(mock_db):
    """Update meal statistics with a win result."""
    mock_conn, mock_cursor = mock_db
    mock_cursor.fetchone.return_value = [False]

    meal_id = 1
    update_meal_stats(meal_id, "win")

    expected_query = normalize_whitespace("UPDATE meals SET battles = battles + 1, wins = wins + 1 WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

def test_get_leaderboard_win(mock_db):
    """Retrieve leaderboard based on total wins."""
    mock_conn, mock_cursor = mock_db
    mock_cursor.fetchall.return_value = [
        (3, "Ramen", "Japanese", 12.99, "HIGH", 6, 4, (4 * 1.0 / 6)),
        (1, "Tacos", "Mexican", 9.99, "MED", 4, 2, (2 * 1.0 / 4)),
        (2, "Pasta", "Italian", 7.99, "LOW", 3, 1, (1 * 1.0 / 3)),
    ]

    result = get_leaderboard("wins")
    expected_result = [
        {"id": 3, "meal": "Ramen", "cuisine": "Japanese", "price": 12.99, "difficulty": "HIGH", "battles": 6, "wins": 4, "win_pct": 66.7},
        {"id": 1, "meal": "Tacos", "cuisine": "Mexican", "price": 9.99, "difficulty": "MED", "battles": 4, "wins": 2, "win_pct": 50},
        {"id": 2, "meal": "Pasta", "cuisine": "Italian", "price": 7.99, "difficulty": "LOW", "battles": 3, "wins": 1, "win_pct": 33.3},
    ]
    
    assert result == expected_result, f"Expected {expected_result}, got {result}."

def test_update_meal_stats_loss(mock_db):
    """Update meal statistics with a loss result."""
    mock_conn, mock_cursor = mock_db
    mock_cursor.fetchone.return_value = [False]

    meal_id = 1
    update_meal_stats(meal_id, "loss")

    expected_query = normalize_whitespace("UPDATE meals SET battles = battles + 1 WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = (meal_id,)
    assert actual_arguments == expected_arguments, f"The SQL arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_get_leaderboard_win_pct(mock_db):
    """Retrieve leaderboard based on win percentage."""
    mock_conn, mock_cursor = mock_db
    
    mock_cursor.fetchall.return_value = [
        (3, "Ramen", "Japanese", 12.99, "HIGH", 4, 3, (3 * 1.0 / 4)),  # 75% win rate
        (1, "Tacos", "Mexican", 9.99, "MED", 5, 2, (2 * 1.0 / 5)),    # 40% win rate
        (2, "Pasta", "Italian", 7.99, "LOW", 3, 1, (1 * 1.0 / 3)),    # 33.3% win rate
    ]

    result = get_leaderboard("win_pct")

    expected_result = [
        {"id": 3, "meal": "Ramen", "cuisine": "Japanese", "price": 12.99, "difficulty": "HIGH", "battles": 4, "wins": 3, "win_pct": 75.0},
        {"id": 1, "meal": "Tacos", "cuisine": "Mexican", "price": 9.99, "difficulty": "MED", "battles": 5, "wins": 2, "win_pct": 40.0},
        {"id": 2, "meal": "Pasta", "cuisine": "Italian", "price": 7.99, "difficulty": "LOW", "battles": 3, "wins": 1, "win_pct": 33.3},
    ]


    assert result == expected_result, f"Expected {expected_result}, got {result}."

    
    expected_query = normalize_whitespace("""
        SELECT id, meal, cuisine, price, difficulty, battles, wins, (wins * 1.0 / battles) AS win_pct
        FROM meals WHERE deleted = false AND battles > 0 ORDER BY win_pct DESC
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    
    assert actual_query == expected_query, "The SQL query did not match the expected structure."
    