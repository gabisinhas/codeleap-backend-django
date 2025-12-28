from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from ..models.post import Post
# As views podem ser movidas para core/views/ para melhor organização MVC.
from ..serializers import PostSerializer

from google.oauth2 import id_token
from google.auth.transport import requests
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken
import os
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

@method_decorator(csrf_exempt, name='dispatch')
class GoogleLoginJWT(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        logger.info("=== Iniciando autenticação Google ===")
        logger.info(f"Request data: {request.data}")
        logger.info(f"Headers: {request.headers}")
        
        try:
            token = request.data.get('token')
            
            if not token:
                logger.error("Token não fornecido no request")
                return Response({
                    'error': 'Token não fornecido'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            logger.info(f"Token recebido (primeiros 50 chars): {token[:50]}...")
            

            client_id = os.getenv('GOOGLE_CLIENT_ID')
            logger.info(f"Google Client ID: {client_id}")
            
            if not client_id:
                logger.error("GOOGLE_CLIENT_ID não configurado")
                return Response({
                    'error': 'Configuração do Google OAuth não encontrada'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            try:
                logger.info("Verificando token com Google...")

                idinfo = id_token.verify_oauth2_token(
                    token, 
                    requests.Request(), 
                    client_id,
                    clock_skew_in_seconds=300
                )
                
                logger.info(f"Token verificado com sucesso! Email: {idinfo.get('email')}")
                logger.info(f"Issuer: {idinfo.get('iss')}")
                

                if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                    logger.error(f"Issuer inválido: {idinfo['iss']}")
                    return Response({
                        'error': 'Token inválido'
                    }, status=status.HTTP_401_UNAUTHORIZED)
                

                email = idinfo['email']
                first_name = idinfo.get('given_name', '')
                last_name = idinfo.get('family_name', '')
                
                logger.info(f"Buscando/criando usuário para email: {email}")
                

                user, created = User.objects.get_or_create(
                    email=email,
                    defaults={
                        'username': email.split('@')[0],
                        'first_name': first_name,
                        'last_name': last_name,
                    }
                )
                
                logger.info(f"Usuário {'criado' if created else 'encontrado'}: {user.username}")
                

                refresh = RefreshToken.for_user(user)
                
                logger.info("Tokens JWT gerados com sucesso!")
                
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                    }
                }, status=status.HTTP_200_OK)
                
            except ValueError as e:
                logger.error(f"Erro ao verificar token: {str(e)}")
                return Response({
                    'error': 'Token inválido ou expirado',
                    'detail': str(e)
                }, status=status.HTTP_401_UNAUTHORIZED)
                
        except Exception as e:
            logger.error(f"Erro interno: {str(e)}", exc_info=True)
            return Response({
                'error': 'Erro interno durante a autenticação',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not username or not email or not password:
            return Response({
                'error': 'Username, email e password são obrigatórios'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(username=username).exists():
            return Response({
                'error': 'Username já existe'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(email=email).exists():
            return Response({
                'error': 'Email já está cadastrado'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            

            refresh = RefreshToken.for_user(user)
            
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': 'Erro ao criar usuário',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({
                'error': 'Username e password são obrigatórios'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=username, password=password)
        
        if user is None:
            return Response({
                'error': 'Credenciais inválidas'
            }, status=status.HTTP_401_UNAUTHORIZED)
        

        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            }
        }, status=status.HTTP_200_OK)


class DeletePostView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def delete(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        if post.username != request.user.username:
            return Response({'detail': 'Você não tem permissão para deletar este post.'}, status=status.HTTP_403_FORBIDDEN)
        post.delete()
        return Response({'detail': 'Post deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)

class PatchPostView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def patch(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        if post.username != request.user.username:
            return Response({'detail': 'Você não tem permissão para editar este post.'}, status=status.HTTP_403_FORBIDDEN)
        data = {}
        if 'title' in request.data:
            data['title'] = request.data['title']
        if 'content' in request.data:
            data['content'] = request.data['content']
        serializer = PostSerializer(post, data=data, partial=True)
        if serializer.is_valid():
            post = serializer.save()
            response_data = {
                'id': post.id,
                'username': post.username,
                'created_datetime': post.created_at,
                'title': post.title,
                'content': post.content
            }
            return Response(response_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetailRouterView(APIView):
	"""Routes PATCH and DELETE requests to separate views"""
	permission_classes = [permissions.IsAuthenticated]
	
	def patch(self, request, post_id):
		"""Update a post"""
		patch_view = PatchPostView()
		return patch_view.patch(request, post_id)
	
	def delete(self, request, post_id):
		"""Delete a post"""
		delete_view = DeletePostView()
		return delete_view.delete(request, post_id)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.models.post import Post
from ..serializers import PostSerializer


class GetPostsView(APIView):
	permission_classes = [IsAuthenticated]
	def get(self, request):
		posts = Post.objects.all().order_by('-created_at')
		data = [
			{
				'id': post.id,
				'username': post.username,
				'created_datetime': post.created_at,
				'title': post.title,
				'content': post.content
			}
			for post in posts
		]
		return Response(data)


class CreatePostView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        data = request.data.copy()
        data['username'] = request.user.username
        serializer = PostSerializer(data=data)
        if serializer.is_valid():
            post = serializer.save()
            response_data = {
                'id': post.id,
                'username': post.username,
                'created_datetime': post.created_at,
                'title': post.title,
                'content': post.content
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostsRouterView(APIView):
	"""Routes GET and POST requests to separate views"""
	permission_classes = [IsAuthenticated]
	
	def get(self, request):
		"""List all posts"""
		get_view = GetPostsView()
		return get_view.get(request)
	
	def post(self, request):
		"""Create a new post"""
		create_view = CreatePostView()
		return create_view.post(request)
