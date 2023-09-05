
from datetime import datetime
from rest_framework import status
from rest_framework.views import APIView
from api.api_v1.v1_appblog.serializers import *
from django.utils.translation import gettext_lazy as _
from utils import GlobalConstant
from utils.functions import custom_response
from rest_framework.permissions import IsAuthenticated
from blogging.models import *
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.settings import api_settings
from utils.custom_methods import CustomPaginationMixin
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status, filters

class LoginView(APIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)

            res = custom_response(True, message=_(GlobalConstant.Data['loggedin_success']), data={"user_id": user.id,"access_token": str(refresh.access_token),"refresh_token": str(refresh),})

            return Response(res, status=status.HTTP_200_OK)

        res = custom_response(False, message=_(list(serializer.errors.values())[0][0]))
        return Response(res, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    refresh_token = request.data.get('refresh_token')
    
    if not refresh_token:
        return Response({'detail': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
    except Exception as e:
        print("Eee",e)
        return Response({'detail': "Successfully logged out."}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({'detail': 'Successfully logged out.'}, status=status.HTTP_200_OK)
    
class SignUpView(APIView):
    serializer_class = UserSignUpSerializer

    def post(self, request):
        serializer = UserSignUpSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.save()
            res = custom_response(True, message=_(GlobalConstant.Data['signup_successfully']),
                                      data=[])
            return Response(res, status=status.HTTP_200_OK)

        res = custom_response(False, message=list(serializer.errors.values())[0][0])
        return Response(res, status=status.HTTP_200_OK)
    
class AddBlogView(APIView):
    serializer_class = BlogSerializer
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        serializer = BlogSerializer(data=self.request.data, context={'request': self.request})
        if serializer.is_valid():
            user_id = serializer.save()
            res = custom_response(True, message=_(GlobalConstant.Data['blog_post_successfully']),
                                        data=[])
            return Response(res, status=status.HTTP_200_OK)

        res = custom_response(False, message=list(serializer.errors.values())[0][0])
        return Response(res, status=status.HTTP_200_OK)
    
class EditBlogView(APIView):
    serializer_class = BlogSerializer
    permission_classes = [IsAuthenticated, ]

    def put(self, request):
        id = request.POST['id']
        blog_post = BlogPost.objects.get(pk=id)
        serializer = BlogSerializer(data=request.data, instance=blog_post, context={'request': self.request})
        if serializer.is_valid():
            validated_data = serializer.validated_data
            if request.user.id == blog_post.author.id or request.user.is_superuser:
                serializer.update(blog_post, validated_data)
                blog_post.save()
                res = custom_response(True, message=_(GlobalConstant.Data['blog_post_successfully_updated']),data=[])
            else:
                res = custom_response(True, message=_(GlobalConstant.Data['no_rights']),
                                            data=[])
            return Response(res, status=status.HTTP_200_OK)

        res = custom_response(False, message=list(serializer.errors.values())[0][0])
        return Response(res, status=status.HTTP_200_OK)
    
class EditCommentView(APIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, ]

    def put(self, request):
        id = request.POST['id']
        if Comment.objects.filter(pk=id):
            blog_post = Comment.objects.get(pk=id)
            serializer = CommentSerializer(data=request.data, instance=blog_post, context={'request': self.request})
            if serializer.is_valid():
                validated_data = serializer.validated_data
                if request.user.id == blog_post.author.id or request.user.is_superuser:
                    serializer.update(blog_post, validated_data)
                    blog_post.save()
                    res = custom_response(True, message=_(GlobalConstant.Data['comment_successfully_updated']),
                                                data=[])
                else:
                    res = custom_response(True, message=_(GlobalConstant.Data['no_rights']),
                                            data=[])

                return Response(res, status=status.HTTP_200_OK)
        else:
            res = custom_response(True, message=_(GlobalConstant.Data['invalid_comment']),
                                                data=[])
            return Response(res, status=status.HTTP_200_OK)

        res = custom_response(False, message=list(serializer.errors.values())[0][0])
        return Response(res, status=status.HTTP_200_OK)


class BlogViewSet(viewsets.ModelViewSet):
    serializer_class = BlogSerializer
    queryset = BlogPost.objects.all()

    def delete(self, request, pk):
        blog_post = get_object_or_404(self.queryset, pk=pk)
        if request.user.id == blog_post.author.id or request.user.is_superuser:
            blog_post.delete()
            res = custom_response(True, message=_(GlobalConstant.Data['blog_post_delete']),
                                                data=[])
        else:
            res = custom_response(True, message=_(GlobalConstant.Data['no_rights']),
                                            data=[])
        return Response(res, status=status.HTTP_200_OK)

class DeleteBlogViewSet(viewsets.ModelViewSet):
    serializer_class = BlogSerializer
    queryset = Comment.objects.all()

    def delete(self, request, pk):
        blog_post = get_object_or_404(self.queryset, pk=pk)
        if request.user.id == blog_post.author.id or request.user.is_superuser:
            blog_post.delete()
            res = custom_response(True, message=_(GlobalConstant.Data['comment_delete']),
                                                data=[])
        else:
            res = custom_response(True, message=_(GlobalConstant.Data['no_rights']),
                                            data=[])
        return Response(res, status=status.HTTP_200_OK)

class ListBlogPost(APIView,CustomPaginationMixin):
    serializer_class = BlogSerializer
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'content']

    # Remove authentication
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        platforms = BlogPost.objects.all().order_by('-id')
        # Apply search filtering
        search_query = self.request.query_params.get('search', None)
        if search_query is not None:
            platforms = self.filter_queryset(platforms, search_query)
        page = self.paginate_queryset(platforms)
        if page is not None:
            serializer_data = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer_data.data)
        serializer = self.serializer_class(page, many=True)
        res = custom_response(True, data=serializer.data)
        return Response(res, status=status.HTTP_200_OK)

    def filter_queryset(self, queryset, search_query):
        filter_backend = filters.SearchFilter()
        request = self.request
        view = self
        return filter_backend.filter_queryset(request, queryset, view)
    
    
class AddCommentView(APIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        serializer = CommentSerializer(data=self.request.data, context={'request': self.request})
        if serializer.is_valid():
            user_id = serializer.save()
            res = custom_response(True, message=_(GlobalConstant.Data['comment_successfully']),
                                        data=[])
            return Response(res, status=status.HTTP_200_OK)

        res = custom_response(False, message=list(serializer.errors.values())[0][0])
        return Response(res, status=status.HTTP_200_OK)

class SingleBlogPost(APIView):
    serializer_class = CommentSerializer

    def get(self, request,pk): 
        ids=pk
        if BlogPost.objects.filter(id=ids):
            dct = {}
            for i in BlogPost.objects.filter(id=ids):
                dct['id'] = i.id
                dct['title'] = i.title
                dct['content'] = i.content
                dct['publication_date'] = str(i.publication_date)
                dct['author'] = i.author.name
            res = custom_response(False,message="Success",data=dct)
            return Response(res, status=status.HTTP_200_OK)
        else:
            res = custom_response(False, message="The requested blog post is not available.")
            return Response(res, status=status.HTTP_200_OK)