from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.middleware.csrf import get_token
from .serializers import UserSerializer, UserRegistrationSerializer, UserUpdateSerializer
from django.contrib.auth import login, logout, authenticate
from django.http import JsonResponse

class CSRFTokenView(APIView):
    """Endpoint to get CSRF token"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        token = get_token(request)
        return Response({'csrfToken': token})

class UserRegistrationView(APIView):
    """Endpoint for user registration"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user)
            return Response(
                UserSerializer(user, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    """Endpoint for user login"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response(
                {'detail': 'Username and password are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Use Django's standard authentication
        user = authenticate(request, username=username, password=password)
        
        if user:
            login(request, user)
            return Response(UserSerializer(user, context={'request': request}).data)
        
        return Response(
            {'detail': 'Invalid credentials'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )

class UserLogoutView(APIView):
    """Endpoint for user logout"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        logout(request)
        return Response({'detail': 'Successfully logged out'})

class UserProfileView(APIView):
    """Endpoint to get and update user profile data"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)
    
    def post(self, request):
        """Handle profile updates via POST (better for file uploads)"""
        # Add debug logging
        print("Received POST update request with data:", request.data)
        print("Request FILES:", request.FILES)
        
        serializer = UserUpdateSerializer(
            request.user, 
            data=request.data, 
            partial=True,
            context={'request': request}
        )
        
        if serializer.is_valid():
            print("Serializer is valid with data:", serializer.validated_data)
            user = serializer.save()
            print("User saved with profile image:", user.profile_image)
            return Response(UserSerializer(user, context={'request': request}).data)
        
        print("Serializer errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def put(self, request):
        # Add debug logging
        print("Received PUT update request with data:", request.data)
        print("Request FILES:", request.FILES)
        
        serializer = UserUpdateSerializer(
            request.user, 
            data=request.data, 
            partial=True,
            context={'request': request}  # Pass request context for file handling
        )
        
        if serializer.is_valid():
            print("Serializer is valid with data:", serializer.validated_data)
            user = serializer.save()
            print("User saved with profile image:", user.profile_image)
            return Response(UserSerializer(user, context={'request': request}).data)
        
        print("Serializer errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AuthCheckView(APIView):
    """Simple endpoint to check if user is authenticated"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        is_authenticated = request.user.is_authenticated
        return Response({
            'isAuthenticated': is_authenticated,
            'username': request.user.username if is_authenticated else None
        })