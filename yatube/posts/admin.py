from django.contrib import admin

from .models import Group, Post


class PostAdmin(admin.ModelAdmin):
    """Настройки отображения модели в интерфейсе админки."""
    list_display = ('pk',
                    'text',
                    'pub_date',
                    'author',
                    'group'
                    )
    search_fields = ('text',)
    list_filter = ('pub_date',)
    list_editable = ('group',)
    empty_value_display = '-пусто-'


admin.site.register(Post, PostAdmin)
admin.site.register(Group)
