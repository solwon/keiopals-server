from django.contrib.auth.models import User
from rest_framework import serializers
from rest_main.models import Profile, Post, Comment
from django.contrib.auth import authenticate


# class ProfileSerializer(serializers.ModelSerializer):
#     username = serializers.ReadOnlyField(source='user.username')
#     first_name = serializers.ReadOnlyField(source='user.first_name')
#     last_name = serializers.ReadOnlyField(source='user.last_name')
#     email = serializers.ReadOnlyField(source='user.email')
#
#     class Meta:
#         model = Profile
#         fields = ('username', 'first_name', 'last_name', 'email', 'school')


class ProfileSerializer(serializers.Serializer):
    school = serializers.CharField(max_length=255)


class CreateUserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password', 'profile']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        user = User.objects.create(**validated_data)
        user.set_password(validated_data.pop('password'))
        Profile.objects.create(user=user, **profile_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class InfoSerializer(serializers.ModelSerializer):
    school = serializers.ReadOnlyField(source='profile.school')

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'school']


class LoginUserSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Unable to log in with these credentials")


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(source='author.user')

    class Meta:
        model = Comment
        fields = ['no', 'author', 'timestamp', 'content']


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(source='author.user')
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['no', 'title', 'author', 'timestamp', 'content', 'comments']


class PostWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['title', 'content']


class CommentWriteSerializer(serializers.ModelSerializer):
    author = UserSerializer(source='author.user', read_only=True)

    class Meta:
        model = Comment
        fields = ['author', 'content']


class PostListSerializer(serializers.ModelSerializer):
    number = serializers.IntegerField(source='no')
    author = UserSerializer(source='author.user')
    comments_num = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['number', 'title', 'author', 'comments_num']

    def get_comments_num(self, obj):
        return obj.comments.count()
