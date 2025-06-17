from django.urls import include, path

from products.views import HomeView

urlpatterns = [
    path("home/", HomeView.as_view(), name="home"),
]
