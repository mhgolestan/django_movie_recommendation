import pytest
from django.contrib.auth import get_user_model
from movies.models import UserMoviePreferences
from movies.services import add_preference


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
