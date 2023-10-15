from django.urls import path

from feeds.views import (
    EntryDetailView,
    EntryListView,
    FeedListView,
    FeedsSettingsView,
    FoldersSettingsView,
    entry_toggle_is_favorite_view,
)

app_name = "feeds"
urlpatterns = [
    path("", FeedListView.as_view(), name="feed_list"),
    path("settings/feeds/", FeedsSettingsView.as_view(), name="settings_feeds"),
    path("settings/folders/", FoldersSettingsView.as_view(), name="settings_folders"),
    path("entries/<str:mode>/", EntryListView.as_view(), name="entry_list"),
    path(
        "entries/<str:mode>/<int:pk>/", EntryDetailView.as_view(), name="entry_detail"
    ),
    path(
        "entry/toggle/is_favorite/<int:entry_pk>/",
        entry_toggle_is_favorite_view,
        name="entry_toggle_is_favorite",
    ),
]
