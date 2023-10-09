from django.test import TestCase
from django.urls import reverse

from feeds.models import Entry


class EntryDetailViewTest(TestCase):
    """
    Test "feeds:entry_list" view with various options.
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

    def test_entry_detail_view_marks_as_read(self):
        """
        Test that when user opens entry detail view the entry's `is_read` is set to `True`.
        """
        entry = Entry.objects.filter(is_read=False).first()
        entry_pk = entry.pk
        url = reverse("feeds:entry_detail", kwargs={"mode": "all", "pk": entry_pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Entry.objects.get(pk=entry_pk).is_read, True)
