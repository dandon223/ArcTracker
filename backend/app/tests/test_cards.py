from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

User = get_user_model()


class CardsAPITests(APITestCase):  # type: ignore[misc]
    fixtures = ["app/initial_data/initial_data.json"]

    def setUp(self) -> None:
        self.client = APIClient()
        self.url = reverse("cards")
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.client.login(username="testuser", password="12345")

    def test_cards_get(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 28)

    def test_cards_get_one(self) -> None:
        data = {"suit": "ADMINISTRATION", "number": "ONE"}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_player_get_no_card(self) -> None:
        data = {"suit": "ADMINISTRATION", "number": "EIGHT"}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "no card found")
