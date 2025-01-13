import json
import uuid
from http.cookies import SimpleCookie

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, View
from todo.models import Todo


class TodoListView(ListView):
    model = Todo
    context_object_name = 'todos'
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            user = self.request.user
            context['todos'] = Todo.objects.filter(user=user)
        else:
            todos_cookie = self.request.COOKIES.get('todos', '[]')
            try:
                todos_list = json.loads(todos_cookie)
            except json.JSONDecodeError:
                todos_list = []
            context['todos'] = todos_list
        return context


class CustomView(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.content_type == "application/json":
            return JsonResponse({'status': 'failed', 'error': 'Unsupported content-type'})
        if not request.user.is_authenticated:
            return JsonResponse({'status': 'failed', 'error': 'Not authenticated'})
        return super().dispatch(request, *args, **kwargs)


@method_decorator(csrf_exempt, name='dispatch')
class TodoCreate(CustomView):
    http_method_names = ['post']

    def post(self, request: WSGIRequest, *args, **kwargs):
        title = json.loads(request.body).get('title')
        if not title:
            return JsonResponse({'status': 'failed', 'error': 'Missed key named "title"'}, status=400)
        todo = Todo.objects.create(user=request.user, title=title)
        return JsonResponse({'status': 'success', 'id': todo.id})


@method_decorator(csrf_exempt, name='dispatch')
class TodoConfirm(CustomView):
    http_method_names = ['post']

    def post(self, request: WSGIRequest, *args, **kwargs):
        obj_id = json.loads(request.body).get('id')
        if not obj_id:
            return JsonResponse({'status': 'failed', 'error': 'Missed key named "id"'}, status=400)
        try:
            todo = Todo.objects.get(id=obj_id)
        except Todo.DoesNotExist:
            return JsonResponse({'status': 'failed', 'error': 'Object not found'}, status=404)
        todo.completed = not todo.completed
        todo.save()
        return JsonResponse({'status': 'success', 'id': todo.id})


@method_decorator(csrf_exempt, name='dispatch')
class TodoDelete(CustomView):
    http_method_names = ['post']

    def post(self, request: WSGIRequest, *args, **kwargs):
        obj_id = json.loads(request.body).get('id')
        if not obj_id:
            return JsonResponse({'status': 'failed', 'error': 'Missed key named "id"'}, status=400)
        try:
            todo = Todo.objects.get(id=obj_id)
        except Todo.DoesNotExist:
            return JsonResponse({'status': 'failed', 'error': 'Object not found'}, status=404)
        todo.delete()
        return JsonResponse({'status': 'success', 'id': todo.id})
