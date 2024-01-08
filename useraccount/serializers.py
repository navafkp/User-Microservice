from rest_framework import serializers
from .models import CustomUser
import base64


class CustomUserSerialzer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        """poping password and saved the user, then hased the password for protection """
        password = validated_data.pop('password', None)
        if not password:
            raise serializers.ValidationError(
                {'password': 'This field is required.'})
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user

# serializer for request for specific user profile


class GetUserSerializer(serializers.ModelSerializer):
    profile_image_base64 = serializers.SerializerMethodField()

    def get_profile_image_base64(self, user):
        if user.profile_image:
            # Open the image file and encode it in base64
            with open(user.profile_image.path, "rb") as image_file:
                encode_image = base64.b64encode(image_file.read())
                return encode_image.decode("utf-8")

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'name', 'role', 'designation', 'email',
                  'date_joined', 'profile_image_base64', 'workspace'
                  ]


class GetallUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'name', 'role', 'designation',
                  'email', 'date_joined', 'workspace', 'is_active'
                  ]
