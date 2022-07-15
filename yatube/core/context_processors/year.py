import datetime


def year(request):
    """Возвращает значение, соответствующее текущему году."""
    return {
        'year': datetime.datetime.now().year
    }
