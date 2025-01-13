import json
import uuid
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, View
from todo.models import Todo


class TodoListView(ListView):
    model=Todo
    context_object_name = 'object_list'
    template_name = 'index.html'
    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            user = self.request.user
            context['object_list']=Todo.objects.filter(user=user)
        else:
            # Cookie'dagi todo ma'lumotlarini olish
            todos_cookie = self.request.COOKIES.get('todos', '[]')
            try:
                # Cookie'dagi JSON formatdagi stringni Python listga aylantirish
                todos_list = json.loads(todos_cookie)
            except json.JSONDecodeError:
                todos_list = []
            context['object_list'] = todos_list
        return context



class CustomView(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.content_type == "application/json":
            return JsonResponse({'status': 'failed', 'error': 'Unsupported content-type'})
        return super().dispatch(request, *args, **kwargs)


@method_decorator(csrf_exempt, name='dispatch')
class TodoCreate(CustomView):
    http_method_names = ['post']
    def post(self, request: WSGIRequest, *args, **kwargs):
        title = json.loads(request.body).get('title')
        if not title:
            return JsonResponse({'status': 'failed', 'error': 'Missed key named "title"'}, status=400)
        if request.user.is_authenticated:
            todo = Todo.objects.create(title=title, user=request.user)
            return JsonResponse({'status': 'success', 'id': todo.id})
        #Anonim foydalanuvchi uchun cookie orqali saqlash
        todos = json.loads(request.COOKIES.get('todos', '[]'))
        todo_id = str(uuid.uuid4())
        todos.append({'id': todo_id, 'title':title, 'completed':False})
        response = JsonResponse({'status': 'success', 'message': 'Todo added to cookies'})
        response.set_cookie('todos', json.dumps(todos), max_age=60 * 60 * 24 * 7)  # 1 hafta saqlanadi
        return response



@method_decorator(csrf_exempt, name='dispatch')
class TodoConfirm(CustomView):
    http_method_names = ['post']
    def post(self, request: WSGIRequest, *args, **kwargs):
        obj_id = json.loads(request.body).get('id')
        if not obj_id:
            return JsonResponse({'status': 'failed', 'error': 'Missed key named "id"'}, status=400)
        if request.user.is_authenticated:
            try:
                todo = Todo.objects.get(id=obj_id)
            except Todo.DoesNotExist:
                return JsonResponse({'status': 'failed', 'error': 'Object not found'}, status=404)
            todo.completed = not todo.completed
            todo.save()
            return JsonResponse({'status': 'success', 'id': todo.id})

        todos = json.loads(request.COOKIES.get('todos', '[]'))
        updated = False  # Yangilanganligini tekshirish uchun flag

        for todo in todos:
            if todo.get('id') == obj_id:  # id ni integer tipida solishtirish
                todo['completed'] = not todo['completed']  # completed qiymatini o‘zgartirish
                updated = True
                break

        if not updated:
            return JsonResponse({'status': 'failed', 'error': 'Object not found in cookies'}, status=404)

        # Yangilangan todos ro‘yxatini cookie-ga yozish
        response = JsonResponse({'status': 'success', 'message': 'Todo updated'})
        response.set_cookie('todos', json.dumps(todos), max_age=60 * 60 * 24 * 7)
        return response


@method_decorator(csrf_exempt, name='dispatch')
class TodoDelete(CustomView):
    http_method_names = ['post']

    def post(self, request: WSGIRequest, *args, **kwargs):
        obj_id = json.loads(request.body).get('id')
        if not obj_id:
            return JsonResponse({'status': 'failed', 'error': 'Missed key named "id"'}, status=400)
        if request.user.is_authenticated:
            try:
                todo = Todo.objects.get(id=obj_id)
            except Todo.DoesNotExist:
                return JsonResponse({'status': 'failed', 'error': 'Object not found'}, status=404)
            todo.delete()
            return JsonResponse({'status': 'success', 'id': todo.id})
        todos = json.loads(request.COOKIES.get('todos', '[]'))
        for todo in todos:
            if todo.get('id')==obj_id:
                todos.remove(todo)
                break
        response = JsonResponse({'status': 'success', 'message': 'Todo deleted from cookies'})
        response.set_cookie('todos', json.dumps(todos), max_age=60 * 60 * 24 * 7)  # 1 hafta saqlanadi
        return response

