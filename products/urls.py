from django.urls import include, path

from products.views import HomeView, ProductListView

urlpatterns = [
    path("home/", HomeView.as_view(), name="home"),
    path("list/", ProductListView.as_view(), name="product_list"),
]
