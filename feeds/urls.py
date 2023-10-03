from django.urls import path

from feeds.views import EntriesListView, EntryDetailView, TagListView

app_name = "feeds"
urlpatterns = [
    path("entries/<str:view>/", EntriesListView.as_view(), name="entry_list"),
    path(
        "entries/<str:view>/<int:pk>/", EntryDetailView.as_view(), name="entry_detail"
    ),
    path("tags/all/", TagListView.as_view(), name="tag_list"),
]
