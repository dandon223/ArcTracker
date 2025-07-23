# from django.test import TestCase

# Create your tests here.

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from .models import Player

User = get_user_model()


class PlayerAPITests(APITestCase):  # type: ignore[misc]
    def setUp(self) -> None:
        self.client = APIClient()
        self.url = reverse("players")
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.user_two = User.objects.create_user(username="testuser_two", password="12345")
        self.client.login(username="testuser", password="12345")

    def test_create_player(self) -> None:
        new_data = {"nick": "a"}
        response = self.client.post(self.url, new_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Player.objects.filter(user=self.user).count(), 1)
        self.assertEqual(Player.objects.first().user, self.user)  # type: ignore[union-attr]

    def test_user_see_only_their_players(self) -> None:
        Player.objects.create(nick="a", user=self.user)
        Player.objects.create(nick="b", user=self.user_two)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["nick"], "a")

    def test_user_get_one_player(self) -> None:
        Player.objects.create(nick="a", user=self.user)
        Player.objects.create(nick="b", user=self.user)
        response = self.client.get(self.url, {"nick": "a"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["nick"], "a")

    def test_user_get_no_player_error(self) -> None:
        response = self.client.get(self.url, {"nick": "a"})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["nick"], "player with nick a does not exists")
