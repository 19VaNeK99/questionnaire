from django.urls import path, include

from rest_framework import routers
from . import views


router = routers.DefaultRouter()
router.register(r'polls', views.GetQuestion)


urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('home', views.home, name='home'),
    path('create/', views.create, name='create'),
    path('results/<poll_id>/', views.results, name='results'),
    path('vote/<question_id>/', views.vote, name='vote'),
    path('test_set/<test_set_id>/', views.test_set, name='test_set')
]