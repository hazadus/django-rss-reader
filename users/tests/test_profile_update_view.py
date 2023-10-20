from django.test import TestCase
from django.urls import reverse

from users.models import CustomUser


class UserProfileUpdateTest(TestCase):
    """
    Tests for "users:user_profile" view.
    """

    email = "anon@mail.com"
    password = "12345678"
    user = None

    fixtures = [
        "users/tests/fixtures/users.json",
        "feeds/tests/fixtures/tags.json",
        "feeds/tests/fixtures/feeds.json",
        "feeds/tests/fixtures/entries.json",
    ]

    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.get(email=cls.email)

    def test_profile_update_view_302_for_anonymous(self):
        url = reverse("users:user_profile", kwargs={"pk": self.user.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_profile_update_view_opens_with_login(self):
        # Login
        url = reverse("account_login")
        self.client.post(
            url, {"login": self.email, "password": self.password}, follow=True
        )

        url = reverse("users:user_profile", kwargs={"pk": self.user.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_profile_update_403_for_other_user(self):
        # Login
        url = reverse("account_login")
        self.client.post(
            url, {"login": self.email, "password": self.password}, follow=True
        )

        other_user = CustomUser.objects.exclude(username=self.user.username).first()

        url = reverse("users:user_profile", kwargs={"pk": other_user.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_profile_update_works_with_correct_data(self):
        # Login
        url = reverse("account_login")
        self.client.post(
            url, {"login": self.email, "password": self.password}, follow=True
        )

        new_username = "newUsername"
        new_first_name = "New First Name"
        new_last_name = "New Last Name"

        url = reverse("users:user_profile", kwargs={"pk": self.user.pk})
        response = self.client.post(
            url,
            data={
                "username": new_username,
                "first_name": new_first_name,
                "last_name": new_last_name,
            },
            follow=True,
        )

        updated_user = CustomUser.objects.get(pk=self.user.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(updated_user.username, new_username)
        self.assertEqual(updated_user.first_name, new_first_name)
        self.assertEqual(updated_user.last_name, new_last_name)
