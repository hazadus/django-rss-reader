from django import forms
from django.forms import ModelForm

from feeds.models import Feed


class FeedCreateForm(ModelForm):
    class Meta:
        model = Feed
        exclude = ["user"]

    def __init__(self, *args, **kwargs):
        """
        Save `request` object in form instance to get `user` from it in `clean` methods.
        """
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

    def clean_url(self):
        """
        Check if user already has Feed with the same URL.
        """
        url = self.data.get("url")
        user = self.request.user
        if Feed.objects.filter(user=user, url=url).exists():
            raise forms.ValidationError(
                "You already have subscription to {url}!".format(url=url)
            )
        return url
