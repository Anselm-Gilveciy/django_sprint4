from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView, ListView, DetailView, UpdateView, DeleteView
)

from .forms import PostForm, CommentForm
from .models import Category, Post, Comment

PUB_DATE = 5
PAGIN = 10

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


class UserUpdateView(UpdateView):
    pass


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
    queryset = get_query_all_posts(model.objects)
    template_name = 'blog/profile.html'

    def get_query_all_posts(model):
        return model.select_related(
            'category',
            'location',
            'author'
        ).annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')

    def get_object(self):
        return get_object_or_404(
            User,
            username=self.kwargs['username']
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
    paginate_by = PAGIN

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
        ).order_by('-pub_date')


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm
    success_url = reverse_lazy('blog:profile')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


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


def category_posts(request, category_slug):
    template_name = 'blog/category.html'
    category = get_object_or_404(Category, slug=category_slug,
                                 is_published=True)
    posts = Post.objects.select_related(
        'author',
        'category',
        'location'
    ).filter(
        pub_date__lte=timezone.datetime.now(),
        category__slug__contains=category_slug,
        is_published=True
    )
    context = {
        'post_list': posts,
        'category': category
    }
    return render(request, template_name, context)


@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        com = form.save(commit=False)
        com.author = request.user
        com.post = post
        com.save()
    return redirect('blog:post_detail', pk=pk)
