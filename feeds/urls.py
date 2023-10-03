from django.urls import path

from feeds.views import AllEntriesListView, EntryDetailView

app_name = "feeds"
urlpatterns = [
    path("entries/all/", AllEntriesListView.as_view(), name="entry_list_all"),
    path("entries/<int:pk>/", EntryDetailView.as_view(), name="entry_detail"),
]
