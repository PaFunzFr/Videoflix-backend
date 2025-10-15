from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'confirmed_password']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }

    def validate(self, attrs):
        password = attrs.get('password')
        confirmed_password = attrs.get('confirmed_password')
        if password != confirmed_password:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def create(self, validated_data):
        validated_data.pop('confirmed_password')
        user = User.objects.create_user(
            username = validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_active=False
        )
        return user


class RequestPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    # no response, if user exists
    def validate_email(self, value):
        return value


class ConfirmPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, attrs):
        if attrs.get('new_password') != attrs.get('confirm_password'):
            raise serializers.ValidationError("Passwords do not match")
        return attrs


class LoginSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True) 

    """ make username unrequired """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "username"in self.fields:
            self.fields.pop("username")


    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        error_respone = "If registered, please confirm your email address before logging in. "\
                        "If you haven't signed up yet, please register first."

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(error_respone)

        if not user.is_active:
            raise serializers.ValidationError(error_respone)
        
        if not user.check_password(password):
            raise serializers.ValidationError(error_respone)
        
        data = super().validate({"username": user.username, "password": password})
        return data