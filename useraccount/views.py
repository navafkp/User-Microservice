from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from .serializers import CustomUserSerialzer, GetUserSerializer, GetallUserSerializer
from .models import CustomUser
import jwt
import base64
from django.core.files.base import ContentFile
import binascii
import os
from dotenv import load_dotenv

# Load the stored environment variables
load_dotenv()
secret_key = os.getenv('SECRET_KEY')

from .producer import publish_to_notification
import json
class RegisterView(APIView):
    """ 
    Getting user registration request from API gateway and registering the user
    """

    def post(self, request):
        user_details = request.data
        name = user_details.get('name')
        username = user_details.get('username')
        email = user_details.get('email')
        designation = request.data.get('designation')
        workspace = user_details.get('workspace')
        role = user_details.get('role')
        password = user_details.get('password')
        password2 = user_details.get('password2')
        if not all([email, name, username, workspace, password, password2]):
            return Response({'error': 'Please fill in all the required fields'},
                            status=status.HTTP_400_BAD_REQUEST)
        if password != password2:
            return Response({'error': 'Password Mismatch'},
                            status=status.HTTP_400_BAD_REQUEST)
        user_details.pop('password2')
        try:
            serializer = CustomUserSerialzer(data=user_details)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            user_details['content'] =f'New account has been created for user, {name}'
            print(user_details, 'test')
            publish_to_notification('new user registered', user_details)
            return Response({'message': "Your Account Registered Successfully"})
        except ValidationError as e:
            if 'username' in e.detail:
                return Response({'error': "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)
            elif 'email' in e.detail:
                return Response({'error': 'Email already exists'}, status=status.HTTP_409_CONFLICT)
            else:
                return Response({'error':'Registraion Failed, please check the details again'},status=status.HTTP_400_BAD_REQUEST)
   
           
class UserDetails(APIView):
    """ 
    Get request from API gateway for getting a specific user , 
    after validating the access token, get the user details and return it.
    """

    def get(self, request):
        token = request.data.get('token')
        if token:
            try:
                payload = jwt.decode(token, secret_key, algorithms=["HS256"])
                user = CustomUser.objects.filter(id=payload['user_id']).first()

                if user is not None:
                    serializer = GetUserSerializer(user)
                    return Response(serializer.data)
                else:
                    raise AuthenticationFailed("User not found")

            except jwt.ExpiredSignatureError:
                raise AuthenticationFailed("Not authorized")
            except jwt.InvalidTokenError:
                raise AuthenticationFailed("Invalid token")
            except Exception as e:
                print(e)
                return Response({"error": "token not"})
        return Response({"message": "token not received"})


class UserUpdate(APIView):
    """ 
    Updating user details after validating the access token, 
    and return the resposne to API gateway
    """

    def patch(self, request):
        print(request.data)
        token = request.data.get('token')
        user_details = request.data.get('userdetails', {})

        name = user_details.get('name', '')
        username = user_details.get('username', '')
        email = user_details.get('email')
        designation = user_details.get('designation', '')
        image_data = user_details.get('image', '')

        if not all([name, username, email, designation]):
            return Response({'message': 'Fileds are required'},
                            status=status.HTTP_400_BAD_REQUEST)

        if token:
            try:
                payload = jwt.decode(token, secret_key, algorithms=["HS256"])
                try:
                    user = CustomUser.objects.filter(
                        id=payload['user_id']).first()
                    if user:
                        
                        user.name = name

                        user.username = username

                        user.email = email

                        user.designation = designation

                        if image_data:
                            try:
                                format, imgstr = image_data.split(';base64,')
                                ext = format.split('/')[-1]
                                image_data = ContentFile(base64.b64decode(
                                    imgstr), name=f"{user.email}.{ext}")
                                user.profile_image.save(
                                    f"{user.email}_profile_image.{ext}", image_data, save=True)
                            except binascii.Error as e:  # handling decoding error
                                print(f"Error decoding base64: {e}")
                            except Exception as e:  # Handle other exceptions
                                print(f"Error: {e}")
                        user.save()
                        return Response({'message': 'Updated succesfully'})

                except:
                    raise AuthenticationFailed("User not found")
            except jwt.ExpiredSignatureError:
                raise AuthenticationFailed("Not authorized")
            except jwt.InvalidTokenError:
                raise AuthenticationFailed("Invalid token")
            except Exception as e:
                print(e)
                return Response({"error": "token not"})
        return Response({"message": "token not received"})


class GetallUsers(APIView):
    def get(self, request):
        workspace = request.data.get('workspace')
        token = request.data.get('token')
        if token:
            try:
                payload = jwt.decode(token, secret_key, algorithms=['HS256'])
                users = CustomUser.objects.filter(
                    workspace=workspace).exclude(id=payload['user_id'])
                if users.exists():
                    serialize = GetallUserSerializer(users, many=True)
                    return Response(serialize.data)
                else:
                    return Response({'message': 'no users found'})
            except jwt.ExpiredSignatureError:
                raise AuthenticationFailed("Not authorized")
            except jwt.InvalidTokenError:
                raise AuthenticationFailed("Invalid token")
            except Exception as e:
                print(e)
                return Response({"error": "An error occurred during token decoding or serialization"})
        return Response({'message': 'Something went wrong, try again'})


class BlockUser(APIView):
    def patch(self, request, id=None):
        id = id
        action = request.data.get('value')
        token = request.data.get('access')
        if token:
            try:
                payload = jwt.decode(token, secret_key, algorithms=['HS256'])
                user = CustomUser.objects.filter(id=id).first()
                if action == 'block':
                    user.is_active = False
                    user.save()
                    return Response({'message': 'Succeffully blocked the user'})
                elif action == 'activate':
                    user.is_active = True
                    user.save()
                return Response({'message': 'Succeffully activated the user'})
            except jwt.ExpiredSignatureError:
                raise AuthenticationFailed("Not authorized")
            except jwt.InvalidTokenError:
                raise AuthenticationFailed("Invalid token")
            except Exception as e:
                print(e)
                return Response({"error": "An error occurred during token decoding or serialization"})
        return Response({'message': 'Something went wrong, try again'})
    

class UserAuthentication(APIView):
    def post(self, request):
        print("sads")
        print(request)
        print(request.data.get('access'))
        token = request.data.get('access')
        try:
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            user_id = payload['user_id']
            print(payload)
            print(user_id)
            availble = CustomUser.objects.filter(id=user_id).exists()
            print(availble)
            return Response(availble)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Not authorized")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid token")
        except Exception as e:
            print(e)
            return Response({"error": "An error occurred during token decoding or serialization"})
        return Response({'message': 'Something went wrong, try again'})
