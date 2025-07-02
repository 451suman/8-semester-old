from django.urls import include, path

from products.views import (
    EmpytCartView,
    HomeView,
    ProductDetailView,
    ProductListView,
    MyCartView,
    AddToCartView,
)

urlpatterns = [
    path("home/", HomeView.as_view(), name="home"),
    path("list/", ProductListView.as_view(), name="product_list"),
    path("detail/<str:slug>/", ProductDetailView.as_view(), name="product_detail"),
    path("add-to-cart/<int:pk>/", AddToCartView.as_view(), name="add_to_cart"),
    path("cart/", MyCartView.as_view(), name="my-cart"),
    path("empty-cart/", EmpytCartView.as_view(), name="empty-cart"),
]
