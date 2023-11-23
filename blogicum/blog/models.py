from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

TITLE_LENGTH = 25


class BoolDateModel(models.Model):
    is_published = models.BooleanField(default=True,
                                       verbose_name='Опубликовано',
                                       help_text=(
                                           'Снимите галочку, чтобы '
                                           'скрыть публикацию.')
                                       )
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name='Добавлено')

    class Meta:
        abstract = True


class Category(BoolDateModel):
    title = models.CharField('Заголовок', max_length=256)
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text=(
            'Идентификатор страницы для URL;'
            ' разрешены символы латиницы, цифры, дефис '
            'и подчёркивание.'
        )
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title[:TITLE_LENGTH]


class Location(BoolDateModel):
    name = models.CharField(
        'Название места',
        max_length=256,
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name[:TITLE_LENGTH]


class Post(BoolDateModel):
    title = models.CharField('Название', max_length=256)
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text=(
            'Если установить дату и время '
            'в будущем — можно делать отложенные публикации.'
        )
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор публикации',
        on_delete=models.CASCADE,
        related_name='Posts',
    )
    location = models.ForeignKey(
        Location,
        verbose_name='Местоположение',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        on_delete=models.SET_NULL,
        null=True
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self):
        return self.title[:TITLE_LENGTH]


class Comment(models.Model):
    text = models.TextField('Комментарий')
    comment = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ('created_at',)
