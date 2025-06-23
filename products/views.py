from django.core.cache import cache
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.db.models import Prefetch
from django.shortcuts import render, get_object_or_404
from .models import Product, Category


class HomeView(ListView):
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
            # cache.set("new_products", new_products, 60)
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
            # cache.set("categories", categories, 60)

        context["categories"] = categories
        return context


# Query 1: Get latest 5 Product objects
# Query 2: Get product_images for those 5 products
# Let’s say 5 categories are returned. Django will:
# Query 3: Get Category objects
# Query 4: Get related Product objects (for those categories)
# Query 5: Get product_images for products in those categories
# Query 6: Session query (django_session)
# Query 7: Auth user query (accounts_customuser)


class ProductListView(LoginRequiredMixin, ListView):
    template_name = "customer/product/product_list.html"
    queryset = Product.objects.prefetch_related("product_images").order_by(
        "-created_at"
    )
    context_object_name = "products"
    paginate_by = 9


class ProductDetailView(View):
    def get(self, request, slug):
        product = get_object_or_404(
            Product.objects.prefetch_related("product_images"),
            slug=slug,
            is_active=True,
        )
        return render(
            request,
            "customer/product_details/product_Details.html",
            {"product": product},
        )
