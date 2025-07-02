from django.core.cache import cache
from django.views.generic import ListView, DetailView, TemplateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.db.models import Prefetch
from django.shortcuts import redirect, render, get_object_or_404

from products.forms import CheckoutForm
from .models import Cart, CartProduct, Order, Product, Category
from django.contrib import messages


class EcomMixin(object):
    def dispatch(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id")
        if cart_id:
            try:
                cart_obj = Cart.objects.get(id=cart_id)
                if request.user.is_authenticated:
                    cart_obj.user = (
                        request.user
                    )  # or cart_obj.customer if that's your field
                    cart_obj.save()
            except Cart.DoesNotExist:
                pass
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


class ProductListView(ListView):
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


from django.shortcuts import redirect, get_object_or_404
from django.views import View


class EmptyCartView(EcomMixin, View):
    def get(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id", None)
        if cart_id:
            try:
                cart = Cart.objects.get(id=cart_id)
                # Delete all related CartProduct items
                cart.cartproduct_set.all().delete()
                cart.total = 0
                cart.save()
                # Optionally clear cart_id from session
                del request.session["cart_id"]
            except Cart.DoesNotExist:
                # Cart not found, just pass or log
                pass
        return redirect("my-cart")


class ManageCartView(EcomMixin, View):
    def get(self, request, pk):
        print("this is manage cart section")
        # cp_id = self.kwargs["cp_id"]
        action = request.GET.get("action")
        cp_obj = CartProduct.objects.get(id=pk)
        cart_obj = cp_obj.cart
        if action == "inc":
            cp_obj.quantity += 1
            cp_obj.subtotal += cp_obj.rate
            cp_obj.save()
            cart_obj.total += cp_obj.rate
            cart_obj.save()
        elif action == "dcr":
            cp_obj.quantity -= 1
            cp_obj.subtotal -= cp_obj.rate
            cp_obj.save()
            cart_obj.total -= cp_obj.rate
            cart_obj.save()
            if cp_obj.quantity == 0:
                cp_obj.delete()

        elif action == "rmv":
            cart_obj.total -= cp_obj.subtotal
            cart_obj.save()
            # delete cartproduct products
            cp_obj.delete()

        else:
            pass

        # print (cp_id, action)
        return redirect("my-cart")


from django.urls import reverse_lazy


class CheckoutView(LoginRequiredMixin, CreateView):
    model = Order  # Define the model here
    template_name = "customer/checkout/checkout.html"
    form_class = CheckoutForm
    success_url = reverse_lazy("home")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
        else:
            cart_obj = None

        context["cart"] = cart_obj
        return context

    def form_valid(self, form):
        cart_id = self.request.session.get("cart_id")
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)

            # Check if an order already exists for this cart
            existing_order = Order.objects.filter(cart=cart_obj).first()
            if existing_order:
                messages.warning(
                    self.request, "An order has already been placed for this cart."
                )
                return redirect(self.success_url)
            form.instance.customer = self.request.user.customer
            form.instance.cart = cart_obj
            form.instance.subtotal = cart_obj.total
            form.instance.discount = 0
            form.instance.total = cart_obj.total
            form.instance.order_status = "Order Received"

            # Clear cart_id from session
            del self.request.session["cart_id"]

            messages.success(self.request, "Order has been received")
        else:
            return redirect("home")

        return super().form_valid(form)
