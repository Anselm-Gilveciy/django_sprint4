from django.contrib import admin

from .models import Category, Location, Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ['title']
    list_filter = ('is_published', 'created_at')
    list_display = ['title', 'description']


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name']
    list_filter = ('is_published', 'created_at')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    search_fields = ['title', 'author']
    list_filter = ('created_at', 'author')
    list_display = ['title', 'author']


