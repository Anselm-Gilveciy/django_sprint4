from django.shortcuts import render


def about(request):
    """Функция для вызова страницы О проекте."""
    template_name = 'pages/about.html'
    title = 'Блогикум - Подробнее'
    context = {
        'title': title,
    }
    return render(request, template_name, context)


def rules(request):
    """Функция для вызова страницы Наши правила."""
    template_name = 'pages/rules.html'
    title = 'Блогикум - Правила'
    context = {
        'title': title,
    }
    return render(request, template_name, context)
