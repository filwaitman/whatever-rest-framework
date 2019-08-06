import django
from django.views.decorators.csrf import csrf_exempt

from . import api

if django.VERSION < (2, 0):
    from django.conf.urls import url

    urlpatterns = [
        url(r'^$', csrf_exempt(api.UserListAPI.as_view()), name='users-list'),
        url(r'^(?P<pk>[0-9]+)/$', csrf_exempt(api.UserDetailAPI.as_view()), name='users-detail'),
        url(r'^(?P<action>\w+)/$', csrf_exempt(api.UserListCustomAPI.as_view()), name='users-list-custom'),
        url(r'^(?P<pk>[0-9]+)/(?P<action>\w+)/$', csrf_exempt(api.UserDetailCustomAPI.as_view()), name='users-detail-custom'),
    ]

else:
    from django.urls import path

    urlpatterns = [
        path('', csrf_exempt(api.UserListAPI.as_view()), name='users-list'),
        path('<int:pk>/', csrf_exempt(api.UserDetailAPI.as_view()), name='users-detail'),
        path('<str:action>/', csrf_exempt(api.UserListCustomAPI.as_view()), name='users-list-custom'),
        path('<int:pk>/<str:action>/', csrf_exempt(api.UserDetailCustomAPI.as_view()), name='users-detail-custom'),
    ]
