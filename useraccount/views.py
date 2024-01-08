from .producer import publish_to_notification
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from .serializers import CustomUserSerialzer, GetUserSerializer, GetallUserSerializer
from .models import CustomUser
import jwt,os,binascii, base64
from django.core.files.base import ContentFile
from dotenv import load_dotenv
from django.http import JsonResponse


# Load the stored environment variables
load_dotenv()
secret_key = os.getenv('SECRET_KEY')

# health check for docker
def healthcheck(request):
    return JsonResponse({'status': 'OK'})


class RegisterView(APIView):
    """ 
    Getting the request and registering the user
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
            response_data = {'id': serializer.data['id'],
                             'name': serializer.data['name'],
                             'username': serializer.data['username'],
                             'email': serializer.data['email'],
                             'role': serializer.data['role'],
                             'date_joined': serializer.data['date_joined'],
                             'is_active': serializer.data['is_active']

                             }
            user_details['content'] = f'New account has been created for user, {name}'
            user_details.pop('password')
            user_details['type'] = 'Registration'
            publish_to_notification('new user registered', user_details)
            return Response({'message': "Your Account Registered Successfully", 'data': response_data})

        except ValidationError as e:
            if 'username' in e.detail:
                print(str(e))
                return Response({'error': "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)
            elif 'email' in e.detail:
                print(str(e))
                return Response({'error': 'Email already exists'}, status=status.HTTP_409_CONFLICT)
            else:
                print(str(e))
                return Response({'error': 'Registraion Failed, please check the details again'}, status=status.HTTP_400_BAD_REQUEST)


class UserDetails(APIView):
    """ 
    Get the user details and return to API gateway.
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
                return Response({"error": "An error occurred during token decoding or serialization"})

        return Response({"message": "token not received"})


class UserUpdate(APIView):
    """ 
    Updated the user details based on the request.
    """

    def patch(self, request):
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
                return Response({"error": "An error occurred during token decoding or serialization"})
        return Response({"message": "token not received"})


class GetallUsers(APIView):

    """Collect all users data and return to the API gateway"""

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
                return Response({"error": "An error occurred during token decoding or serialization"})
        return Response({'message': 'Something went wrong, try again'})


class BlockUser(APIView):

    """Block the user based on the request"""

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
                elif action == 'Active':
                    user.is_active = True
                    user.save()
                return Response({'message': 'Succeffully activated the user'})

            except jwt.ExpiredSignatureError:
                raise AuthenticationFailed("Not authorized")
            except jwt.InvalidTokenError:
                raise AuthenticationFailed("Invalid token")
            except Exception as e:
                return Response({"error": "An error occurred during token decoding or serialization"})
        return Response({'message': 'Something went wrong, try again'})