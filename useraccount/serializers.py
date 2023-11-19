from rest_framework import serializers
from .models import CustomUser

class CustomUserSerialzer(serializers.ModelSerializer):
    class Meta:
        model  = CustomUser
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only':True}
        }
          
    def create(self, validated_data):
        """poping password and saved the user, then hased the password for protection """
        password = validated_data.pop('password', None)
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user