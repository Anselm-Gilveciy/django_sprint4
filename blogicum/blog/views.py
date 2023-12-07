from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .forms import CommentForm, PostForm, UserCreateForm
from .models import Category, Comment, Post

PAGINATION_OF_POSTS = 10

User = get_user_model()


def get_filtered_posts(posts):
    """Получение списка постов."""
    return posts.select_related(
        'category',
        'location',
        'author'
    ).filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    )


def get_comment_count(queryset):
    """Аннотация комментариев к постам."""
    return queryset.annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')


class UserUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля пользователя."""

    model = User
    form_class = UserCreateForm
    template_name = 'blog/user.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        username = self.request.user
        return reverse('blog:profile', kwargs={'username': username})


class UserDetailView(ListView):
    """Информация о пользователе (профиль пользователя)."""

    model = Post
    paginate_by = PAGINATION_OF_POSTS
    slug_url_kwargs = 'username'
    template_name = 'blog/profile.html'

    def get_object(self):
        return get_object_or_404(
            User,
            username=self.kwargs[self.slug_url_kwargs]
        )

    def get_context_data(self, **kwargs):
        return dict(
            **super().get_context_data(**kwargs),
            profile=self.get_object()
        )

    def get_queryset(self):
        author = self.get_object()
        posts = get_comment_count(author.posts)
        if author == self.request.user:
            return posts.filter(author=author)
        return get_filtered_posts(posts)


class HomeListView(ListView):
    """Главная страница."""

    model = Post
    template_name = 'blog/index.html'
    ordering = '-created_at'
    paginate_by = PAGINATION_OF_POSTS

    def get_queryset(self):
        return get_comment_count(
            get_filtered_posts(self.model.objects)
        )


class PostCreateView(LoginRequiredMixin, CreateView):
    """Создание поста."""

    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        username = self.request.user.username
        return reverse('blog:profile', kwargs={'username': username})


class PostDetailView(DetailView):
    """Просмотр поста в отдельной странице."""

    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'id'

    def get_object(self):
        post = get_object_or_404(
            Post,
            pk=self.kwargs[self.pk_url_kwarg]
        )
        if post.author != self.request.user:
            post = get_object_or_404(
                get_filtered_posts(self.model.objects),
                pk=self.kwargs[self.pk_url_kwarg],
            )
        return post

    def get_context_data(self, **kwargs):
        return dict(
            **super().get_context_data(**kwargs),
            comments=self.object.comments.select_related('author'),
            form=CommentForm()
        )


class PostUpdateDeleteMixin(UserPassesTestMixin):
    """Миксин для удаления и редактирования публикации."""

    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm
    pk_url_kwarg = 'post_id'

    def test_func(self):
        self.object = self.get_object()
        return self.request.user == self.object.author

    def handle_no_permission(self):
        return redirect(self.get_success_url())


class PostUpdateView(PostUpdateDeleteMixin, UpdateView):
    """Редактирование поста."""

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'id': self.kwargs[self.pk_url_kwarg]}
        )


class PostDeleteView(LoginRequiredMixin, PostUpdateDeleteMixin, DeleteView):
    """Удаление поста."""

    def get_success_url(self):
        return reverse('blog:index')

    def get_context_data(self, **kwargs):
        return dict(
            **super().get_context_data(**kwargs),
            form=self.form_class(instance=self.object)
        )


class CategoryListView(ListView):
    """Посты из отдельной категории."""

    template_name = 'blog/category.html'
    model = Post
    slug_url_kwarg = 'category_slug'
    paginate_by = PAGINATION_OF_POSTS

    def get_category_or_404(self):
        return get_object_or_404(
            Category,
            slug=self.kwargs[self.slug_url_kwarg],
            is_published=True
        )

    def get_queryset(self):
        category = self.get_category_or_404()
        return get_comment_count(get_filtered_posts(category.posts))

    def get_context_data(self, **kwargs):
        return dict(
            **super().get_context_data(**kwargs),
            category=self.get_category_or_404()
        )


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Создание комментария."""

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'post_id'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(
            Post, id=self.kwargs[self.pk_url_kwarg])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail', kwargs={'id': self.kwargs[self.pk_url_kwarg]})


class CommentMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Миксин для комментариев."""

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'comment_id'

    def test_func(self):
        self.object = self.get_object()
        return self.request.user == self.object.author


class CommentDeleteView(CommentMixin, DeleteView):
    """Удаление комментария."""


class CommentUpdateView(CommentMixin, UpdateView):
    """Изменение комментария."""
