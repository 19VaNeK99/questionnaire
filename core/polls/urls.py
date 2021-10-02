from django.urls import path, include

from rest_framework import routers
from . import views


router = routers.DefaultRouter()
router.register(r'polls', views.GetQuestion)


urlpatterns = [
    path('', include(router.urls)),
    path(r'accounts/register/', views.register, name='register'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('home', views.home, name='home'),
    path('create_test_set/', views.create_test_set, name='create_test_set'),
    path('create_question/<test_set_id>/', views.create_question, name='create_question'),
    #path('create_question/<test_set_id>/', views.CreateQuestion.as_view(test_set_id='test_set_id'), name='create_question'),
    path('start_test_set/<test_set_id>/', views.start_test_set, name='start_test_set'),
    path('start_test_set/<test_set_id>/<question_index>/', views.start_test_set, name='start_test_set'),
    path('results/<test_set_id>/', views.results, name='results'),
    path('vote/<question_id>/', views.vote, name='vote'),
    path('test_set/<test_set_id>/', views.test_set, name='test_set')
]