from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from .serializers import CustomUserSerialzer
from .models import CustomUser
import jwt, datetime
import os

class RegisterView(APIView):
    def post(self, request):
        user_details = request.data
        name = user_details.get('name')
        username = user_details.get('username')
        email = user_details.get('email')
        workspace = user_details.get('workspace')
        password = user_details.get('password')
        password2 = user_details.get('password2')
        
        if not all([email, name, username, workspace, password, password2]):
            return Response({'error': 'Please fill in all the required fields'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        if password != password2:  
            return Response({'error': 'Password Mismatch'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        user_details.pop('password2')
        serializer = CustomUserSerialzer(data=user_details)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'message':"User Registered Successfully"})
        except ValidationError as e:
            return Response({'error':str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class LoginView(APIView):
    def get(self, request):
        # Handle GET request logic here
        return Response({"message": "Success, show the loginpage"})
    def post(self, request):
        try:
            # Get email and password from request data
            email = request.data.get('email')
            password = request.data.get('password')
            
            # Check if both email and password are provided
            if not (email or password):
                return Response({"error": "Please fill all required fileds"})
            # Retrieve user based on email
            user = CustomUser.objects.filter(email=email).first()
            # if user exists, return error
            if user is None:
                raise AuthenticationFailed({
                    "error":"user doesn't exists"
                })
            # if entered password is wrong, return error
            if not user.check_password(password):
                raise AuthenticationFailed({"error":"incorrect password"})
            payload = {
                'id':'user.id',
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
                'iat': datetime.datetime.utcnow()
            }
            # Key taken from .env file
            secret_key = os.getenv('JWT_SECURITY_KEY', 'secret')
            #token generated for authentication
            token = jwt.encode(payload, secret_key,algorithm='HS256')
            response = Response()
            response.data = {
                'jwt': token
            }
            return response
        # if any unexpected error or  user data not received
        except Exception as e:
            return Response({"error": str(e)})
        
            
        
        
        
        
        
        
        
        
            