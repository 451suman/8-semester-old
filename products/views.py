from django.core.cache import cache
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch
from .models import Product, Category


class HomeView(LoginRequiredMixin, ListView):
    template_name = "customer/home/home.html"
    model = Product
    context_object_name = "new_products"

    def get_queryset(self):
        # Try to get cached new_products queryset
        new_products = cache.get("new_products")
        if not new_products:
            new_products = Product.objects.prefetch_related("product_images").order_by(
                "-created_at"
            )[:5]
            cache.set("new_products", new_products, 60)  # cache for 5 minutes
        return new_products

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Try to get cached categories
        categories = cache.get("categories")
        if not categories:
            product_qs = Product.objects.prefetch_related("product_images")
            categories = (
                Category.objects.prefetch_related(
                    Prefetch("products", queryset=product_qs)
                )
                .filter(arranged__isnull=False)
                .order_by("arranged")
            )
            cache.set("categories", categories, 60)  # cache for 5 minutes

        context["categories"] = categories
        return context
