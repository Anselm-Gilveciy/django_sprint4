from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .forms import CommentForm, PostForm, UserCreateForm
from .models import Category, Comment, Post

PUB_DATE = 5
PAGINAT = 10

User = get_user_model()


def get_object_or():
    code = Post.objects.select_related(
        'author',
        'category',
        'location'
    ).filter(
        pub_date__lte=timezone.datetime.now(),
        is_published=True,
        category__is_published=True
    )
    return code


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserCreateForm
    template_name = 'blog/user.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        username = self.request.user
        return reverse('blog:profile', kwargs={'username': username})


def get_query_all_posts(model):
    return model.select_related(
        'category',
        'location',
        'author'
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')


class UserDetailView(ListView):
    model = Post
    author = None
    paginate_by = 10
    queryset = get_query_all_posts(model.objects)
    slug_url_kwargs = 'username'
    template_name = 'blog/profile.html'

    def get_object(self):
        return get_object_or_404(
            User,
            username=self.kwargs[self.slug_url_kwargs]
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_object()
        return context

    def get_queryset(self):
        self.author = self.get_object()
        if self.author == self.request.user:
            return self.queryset.filter(author=self.author)
        return super().get_queryset().filter(
            author=self.author, is_published=True)


class HomeListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = PAGINAT

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self):
        return Post.objects.prefetch_related(
            'location',
            'category',
            'author',
        ).filter(
            pub_date__date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        ).order_by(
            '-pub_date'
        ).annotate(
            comment_count=Count('comments')
        ).order_by(
            '-pub_date'
        )


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        username = self.request.user
        return reverse('blog:profile', kwargs={'username': username})


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm

    def dispatch(self, request, *args, **kwargs):
        get_object_or_404(Post, pk=kwargs['pk'], author=request.user)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    template_name = 'blog/create.html'
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        get_object_or_404(Post, pk=kwargs['pk'], author=request.user)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def dispatch(self, request, *args, **kwargs):
        get_object_or_404(Post, pk=kwargs['pk'], author=request.user)
        return super().dispatch(request, *args, **kwargs)


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    success_url = reverse_lazy('blog:index')

    def dispatch(self, request, *args, **kwargs):
        get_object_or_404(Post, pk=kwargs['pk'], author=request.user)
        return super().dispatch(request, *args, **kwargs)


class CategoryListView(ListView):
    template_name = 'blog/category.html'
    model = Post
    context_object_name = 'category_list'
    paginate_by = PAGINAT

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['slugname'],
            is_published=True
        )
        queryset = Post.objects.filter(
            category_id=self.category.pk,
            pub_date__date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        ).annotate(comment_count=Count('comments')).order_by('-pub_date')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            slug=self.kwargs['slugname'],
            is_published=True,
        )
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    object = None
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'post_id'
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        self.post_object = get_object_or_404(Post, pk=kwargs[self.pk_url_kwargs])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_object
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs[self.pk_url_kwarg]})