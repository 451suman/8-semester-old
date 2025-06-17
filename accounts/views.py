# views.py

from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate, login
from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy
from accounts.models import CustomUser
from .forms import CustomUserCreationForm, CustomerLoginForm


class WelcomePage(TemplateView):
    template_name = "customer/welcome_page/welcomepage.html"


class CustomerSignUpView(View):
    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, "customer/accounts/signup.html", {"form": form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("customer_login")
        return render(request, "customer/accounts/signup.html", {"form": form})


class CustomerLoginView(FormView):
    template_name = "customer/accounts/login.html"
    form_class = CustomerLoginForm
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password"]
        user = authenticate(self.request, email=email, password=password)

        if user is None:
            return self.form_invalid(form, message="Invalid email or password")

        if not user.is_verified:
            return self.form_invalid(form, message="Account not verified")

        if user.is_active:
            login(self.request, user)
            return super().form_valid(form)
        else:
            return self.form_invalid(form, message="Account is inactive")

    def form_invalid(self, form, message=None):
        return render(
            self.request,
            self.template_name,
            {"form": form, "error": message},
        )
