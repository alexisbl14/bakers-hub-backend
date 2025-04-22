from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from .serializers import RegisterSerializer
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token

# Create your views here.
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    # update permissions to allow registration without authentication
    permission_classes = [AllowAny]

class LoginView(APIView):
    # update permissions to allow login without authentication
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        # return user info if user is authenticated, else return an error
        if user is not None:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "message": "Login successful",
                "username": user.username,
                "token": token.key
            })
        return Response({"error": "Invalid Credentials"}, status=status.HTTP_401_UNAUTHORIZED)

