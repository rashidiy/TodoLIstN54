from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView

from accounts.forms import SignupForm


# Create your views here.
# def register(request):
#     register_form = SignupForm()
#     login_form = LoginForm()
#     if request.method == 'POST' and 'register' in request.POST:
#         register_form = SignupForm(data=request.POST)
#         if register_form.is_valid():
#             user = register_form.save()
#             messages.success(request, 'You have successfully registered.')
#             return redirect(reverse_lazy('register'))
#
#     if request.method == 'POST' and 'login' in request.POST:
#         login_form = LoginForm(data=request.POST)
#         if login_form.is_valid():
#             email = login_form.cleaned_data.get('username')
#             password = login_form.cleaned_data.get('password')
#             user = authenticate(email=email, password=password)
#             if user is not None:
#                 login(request, user)
#                 messages.success(request, 'You are now logged in')
#                 return redirect(reverse_lazy('home'))
#             else:
#                 messages.error(request, 'Invalid username or password')
#     context = {
#         'register_form': register_form,
#         'login_form': login_form,
#     }
#
#     return render(request, 'registration/login_signup.html', context)


class RegistrationView(CreateView):
    form_class = SignupForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('login')


