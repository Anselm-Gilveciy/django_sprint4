from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.HomeListView.as_view(), name='index'),
    path('<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('profile/<slug:username_slug>/', views.UserDetailView.as_view(), name='profile'),
    path('posts/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path(
        'category/<slug:category_slug>/',
        views.category_posts,
        name='category_posts'
    ),
    path('posts/create/', views.PostCreateView.as_view(), name='create_post')
]
