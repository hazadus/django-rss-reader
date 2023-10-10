from datetime import datetime

from django.test import TestCase

from feeds.models import Entry
from users.models import CustomUser


class BaseFeedsViewsTestCase(TestCase):
    """
    Common stuff for `feeds` view tests.
    """

    MODE_QUERYSETS = {}

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

        cls.MODE_QUERYSETS = {
            "all": Entry.objects.filter(
                feed__user=cls.user,
            ),
            "today": Entry.objects.filter(
                feed__user=cls.user,
                pub_date__day=datetime.today().day,
                pub_date__month=datetime.today().month,
                pub_date__year=datetime.today().year,
            ),
            "unread": Entry.objects.filter(
                feed__user=cls.user,
                is_read=False,
            ),
            "read": Entry.objects.filter(
                feed__user=cls.user,
                is_read=True,
            ),
            "favorites": Entry.objects.filter(
                feed__user=cls.user,
                is_favorite=True,
            ),
        }
