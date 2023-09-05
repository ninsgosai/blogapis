from django.urls import path
from api.api_v1.v1_appblog.views import *

urlpatterns = [
    
    path('login/', LoginView.as_view(), name='api_v1_login'),
    path('register/', SignUpView.as_view(), name="api_v1_signup"),
    path('add-blog/', AddBlogView.as_view(), name="api_v1_addblog"),
    path('add-comment/', AddCommentView.as_view(), name="api_v1_addcomment"),
    path('edit-blog/', EditBlogView.as_view(), name="api_v1_editblog"),
    path('edit-comment/', EditCommentView.as_view(), name="api_v1_editcomment"),
    path('delete-blog/<str:pk>/', BlogViewSet.as_view({'get': 'list'}), name="api_v1_deleteblog"),
    path('delete-comment/<str:pk>/', DeleteBlogViewSet.as_view({'get': 'list'}), name="api_v1_deletecomment"),
    path('blogs/', ListBlogPost.as_view(), name="api_v1_blogs"),
    path('blog/<str:pk>/', SingleBlogPost.as_view(), name="api_v1_singleblogs"),
    path('logout/', logout, name='api_v1_logout'),

]
