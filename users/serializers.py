from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, 
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'password', 'password_confirm', 'role', 'department',
            'position', 'phone_number', 'date_joined_company'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError(
                "Password fields didn't match."
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(
                request=self.context.get('request'),
                username=username,
                password=password
            )

            if not user:
                msg = 'Unable to log in with provided credentials.'
                raise serializers.ValidationError(msg, code='authorization')
            
            if not user.is_active:
                msg = 'User account is disabled.'
                raise serializers.ValidationError(msg, code='authorization')
            
            attrs['user'] = user
            return attrs
        else:
            msg = 'Must include "username" and "password".'
            raise serializers.ValidationError(msg, code='authorization')


class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'role', 'employee_id', 'department',
            'position', 'phone_number', 'date_joined_company',
            'is_active_employee', 'date_joined', 'last_login'
        ]
        read_only_fields = [
            'id', 'username', 'employee_id', 'date_joined', 'last_login'
        ]


class UserListSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'full_name', 'role',
            'employee_id', 'department', 'position', 'is_active_employee'
        ]


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, 
        validators=[validate_password]
    )

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'password', 'role', 'department', 'position',
            'phone_number', 'date_joined_company'
        ]

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'department',
            'position', 'phone_number', 'is_active_employee'
        ]
