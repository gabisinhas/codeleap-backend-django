from django.urls import path
from .utils.csrf import get_csrf_token

from .views.views import (
    PostsRouterView, PatchPostView, DeletePostView,
    GoogleLoginJWT, RegisterView, LoginView, CreatePostView, health_check
)

urlpatterns = [
    path('csrf/', get_csrf_token, name='get_csrf_token'),
    path('health/', health_check, name='health_check'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/google/', GoogleLoginJWT.as_view(), name='google_login'),
    path('listposts/', PostsRouterView.as_view(), name='listposts'),
    path('createpost/', CreatePostView.as_view(), name='createpost'),
    path('editpost/<int:post_id>/', PatchPostView.as_view(), name='editpost'),
    path('deletepost/<int:post_id>/', DeletePostView.as_view(), name='deletepost'),
]
