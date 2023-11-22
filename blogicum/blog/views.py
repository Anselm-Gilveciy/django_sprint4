from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from .models import Category, Post

PUB_DATE = 5


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


def index(request):
    template_name = 'blog/index.html'
    post_list = get_object_or().order_by('-pub_date')[:PUB_DATE]
    context = {
        'post_list': post_list
    }
    return render(request, template_name, context)


def post_detail(request, id):
    template_name = 'blog/detail.html'
    detail = get_object_or_404(
        get_object_or(),
        pk=id
    )
    context = {'post': detail}
    return render(request, template_name, context)


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
