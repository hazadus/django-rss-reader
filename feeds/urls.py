from django.urls import path

from feeds.views import (EntriesListView, EntryDetailView, FeedListView,
                         TagListView)

app_name = "feeds"
urlpatterns = [
    path("", FeedListView.as_view(), name="feed_list"),
    path("entries/<str:mode>/", EntriesListView.as_view(), name="entry_list"),
    path(
        "entries/<str:mode>/<int:pk>/", EntryDetailView.as_view(), name="entry_detail"
    ),
    path("tags/all/", TagListView.as_view(), name="tag_list"),
]
