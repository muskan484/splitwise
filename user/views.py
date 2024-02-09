from rest_framework import generics
from .models import User
from .serializers import UserSerializer
    
class CreateUser(generics.ListCreateAPIView):
    """
    A view to handle the creation and listing of users using built in ListCreateAPIView.

    Methods: 
    - Get: Retrieves a list of users
    - Post: Creates a new user
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer