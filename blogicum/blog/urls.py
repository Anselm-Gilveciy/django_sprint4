from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path(
        '',
        views.HomeListView.as_view(),
        name='index'
    ),
    path(
        'edit_profile/',
        views.UserUpdateView.as_view(),
        name='edit_profile'
    ),
    path(
        'posts/create/',
        views.PostCreateView.as_view(),
        name='create_post'
    ),
    path(
        'posts/<int:pk>/edit/',
        views.PostUpdateView.as_view(),
        name='edit_post'
    ),
    path(
        'posts/<int:pk>/edit_comment/<comment_id>/',
        views.CommentUpdateView.as_view(),
        name='edit_comment'
    ),
    path(
        'posts/<int:pk>/delete_comment/<comment_id>/',
        views.CommentDeleteView.as_view(),
        name='delete_comment'
    ),
    path(
        'posts/<int:pk>/delete/',
        views.PostDeleteView.as_view(),
        name='delete_post'
    ),
    path(
        'posts/<int:post_id>/comment/',
        views.CommentCreateView.as_view(),
        name='add_comment'
    ),
    path(
        'profile/<slug:username>/',
        views.UserDetailView.as_view(),
        name='profile'
    ),
    path(
        'posts/<int:pk>/',
        views.PostDetailView.as_view(),
        name='post_detail'
    ),
    path('category/<slug:slugname>/',
         views.CategoryListView.as_view(),
         name='category_posts'),
]
