from django.core.paginator import Paginator

NUM_REC: int = 10


def get_page_obj(request, post_list):
    """Функция возвращает объект пейджинатора."""
    paginator = Paginator(post_list, NUM_REC)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
