from rest_framework.routers import DefaultRouter
from django.conf.urls import url
from apps.users.views import UserViewSet, GroupViewSet
from . import views

router = DefaultRouter()
router.register(r'users', UserViewSet, base_name='users')
router.register(r'groups', GroupViewSet, base_name='groups')
urlpatterns = [
    url(r'^users/current/$', views.CurrentUserView.as_view()),
]
urlpatterns += router.urls
