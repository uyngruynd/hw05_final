from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from posts.models import Comment, Follow, Group, Post, User


class GroupSerializer(serializers.ModelSerializer):
    """Описание сериализатора для модели Group"""

    class Meta:
        model = Group
        fields = '__all__'


class PostSerializer(serializers.ModelSerializer):
    """Описание сериализатора для модели Post"""
    author = SlugRelatedField(read_only=True, slug_field='username')

    class Meta:
        fields = ('id', 'text', 'pub_date', 'author', 'image', 'group')
        model = Post


class CommentSerializer(serializers.ModelSerializer):
    """Описание сериализатора для модели Comment"""
    author = SlugRelatedField(read_only=True, slug_field='username')

    class Meta:
        fields = '__all__'
        model = Comment
        read_only_fields = ('post',)


class FollowSerializer(serializers.ModelSerializer):
    """Описание сериализатора для модели Follow"""
    user = SlugRelatedField(read_only=True, slug_field='username',
                            default=serializers.CurrentUserDefault())
    following = SlugRelatedField(slug_field='username',
                                 queryset=User.objects.all())

    class Meta:
        fields = ('user', 'following',)
        model = Follow
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following'),
                message='Подписка на данного пользователя уже оформлена!'
            )
        ]

    def validate_following(self, value):
        if self.context.get('request').user == value:
            raise serializers.ValidationError(
                'Пользователь не может подписаться на самого себя!')
        return value
