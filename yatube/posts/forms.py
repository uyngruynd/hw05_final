from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    """Форма создания нового поста на основе модели Post"""
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')


class CommentForm(forms.ModelForm):
    """Форма создания нового комментария на основе модели Comment"""
    class Meta:
        model = Comment
        fields = ('text',)
