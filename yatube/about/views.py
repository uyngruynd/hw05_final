from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    """Статический view-класс для вывода страницы "Об авторе"."""
    template_name = 'about/author.html'


class AboutTechView(TemplateView):
    """Статический view-класс для вывода страницы "Технологии"."""
    template_name = 'about/tech.html'
