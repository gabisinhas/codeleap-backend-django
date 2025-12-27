
from django.urls import path
from .csrf import get_csrf_token
from .views import GetPostsView, CreatePostView, PatchPostView, DeletePostView, GoogleLoginJWT

urlpatterns = [
    path('csrf/', get_csrf_token, name='get_csrf_token'),
    path('posts/', GetPostsView.as_view(), name='listposts'),
    path('posts/', CreatePostView.as_view(), name='createpost'),
    path('posts/<int:post_id>/', PatchPostView.as_view(), name='editpost'),
    path('posts/<int:post_id>/', DeletePostView.as_view(), name='deletepost'),
    path('auth/google/', GoogleLoginJWT.as_view(), name='google_login'),
]
