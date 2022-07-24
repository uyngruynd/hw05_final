from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render

from .utils import get_page_obj
from .models import Group, Post, User, Follow
from .forms import PostForm, CommentForm


def index(request):
    """Функция-обработчик для главной страницы."""
    post_list = Post.objects.select_related('group')
    page_obj = get_page_obj(request, post_list)
    context = {
        'page_obj': page_obj,
        'index': True,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Функция-обработчик для страницы группы."""
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    page_obj = get_page_obj(request, post_list)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def post_detail(request, post_id):
    """Функция-обработчик для страницы поста."""
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    form = CommentForm()
    context = {
        'post': post,
        'comments': comments,
        'form': form,
    }
    return render(request, 'posts/post_detail.html', context)


def profile(request, username):
    """Функция-обработчик для страницы профиля пользователя."""
    author = get_object_or_404(User, username=username)
    is_following = Follow.objects.values_list("author_id", flat=True).filter(
        user_id=request.user.id, author_id=author.id).exists()
    post_list = author.posts.all()
    page_obj = get_page_obj(request, post_list)
    context = {
        'page_obj': page_obj,
        'author': author,
        'is_following': is_following,
        'my_profile': request.user == author,
    }
    return render(request, 'posts/profile.html', context)


@login_required
def post_create(request):
    """Функция-обработчик для создания нового поста."""
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if request.method == 'POST':
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            return redirect('posts:profile', username=request.user)
        return render(request, 'posts/create_post.html', {
            'form': form,
        }
                      )
    return render(request, 'posts/create_post.html', {
        'form': form,
    }
                  )


@login_required
def post_edit(request, post_id):
    """Функция-обработчик для редактирования существующего поста."""
    post = get_object_or_404(Post, id=post_id, author_id=request.user.id)

    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post_id)

    if request.method == 'POST':
        form = PostForm(
            request.POST,
            files=request.FILES or None,
            instance=post
        )
        if form.is_valid():
            form.save()
        return redirect('posts:post_detail', post_id=post_id)

    form = PostForm(instance=post)
    context = {'form': form,
               'is_edit': True,
               'post_id': post_id,
               }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    """Функция-обработчик добавления комментария к посту."""
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Функция-обработчик для страницы подписок."""
    post_list = Post.objects.select_related('group').filter(
        author__following__user=request.user)
    page_obj = get_page_obj(request, post_list)
    context = {
        'page_obj': page_obj,
        'follow': True,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Функция-обработчик процедуры подписки."""
    author = get_object_or_404(User, username=username)
    try:
        if author == request.user:
            raise IntegrityError
        Follow.objects.create(user_id=request.user.id, author_id=author.id)
    except IntegrityError:
        return redirect('posts:follow_error')
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    """Функция-обработчик процедуры отписки."""
    author = get_object_or_404(User, username=username)
    follow_qs = Follow.objects.filter(author=author, user=request.user)
    if follow_qs.exists():
        follow_qs.delete()
    return redirect('posts:follow_index')


def follow_error(request):
    """Функция-обработчик ошибки процедуры подписки."""
    return render(request, 'posts/error.html',
                  context={
                      'message': 'Ошибка при подписке!',
                  }
                  )
