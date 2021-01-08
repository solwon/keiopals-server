"""KPals URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path, include
from .views import *
from knox import views as knox_views

urlpatterns = [
    path('hello/', HelloAPI.as_view()),
    
    path('auth/register/', RegistrationAPI.as_view()),
    path('auth/login/', LoginAPI.as_view()),
    path('auth/info/', UserAPI.as_view()),
    path('api/auth/logout/', knox_views.LogoutView.as_view(), name='knox_logout'),
    
    path('board/posts/<int:no>', PostViewAPI.as_view()),
    path('board/posts/<int:no>/writecomment/', CommentAPI.as_view()),
    path('board/posts/<int:p_no>/deletecomment/<int:c_no>', CommentAPI.as_view()),
    path('board/write/', PostWriteAPI.as_view()),
    path('board/', PostListViewAPI.as_view({'get': 'list'})),
]