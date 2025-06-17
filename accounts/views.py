from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate, login
from django.views.generic import TemplateView

from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import CustomUserCreationForm
from django.shortcuts import redirect
from django.contrib.auth import get_user_model

User = get_user_model()


class WelcomePage(TemplateView):
    template_name = "customer/welcome_page/welcomepage.html"


class SignUpView(View):
    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, "customer/accounts/login.html", {"form": form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
        return render(request, "customer/accounts/login.html", {"form": form})


class LoginView(View):
    def get(self, request):
        return render(request, "customer/accounts/login.html")

    def post(self, request):
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = User.objects.filter(email=email).first()
        if user is not None:
            try:
                user = authenticate(request, email=email, password=password)
            except:
                user = None
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password")
            return redirect("login")
