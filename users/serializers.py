from django.contrib.auth.models import User
from rest_framework import serializers

class RegisterSerializer(serializers.ModelSerializer):
    # ensures password is only accepted in requests, but not shown in responses
    password = serializers.CharField(write_only = True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    # define how to validate email - allow only unique emails
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    # define how to create user object
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user