from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class UserProfileView(LoginRequiredMixin, TemplateView):
    template_name = "layout_settings.html"
