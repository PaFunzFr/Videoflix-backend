from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    This serializer validates and creates a new inactive user account. 
    It ensures password confirmation, enforces unique email addresses, 
    and prepares the user instance for activation via email verification.
    """
    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'confirmed_password']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }

    def validate(self, attrs):
        """
        Ensure that the provided passwords match.
        """
        password = attrs.get('password')
        confirmed_password = attrs.get('confirmed_password')
        if password != confirmed_password:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs
    
    def validate_email(self, value):
        """
        Ensure the provided email address is unique.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def create(self, validated_data):
        """
        Create a new user with an inactive status.

        The username is set to the same value as the email for convenience.
        The user will need to confirm their email before becoming active.
        """
        validated_data.pop('confirmed_password')
        user = User.objects.create_user(
            username = validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_active=False
        )
        return user


class RequestPasswordResetSerializer(serializers.Serializer):
    """
    Serializer for requesting a password reset link.

    This serializer accepts an email address and silently validates the input 
    without revealing whether the account exists, maintaining security best practices.
    """
    email = serializers.EmailField()

    # no response, if user exists
    def validate_email(self, value):
        return value


class ConfirmPasswordSerializer(serializers.Serializer):
    """
    Serializer for confirming a new password during password reset.
    Ensures that the two password fields match before proceeding.
    """

    new_password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, attrs):
        if attrs.get('new_password') != attrs.get('confirm_password'):
            raise serializers.ValidationError("Passwords do not match")
        return attrs


class LoginSerializer(TokenObtainPairSerializer):
    """
    Serializer for user login using email and password.

    This serializer authenticates users and issues JWT access and refresh tokens.
    It removes the dependency on a `username` field and supports email-based login.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True) 

    def __init__(self, *args, **kwargs):
        """
        Initialize the serializer and remove the username field 
        from TokenObtainPairSerializer for email-based authentication.
        """
        super().__init__(*args, **kwargs)

        if "username"in self.fields:
            self.fields.pop("username")


    def validate(self, attrs):
        """
        Validate user credentials and account activation status.
        """
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
        
        # Authenticate using JWT
        data = super().validate({"username": user.username, "password": password})
        return data