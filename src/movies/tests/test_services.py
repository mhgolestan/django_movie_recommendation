import pytest
from django.contrib.auth import get_user_model
from movies.services import add_preference
from movies.models import Movie, UserMoviePreferences
from movies.services import add_watch_history

@pytest.mark.django_db
def test_add_preference_creates_new_preferences():
    user_model = get_user_model()
    user = user_model.objects.create_user(username="test_user", password="password")
    new_preferences = {"genres": ["Sci-Fi"], "directors": ["Christopher Nolan"]}

    add_preference(user.id, new_preferences)

    user_preferences = UserMoviePreferences.objects.get(user_id=user.id)
    expected_preferences = {"genres": ["Sci-Fi"], "directors": ["Christopher Nolan"]}
    assert expected_preferences == user_preferences.preferences


@pytest.mark.django_db
def test_add_preference_updates_existing_preferences():
    user_model = get_user_model()
    user = user_model.objects.create_user(username="test_user", password="password")
    existing_preferences = {"genres": ["Action"], "directors": ["James Cameron"]}
    UserMoviePreferences.objects.create(user=user, preferences=existing_preferences)
    new_preferences = {"genres": ["Sci-Fi"], "directors": ["James Cameron"]}

    add_preference(user.id, new_preferences)

    user_preferences = UserMoviePreferences.objects.get(user_id=user.id)
    expected_preferences = {"genres": ["Action", "Sci-Fi"], "directors": ["James Cameron"]}
    assert expected_preferences == user_preferences.preferences


@pytest.mark.django_db
def test_add_preference_with_duplicate_value():
    user_model = get_user_model()
    user = user_model.objects.create_user(username="test_user", password="password")
    existing_preferences = {"genres": ["Sci-Fi"]}
    UserMoviePreferences.objects.create(user=user, preferences=existing_preferences)
    new_preferences = {"genres": ["Sci-Fi"]}

    add_preference(user.id, new_preferences)

    user_preferences = UserMoviePreferences.objects.get(user_id=user.id)
    expected_preferences = {"genres": ["Sci-Fi"]}
    assert expected_preferences == user_preferences.preferences


@pytest.mark.django_db
def test_add_preference_creates_default_preferences():
    user_model = get_user_model()
    user = user_model.objects.create_user(username="test_user", password="password")
    new_preferences = {"genres": ["Comedy"]}

    add_preference(user.id, new_preferences)

    user_preferences = UserMoviePreferences.objects.get(user_id=user.id)
    expected_preferences = {"genres": ["Comedy"]}
    assert expected_preferences == user_preferences.preferences


@pytest.mark.django_db
def test_add_preference_raises_error_for_nonexistent_user():
    non_existent_user_id = 99999
    new_preferences = {"genres": ["Drama"]}

    with pytest.raises(Exception):
        add_preference(non_existent_user_id, new_preferences)


@pytest.mark.django_db
class TestAddWatchHistory:
    @pytest.fixture
    def user(self):
        User = get_user_model()
        return User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    @pytest.fixture
    def movie(self):
        return Movie.objects.create(
            title='Test Movie',
            genres=['Action'],
            release_year=2023,
            extra_data={'director': ['Test Director']}
        )

    def test_add_first_movie_to_watch_history(self, user, movie):
        """Test adding a movie to watch history for the first time."""
        add_watch_history(user.id, movie.id)

        user_preferences = UserMoviePreferences.objects.get(user_id=user.id)
        assert len(user_preferences.watch_history) == 1

        movie_info = user_preferences.watch_history[0]
        assert movie_info['title'] == 'Test Movie'
        assert movie_info['year'] == 2023
        assert movie_info['director'] == ['Test Director']
        assert movie_info['genres'] == ['Action']

    def test_add_multiple_movies_to_watch_history(self, user, movie):
        """Test adding multiple movies to watch history."""
        # Add first movie
        add_watch_history(user.id, movie.id)

        # Create and add second movie
        movie2 = Movie.objects.create(
            title='Test Movie 2',
            genres=['Drama'],
            release_year=2024,
            extra_data={'director': ['Another Director']}
        )
        add_watch_history(user.id, movie2.id)

        user_preferences = UserMoviePreferences.objects.get(user_id=user.id)
        assert len(user_preferences.watch_history) == 2
        assert user_preferences.watch_history[1]['title'] == 'Test Movie 2'

    def test_add_movie_with_missing_optional_fields(self, user):
        """Test adding a movie with missing optional fields."""
        movie = Movie.objects.create(
            title='Minimal Movie',
            genres=[],
            extra_data={}
        )

        add_watch_history(user.id, movie.id)

        user_preferences = UserMoviePreferences.objects.get(user_id=user.id)
        movie_info = user_preferences.watch_history[0]
        assert movie_info['title'] == 'Minimal Movie'
        assert movie_info['year'] is None
        assert movie_info['director'] == []
        assert movie_info['genres'] == []

    def test_add_same_movie_multiple_times(self, user, movie):
        """Test adding the same movie multiple times."""
        add_watch_history(user.id, movie.id)
        add_watch_history(user.id, movie.id)

        user_preferences = UserMoviePreferences.objects.get(user_id=user.id)
        assert len(user_preferences.watch_history) == 2
        assert user_preferences.watch_history[0] == user_preferences.watch_history[1]

    def test_nonexistent_movie(self, user):
        """Test adding a non-existent movie."""
        non_existent_movie_id = 99999

        with pytest.raises(Exception):
            add_watch_history(user.id, non_existent_movie_id)

    def test_nonexistent_user(self, movie):
        """Test adding a movie for non-existent user."""
        non_existent_user_id = 99999
        user = get_user_model()
        with pytest.raises(user.DoesNotExist):
            add_watch_history(non_existent_user_id, movie.id)

    def test_concurrent_access(self, user, movie):
        """Test handling of concurrent access to watch history."""
        # Simulate a race condition by creating preferences first
        UserMoviePreferences.objects.create(user=user, watch_history=[])

        add_watch_history(user.id, movie.id)

        user_preferences = UserMoviePreferences.objects.get(user_id=user.id)
        assert len(user_preferences.watch_history) == 1
        assert user_preferences.watch_history[0]['title'] == movie.title