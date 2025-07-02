from django.urls import include, path

from products.views import HomeView, ProductDetailView, ProductListView, MyCartView

urlpatterns = [
    path("home/", HomeView.as_view(), name="home"),
    path("list/", ProductListView.as_view(), name="product_list"),
    path("detail/<str:slug>/", ProductDetailView.as_view(), name="product_detail"),
    # path("add-to-cart/<int:pk>/", AddToCartView.as_view(), name="add_to_cart"),
    path("cart", MyCartView.as_view(), name="add_to_cart"),
]
