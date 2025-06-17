from django.shortcuts import render
from django.views.generic import ListView

from products.models import Product

# Create your views here.


class HomeView(ListView):
    template_name = "customer/home/home.html"
    queryset = Product.objects.prefetch_related("product_images").order_by(
        "-created_at"
    )[:5]
    context_object_name = "new_products"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["best_sell"] = Product.objects.filter(is_featured=True).order_by(
            "-created_at"
        )[:5]
        return context
