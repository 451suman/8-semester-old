from django.core.cache import cache
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.db.models import Prefetch
from django.shortcuts import redirect, render, get_object_or_404
from .models import Cart, CartProduct, Product, Category


class EcomMixin(object):
    def dispatch(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id")
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            if request.user.is_authenticated and request.user.CustomUser:
                cart_obj.CustomUser = request.user.CustomUser
                cart_obj.save()
        return super().dispatch(request, *args, **kwargs)


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


class AddToCartView(EcomMixin, View):
    def get(self, request, pk):
        # Get product
        product_obj = Product.objects.get(id=pk)
        # Check if cart exists
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            # Check if the product is already in the cart
            this_product_in_cart = cart_obj.cartproduct_set.filter(product=product_obj)

            # Items already in cart
            if this_product_in_cart.exists():
                cartproduct = this_product_in_cart.last()
                cartproduct.quantity += 1
                cartproduct.subtotal += product_obj.current_price
                cartproduct.save()
                cart_obj.total += product_obj.current_price
                cart_obj.save()

            # New item is added in cart
            else:
                cartproduct = CartProduct.objects.create(
                    cart=cart_obj,
                    product=product_obj,
                    rate=product_obj.current_price,
                    quantity=1,
                    subtotal=product_obj.current_price,
                )
                cart_obj.total += product_obj.current_price
                cart_obj.save()
        else:
            cart_obj = Cart.objects.create(total=0)

            cartproduct = CartProduct.objects.create(
                cart=cart_obj,
                product=product_obj,
                rate=product_obj.current_price,
                quantity=1,
                subtotal=product_obj.current_price,
            )
            cart_obj.total += product_obj.current_price
            cart_obj.save()
            request.session["cart_id"] = cart_obj.id  # Save cart_id in session

        # Redirect to the cart view
        return redirect("my-cart")


class MyCartView(EcomMixin, TemplateView):
    template_name = "customer/cart/cart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id")

        cart = None
        if cart_id:
            try:
                cart = Cart.objects.get(id=cart_id)
            except Cart.DoesNotExist:
                cart = None  # cart not found, treat as no cart

        context["cart"] = cart
        return context


class EmpytCartView(EcomMixin, View):
    def get(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id", None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
            # select all cart product and delete using cart id
            cart.cartproduct_set.all().delete()
            cart.total = 0
            cart.save()
        return redirect("my-cart")
