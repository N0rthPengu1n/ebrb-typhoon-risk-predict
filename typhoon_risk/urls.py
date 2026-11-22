"""
URL configuration for typhoon_risk project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from users import views as users_views

urlpatterns = [
    # path('', include('users.urls')),  # 函数 include() 允许引用其它 URLconfs
    path('admin/', admin.site.urls),
    path('captcha', include('captcha.urls')),
    path('', users_views.index),  # 确保路径与视图重定向匹配
    path('login/', users_views.login, name="login"),
    path('register/', users_views.register, name="register"),
    path('logout/', users_views.logout, name="logout"),
    path('progress/', users_views.progress_views, name="progress"),
    path('contact/', users_views.contact, name='contact'),
    path('classify/', users_views.classify, name='classify')
]