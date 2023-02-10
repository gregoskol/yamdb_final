from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from reviews.models import Category, Comment, Genre, Review, Title, User

from .utils import CurrentTitleDefault


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ("id",)
        model = Category
        lookup_field = "slug"


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ("id",)
        model = Genre
        lookup_field = "slug"


class TitleReadSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        fields = "__all__"
        model = Title


class TitleWriteSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field="slug", many=True, queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field="slug", queryset=Category.objects.all()
    )

    class Meta:
        fields = "__all__"
        model = Title


class UserCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        email = serializers.EmailField(required=True)
        username = serializers.CharField(required=True)

        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role",
        )

    def validate_username(self, value):
        """Проверяем, что нельзя создать пользователя с username = "me"
        и, что нельзя создать с одинаковым username."""
        username = value.lower()
        if username == "me":
            raise serializers.ValidationError(
                'Пользователя с username="me" создавать нельзя.'
            )
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                f"Пользователь с таким username — {username} — уже существует."
            )
        return value

    def validate_email(self, value):
        """Проверяем, что нельзя создать пользователя с одинаковым email."""
        email = value.lower()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                f"Пользователь с таким Email — {email} — уже существует."
            )
        return value


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "username")


class AuthTokenSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField(max_length=50)


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        read_only=True,
        slug_field="username",
    )
    title = serializers.HiddenField(default=CurrentTitleDefault())

    class Meta:
        model = Review
        fields = ["id", "title", "author", "text", "score", "pub_date"]
        validators = [
            UniqueTogetherValidator(
                queryset=Review.objects.all(), fields=("author", "title")
            )
        ]


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field="username"
    )

    class Meta:
        model = Comment
        fields = [
            "id",
            "text",
            "author",
            "pub_date",
        ]
