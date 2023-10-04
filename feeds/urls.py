from django.urls import path

from feeds.views import EntriesListView, EntryDetailView, TagListView, FeedListView

app_name = "feeds"
urlpatterns = [
    path("feeds/", FeedListView.as_view(), name="feed_list"),
    path("entries/<str:mode>/", EntriesListView.as_view(), name="entry_list"),
    path(
        "entries/<str:mode>/<int:pk>/", EntryDetailView.as_view(), name="entry_detail"
    ),
    path("tags/all/", TagListView.as_view(), name="tag_list"),
]
