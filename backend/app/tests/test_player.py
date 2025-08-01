from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from ..models import Player

User = get_user_model()


class PlayerAPITests(APITestCase):  # type: ignore[misc]
    def setUp(self) -> None:
        self.client = APIClient()
        self.url = reverse("players")
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.user_two = User.objects.create_user(username="testuser_two", password="12345")
        self.client.login(username="testuser", password="12345")

    def test_player_post(self) -> None:
        response = self.client.post(self.url, {"nick": "a"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Player.objects.filter(user=self.user).count(), 1)

    def test_player_post_already_created(self) -> None:
        Player.objects.create(nick="a", user=self.user)
        response = self.client.post(self.url, {"nick": "a"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "player a already exist")

    def test_player_post_duplicated_nick_in_database(self) -> None:
        Player.objects.create(nick="a", user=self.user_two)
        response = self.client.post(self.url, {"nick": "a"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Player.objects.filter(user=self.user).count(), 1)

    def test_player_get(self) -> None:
        Player.objects.create(nick="a", user=self.user)
        Player.objects.create(nick="b", user=self.user_two)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["nick"], "a")

    def test_player_get_one(self) -> None:
        Player.objects.create(nick="a", user=self.user)
        Player.objects.create(nick="b", user=self.user)
        response = self.client.get(self.url, {"nick": "a"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nick"], "a")

    def test_player_get_no_player(self) -> None:
        response = self.client.get(self.url, {"nick": "a"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "player a does not exist")
