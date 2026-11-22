from django.shortcuts import render, redirect
from . import models
from users.forms import UserForm, RegisterForm
import hashlib
from django.core.files.storage import FileSystemStorage
# from django.contrib.auth.decorators import login_required
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.sessions.backends.db import SessionStore
from django.shortcuts import redirect
# from django.contrib.auth import login as auth_login
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, StreamingHttpResponse
from files.loss_prediction import run
import json
import time
import threading
from django.core.cache import cache
from django.http import JsonResponse
import subprocess



def login_required(function):
    def _wrapped_view(request, *args, **kwargs):
        is_login = request.session.get('is_login')
        # print(111111, is_login)
        # request.session['user_id']
        # request.session['user_name']

        if is_login:
            return function(request)
        else:
            return redirect('/login/')

    return _wrapped_view


def hash_code(s, salt='Covid-19'):
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())
    # print(h.hexdigest())
    return h.hexdigest()


@login_required
def index(request):
    if request.method == 'POST':
        train_csvfile = request.FILES['train_csvfile']
        test_csvfile = request.FILES['test_csvfile']

        fs = FileSystemStorage()
        train_filename = fs.save(f"files/in/{train_csvfile.name}", train_csvfile)
        train_uploaded_file_url = fs.url(train_filename)

        test_filename = fs.save(f"files/in/{test_csvfile.name}", test_csvfile)
        test_uploaded_file_url = fs.url(test_filename)

        # 将 URL 存储在 session 中
        request.session['train_uploaded_file_url'] = train_uploaded_file_url
        request.session['test_uploaded_file_url'] = test_uploaded_file_url

        # 启动后台任务
        threading.Thread(target=process_files, args=(train_uploaded_file_url, test_uploaded_file_url, request.session.session_key)).start()

        return JsonResponse({'status': 'success'})

    else:
        data = dict(
            user_name=request.session.get('user_name')
        )
        return render(request, 'index.html', data)


def login(request):
    # if request.session.get('is_login', None):
    #     return redirect('/')
    if request.method == "POST":
        login_form = UserForm(request.POST)
        message = "请检查填写的内容！"
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            try:
                user = models.User.objects.get(username=username)
                if user.password == hash_code(password):
                    request.session['is_login'] = True
                    request.session['user_id'] = user.id
                    request.session['user_name'] = user.username
                    return redirect('/')  # 登录成功后跳转到主页
                else:
                    message = "密码不正确！"
                    print(message)
            except Exception as e:
                print(e)
                message = "用户不存在！"
        else:
            print(login_form.is_valid())
            return render(request, 'login.html', locals())

    login_form = UserForm()
    return render(request, 'login.html', locals())


def register(request):
    if request.method == "POST":
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            username = register_form.cleaned_data['username']
            password1 = register_form.cleaned_data['password1']
            password2 = register_form.cleaned_data['password2']
            email = register_form.cleaned_data['email']
            phone = register_form.cleaned_data['phone']
            age = register_form.cleaned_data.get('age')  # 使用 get 方法，如果字段不存在返回 None
            gender = register_form.cleaned_data.get('gender')

            if password1 != password2:
                return JsonResponse({'status': 'error', 'message': '两次输入的密码不同！'})

            if models.User.objects.filter(username=username).exists():
                return JsonResponse({'status': 'error', 'message': '用户名已经存在！'})

            if models.User.objects.filter(email=email).exists():
                return JsonResponse({'status': 'error', 'message': '该邮箱地址已被注册！'})

            new_user = models.User.objects.create(
                username=username,
                password=hash_code(password1),
                email=email,
                phone=phone,
                age=age,
                gender=gender
            )
            return JsonResponse({'status': 'success', 'message': '注册成功！'})
        else:
            errors = register_form.errors.as_json()
            return JsonResponse({'status': 'error', 'message': errors})

    return JsonResponse({'status': 'error', 'message': '不支持的请求方法'})

def logout(request):
    # if not request.session.get('is_login', None):
    #     # 如果没登录，也就没有登出一说
    #     return redirect('/')
    request.session.flush()
    # # 或者使用下面的方法
    # del request.session['is_login']
    # del request.session['user_id']
    # del request.session['user_name']
    return redirect('/')


# 进度条流式响应
def progress_stream(train_url, test_url):
    def progress_callback(value):
        return f"data: {json.dumps({'progress': value})}\n\n"

    try:
        output = run(train_url[1:], test_url[1:], progress_callback)
        yield f"data: {json.dumps({'progress': 100, 'result': output})}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"


def progress_views(request):
    from django.core.cache import cache

    def event_stream():
        session_key = request.session.session_key
        while True:
            progress = cache.get(f'progress_{session_key}')
            if progress is not None:
                yield f"data: {json.dumps({'progress': progress})}\n\n"

            result = cache.get(f'result_{session_key}')
            if result is not None:
                yield f"data: {json.dumps({'progress': 100, 'result': result})}\n\n"
                break

            error = cache.get(f'error_{session_key}')
            if error is not None:
                yield f"data: {json.dumps({'error': error})}\n\n"
                break

            time.sleep(1)  # 每秒检查一次进度

    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response


def process_files(train_url, test_url, session_key):
    from django.core.cache import cache

    def progress_callback(value):
        cache.set(f'progress_{session_key}', value, timeout=3600)

    try:
        output = run(train_url[1:], test_url[1:], progress_callback)
        cache.set(f'result_{session_key}', output, timeout=3600)
    except Exception as e:
        cache.set(f'error_{session_key}', str(e), timeout=3600)

def contact(request):
    return render(request, 'contact.html')

def classify(request):
    if request.method == 'POST':
        standard_csvfile = request.FILES['standard_csvfile']
        fs = FileSystemStorage()
        standard_filename = fs.save(f"files/in/{standard_csvfile.name}", standard_csvfile)
        standard_uploaded_file_url = fs.url(standard_filename)

        request.session['train_uploaded_file_url'] = standard_uploaded_file_url

        # 启动后台任务
        threading.Thread(target=process_files, args=(standard_uploaded_file_url, request.session.session_key)).start()

        return JsonResponse({'status': 'success'})

    else:
        data = dict(
            user_name=request.session.get('user_name')
        )
    return render(request, 'classify.html')

def run_code1(request):
    if request.method == 'POST':
        # 执行 code1.py
        try:
            result = subprocess.run(
                    ['python', 'files/risk_classification.py'],
                    check=True,
                    capture_output=True,
                    text=True
            )
            return JsonResponse({'status': 'success', 'output': result.stdout})
        except subprocess.CalledProcessError as e:
            return JsonResponse({'status': 'error', 'output': e.stderr})

    return JsonResponse({'status': 'failed', 'message': 'Only POST method is allowed.'})