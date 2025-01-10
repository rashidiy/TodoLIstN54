from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView


class ToDoLoginView(LoginView):
    template_name = 'login.html'
    success_url = '/'


class ToDoRegisterView(CreateView):
    template_name = 'register.html'
    form_class = UserCreationForm
    success_url = '/'

    def form_valid(self, form):
        print(form.instance)
        if email := self.request.POST.get('email'):
            form.instance.email = email
            if User.objects.filter(email=email).exists():
                form.fields['email'] = True
                form.add_error('email', 'Email already registered!')
                return self.form_invalid(form)
        return super().form_valid(form)

    def form_invalid(self, form):
        if email := self.request.POST.get('email'):
            form.instance.email = email
        return super().form_invalid(form)
