from django.test import TestCase
from django.urls import reverse

from feeds.models import Entry


class MiscViewTest(TestCase):
    """
    Test misc. views.
    """

    fixtures = [
        "users/tests/fixtures/users.json",
        "feeds/tests/fixtures/tags.json",
        "feeds/tests/fixtures/feeds.json",
        "feeds/tests/fixtures/entries.json",
    ]

    @classmethod
    def setUpTestData(cls):
        pass

    def test_entry_toggle_is_favorite_view(self):
        """
        Test `entry_toggle_is_favorite` view works as expected.
        """
        entry = Entry.objects.filter(is_favorite=False).first()
        entry_pk = entry.pk
        url = reverse("feeds:entry_toggle_is_favorite", kwargs={"entry_pk": entry_pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Entry.objects.get(pk=entry_pk).is_favorite, True)
