from django.urls import include, path

from products.views import (
    CheckoutView,
    CustomerOrderDetailView,
    EmptyCartView,
    HomeView,
    OrderListView,
    ProductDetailView,
    ProductListView,
    MyCartView,
    AddToCartView,
    ManageCartView,
)

urlpatterns = [
    path("home/", HomeView.as_view(), name="home"),
    # product
    path("list/", ProductListView.as_view(), name="product_list"),
    path("detail/<str:slug>/", ProductDetailView.as_view(), name="product_detail"),
    # cart
    path("add-to-cart/<int:pk>/", AddToCartView.as_view(), name="add_to_cart"),
    path("cart/", MyCartView.as_view(), name="my-cart"),
    path("empty-cart/", EmptyCartView.as_view(), name="empty-cart"),
    path("manage-cart/<int:pk>/", ManageCartView.as_view(), name="managecart"),
    # checkout
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    # order
    path("order-list/", OrderListView.as_view(), name="order-list"),
    path("order/<int:pk>/", CustomerOrderDetailView.as_view(), name="order_detail"),
]
