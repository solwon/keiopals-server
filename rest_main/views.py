from django.http import Http404
from rest_framework import viewsets, permissions, generics, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from knox.models import AuthToken
from .serializers import *
from .models import Profile

import datetime


class HelloAPI(APIView):
    def get(self, request):
        return Response('Hello, world!')


class RegistrationAPI(generics.GenericAPIView):
    serializer_class = CreateUserSerializer

    def post(self, request, *args, **kwargs):
        if len(request.data['username']) < 6 or len(request.data['password']) < 8:
            body = {'message': 'short field'}
            return Response(body, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.set_password(request.data['password'])
        user.save()
        token_obj = AuthToken.objects.create(user)
        expire = token_obj[0].expiry
        key = token_obj[1]
        return Response(
            {
                'success': True,
                'data': {
                    'user': UserSerializer(
                        user, context=self.get_serializer_context()
                    ).data,
                    'token': {
                        'key': key,
                        'expires': expire.astimezone(),
                    },
                }
            }
        )


class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        user_tokens = AuthToken.objects.filter(user=user)
        if len(user_tokens) > 0:
            for utoken in user_tokens:
                utoken.delete()
        token_obj = AuthToken.objects.create(user)
        expire = token_obj[0].expiry
        key = token_obj[1]
        return Response(
            {
                'success': True,
                'data': {
                    'user': UserSerializer(
                        user, context=self.get_serializer_context()
                    ).data,
                    'token': {
                        'key': key,
                        'expires': expire.astimezone(),
                    },
                }
            }
        )


class UserAPI(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = InfoSerializer

    def get(self, request, *args, **kwargs):
        user = self.request.user
        profile = user.profile
        return Response(
            {
                'success': True,
                'data': InfoSerializer(user).data
            }
        )


class PostViewAPI(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PostSerializer

    def get_object(self, no):
        try:
            return Post.objects.get(no=no)
        except Post.DoesNotExist:
            raise Http404

    def get(self, request, no, *args, **kwargs):
        post = self.get_object(no)
        serializer = self.get_serializer(post)

        return Response(
            {
                'success': True,
                'data': serializer.data
            }
        )


class PostWriteAPI(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PostWriteSerializer

    def get_profile(self, user):
        try:
            return Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            raise Http404

    def post(self, request, *args, **kwargs):
        print(request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        author = self.get_profile(request.user)
        timestamp = datetime.datetime.now()
        post = Post.create(data['title'], author, timestamp, data['content'])
        post.save()
        return Response(
            {
                'success': True,
                'data': {
                    'no': post.no,
                }
            }
        )


class Pagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page'

    def get_paginated_response(self, data):
        return Response(
            {
                'success': True,
                'data': {
                    'links': {
                        'next': self.get_next_link(),
                        'previous': self.get_previous_link(),
                    },
                    'count': self.page.paginator.count,
                    'results': data
                }
            }
        )


class PostListViewAPI(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Post.objects.all().reverse()
    serializer_class = PostListSerializer
    pagination_class = Pagination

    # def get(self, request, *args, **kwargs):
    #     posts = Post.objects.all()
    #     serializer = self.get_serializer(posts, many=True)
    #     return Response(
    #         {
    #             'success': True,
    #             'data': serializer.data
    #         }
    #     )


class CommentAPI(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CommentWriteSerializer

    def get_profile(self, user):
        try:
            return Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            raise Http404

    def get_post(self, no):
        try:
            return Post.objects.get(no=no)
        except Post.DoesNotExist:
            raise Http404

    def post(self, request, no, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        author = self.get_profile(request.user)
        parent = self.get_post(no)
        comment = Comment.create(parent, author, datetime.datetime.now(), data['content'])
        comment.save()
        parent.comments.add(comment)
        parent.save()
        return Response(
            {
                'success': True,
                'data': {
                    'no': comment.no,
                    'parent': parent.no,
                    'author': author.user.username,
                    'timestamp': comment.timestamp,
                    'content': comment.content,
                },
            }
        )

    def delete(self, request, p_no, c_no, *args, **kwargs):
        user = request.user
        comment = Comment.objects.get(no=c_no)
        if user == comment.author.user:
            comment.delete()
            return Response(
                {
                    'success': True,
                }
            )
        else:
            return Response(
                {
                    'success': False,
                    'msg': 'Credential not matches with author'
                }
            )
