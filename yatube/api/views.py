from rest_framework import filters, mixins, permissions, viewsets
from django.shortcuts import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination

from posts.models import Group, Post
from .permissions import IsAuthorOrReadOnly
from .serializers import (CommentSerializer, FollowSerializer, GroupSerializer,
                          PostSerializer, )


class PostViewSet(viewsets.ModelViewSet):
    """Описание вьюсета для работы с моделью Post"""
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsAuthorOrReadOnly,)
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = ('id', 'text', 'pub_date',)
    ordering = ('id',)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """Описание вьюсета для работы с моделью Group"""
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class CommentViewSet(viewsets.ModelViewSet):
    """Описание вьюсета для работы с моделью Comment"""
    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsAuthorOrReadOnly,)

    def get_queryset(self):
        post = get_object_or_404(Post, pk=self.kwargs.get("post_id"))
        new_queryset = post.comments.all()
        return new_queryset

    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs.get("post_id"))
        serializer.save(author=self.request.user, post=post)


class FollowViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    """Описание вьюсета для работы с моделью Follow."""
    serializer_class = FollowSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('following__username',)

    def get_queryset(self):
        return self.request.user.follower.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
