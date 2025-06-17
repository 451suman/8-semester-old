from django.shortcuts import render
from django.views.generic import ListView

from products.models import Category, Product
from django.db.models import Prefetch

# Create your views here.


class HomeView(ListView):
    template_name = "customer/home/home.html"
    queryset = Product.objects.prefetch_related("product_images").order_by(
        "-created_at"
    )[:5]
    context_object_name = "new_products"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Prefetch products along with their images
        product_qs = Product.objects.prefetch_related("product_images")
        context["categories"] = (
            Category.objects.prefetch_related(Prefetch("products", queryset=product_qs))
            .filter(arranged__isnull=False)
            .order_by("arranged")
        )

        return context
