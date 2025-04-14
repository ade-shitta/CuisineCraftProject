from rest_framework import serializers
from .models import User
from django.contrib.auth.password_validation import validate_password

class UserSerializer(serializers.ModelSerializer):
    """Serializer for user data returned to frontend"""
    firstName = serializers.CharField(source='first_name')
    lastName = serializers.CharField(source='last_name')
    dateOfBirth = serializers.DateField(source='date_of_birth')
    profileImage = serializers.SerializerMethodField()
    
    def get_profileImage(self, obj):
        if obj.profile_image:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.profile_image.url)
            return obj.profile_image.url
        return None
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'firstName', 'lastName', 'dateOfBirth', 'profileImage']

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    firstName = serializers.CharField(source='first_name')
    lastName = serializers.CharField(source='last_name')
    dateOfBirth = serializers.DateField(source='date_of_birth')
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'firstName', 'lastName', 'email', 'dateOfBirth', 'password']
    
    def validate_password(self, value):
        validate_password(value)
        return value
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            date_of_birth=validated_data.get('date_of_birth')
        )
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    firstName = serializers.CharField(source='first_name', required=False)
    lastName = serializers.CharField(source='last_name', required=False)
    dateOfBirth = serializers.DateField(source='date_of_birth', required=False)
    profileImage = serializers.ImageField(source='profile_image', required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'firstName', 'lastName', 'dateOfBirth', 'profileImage']
        extra_kwargs = {
            'username': {'required': False},
            'email': {'required': False}
        }
        
    def update(self, instance, validated_data):
        """Custom update method to handle profile image"""
        print("Updating user with validated data:", validated_data)
        
        # Update text fields
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.date_of_birth = validated_data.get('date_of_birth', instance.date_of_birth)
        
        # Handle profile image if present
        if 'profile_image' in validated_data:
            instance.profile_image = validated_data['profile_image']
            print("Setting profile image to:", instance.profile_image)
        
        instance.save()
        return instance