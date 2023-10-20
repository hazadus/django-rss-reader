from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from users.models import CustomUser


class UserProfileView(
    LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView
):
    model = CustomUser
    fields = ["username", "first_name", "last_name", "profile_image"]
    template_name = "layout_settings.html"
    success_message = "Profile successfully updated!"

    def test_func(self):
        """Only allow user to update own profile."""
        user = self.get_object()
        return user == self.request.user

    def get_success_url(self):
        return reverse_lazy("users:user_profile", kwargs={"pk": self.get_object().pk})
