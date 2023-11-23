from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView, ListView, DetailView
)

from .forms import PostForm, CommentForm
from .models import Category, Post

PUB_DATE = 5
PAGIN = 10

User = get_user_model()


class Edit(ListView):
    pass


class UserDetailView(ListView):
    model = Post
    fields = '__all__'
    template_name = 'blog/profile.html'

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
        return Post.objects.filter(author__username=self.kwargs.get("username"))



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
            'author',).filter(
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


def profile(request):
    template_name = 'blog/profile.html'
    return render(request, template_name)


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Записываем в переменную form пустой объект формы.
        context['form'] = CommentForm()
        # Запрашиваем все поздравления для выбранного дня рождения.
        context['comments'] = (
            # Дополнительно подгружаем авторов комментариев,
            # чтобы избежать множества запросов к БД.
            self.object.comments.select_related('author')
        )
        return context


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


# class PostUpdateView(LoginRequiredMixin, UpdateView):
#     form_class = BlogForm
#     template_name = 'blog/create.html'
#     pk_url_kwarg = 'post_id'
#     queryset = Post.objects.all().select_related(
#         'author',
#         'location',
#         'category',
#     ).order_by('-pub_date')
#
#     def get_success_url(self):
#         return reverse_lazy(
#             'blog:post_detail',
#             kwargs={'post_id': self.kwargs['post_id']}
#         )
#
#     def dispatch(self, request, *args, **kwargs):
#         self.post_obj = get_object_or_404(Post, pk=kwargs['post_id'])
#         if self.post_obj.author != request.user:
#             return redirect('blog:post_detail', self.kwargs.get('post_id'))
#         return super().dispatch(request, *args, **kwargs)


@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.comment = comment
        comment.save()
    return redirect('blog:detail', pk=pk)