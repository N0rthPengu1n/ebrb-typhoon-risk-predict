# typhoon_risk/users/urls.py
from django.urls import path
from . import views
from django.urls import path
from .views import classify, run_code1

urlpatterns = [
    path('classify/', classify, name='classify'),
    path('run_code1/', run_code1, name='run_code1'),  # 注册新视图
]

urlpatterns = [
]