from http import HTTPStatus

from django.shortcuts import render


def page_not_found(request, exception):
    """Функция-обработчик для страницы 404."""
    return render(request, 'core/404.html', {'path': request.path},
                  status=HTTPStatus.NOT_FOUND)


def csrf_failure(request, reason=''):
    """Функция-обработчик для страницы 403."""
    return render(request, 'core/403csrf.html')


def server_error(request):
    """Функция-обработчик для страницы 500."""
    return render(request, 'core/500.html',
                  status=HTTPStatus.INTERNAL_SERVER_ERROR)
