from django.contrib import admin

from .models import Category, Location, Post


class CategoryAdmin(admin.ModelAdmin):
    search_fields = ['title']
    list_filter = ('is_published', 'created_at')
    list_display = ['title', 'description']


class LocationAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name']
    list_filter = ('is_published', 'created_at')


class PostAdmin(admin.ModelAdmin):
    search_fields = ['title', 'author', 'location', 'category']
    list_filter = ('is_published', 'created_at')
    list_display = ['title', 'author', 'location', 'category']


admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Post, PostAdmin)
