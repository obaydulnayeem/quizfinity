from django.urls import path
from . import views


urlpatterns = [
    # path('', views.quiz_list, name='quiz_list'),
    path('', views.quiz_list_new, name='quiz_list_new'),
    
    path('<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    
    path('result/', views.quiz_result, name='quiz_result'),
    
    path('progress/', views.user_progress, name='user_progress'),
    
    path('leaderboard/', views.leaderboards, name='leaderboards'),
    
    path('category/', views.category_list, name='category_list'),
    
    path('<int:quiz_id>/rate/', views.rate_quiz, name='rate_quiz'),
]
