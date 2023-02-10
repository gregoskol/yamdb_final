from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (filters, mixins, permissions, serializers, status,
                            viewsets)
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import Category, Comment, Genre, Review, Title, User

from api_yamdb.settings import EMAIL_ADMIN

from .filters import TitleFilter  # isort:skip
from .permissions import (  # isort:skip
    IsAdminOrReadOnly,
    IsAuthorModeratorAdminPermission,
    IsStaffAdminPermission,
)
from .serializers import (  # isort:skip
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    TitleReadSerializer,
    TitleWriteSerializer,
    AuthTokenSerializer,
    UserCreationSerializer,
)


class CDLViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    ViewSet для create(), destroy(), list()
    """

    pass


class CategoryViewSet(CDLViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"


class GenreViewSet(CDLViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(rating=Avg("reviews__score"))
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return TitleReadSerializer
        return TitleWriteSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserCreationSerializer
    permission_classes = (IsStaffAdminPermission,)
    search_fields = ("=username",)
    lookup_field = "username"

    @action(
        detail=False,
        methods=["GET", "PATCH"],
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        user = request.user
        if request.method == "GET":
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        serializer.save(role=user.role, partial=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([AllowAny])
def signup_new_user(request):
    serializer = UserCreationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.data["email"]
    username = serializer.data["username"]

    user, _ = User.objects.get_or_create(email=email, username=username)
    confirmation_code = default_token_generator.make_token(user)

    send_mail(
        "Код подтверждения",
        f"Ваш код подтверждения: {confirmation_code}",
        EMAIL_ADMIN,
        [email],
        fail_silently=False,
    )

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([AllowAny])
def get_token(request):
    serializer = AuthTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data["username"]
    confirmation_code = serializer.validated_data["confirmation_code"]
    try:
        user = get_object_or_404(User, username=username)
    except User.DoesNotExist:
        return Response(
            "Пользователь не найден", status=status.HTTP_404_NOT_FOUND
        )
    if default_token_generator.check_token(user, confirmation_code):
        token = AccessToken.for_user(user)
        return Response({"token": str(token)}, status=status.HTTP_200_OK)
    return Response(
        {"confirmation_code": "Неверный код подтверждения"},
        status=status.HTTP_400_BAD_REQUEST,
    )


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [
        IsAuthorModeratorAdminPermission,
        permissions.IsAuthenticatedOrReadOnly,
    ]

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs["title_id"])
        return Review.objects.filter(title=title)

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs["title_id"])
        if title and serializer.is_valid:
            review = Review.objects.filter(
                title=title, author=self.request.user
            )
            if len(review) == 0:
                serializer.save(author=self.request.user, title=title)
            else:
                raise serializers.ValidationError("Ревью уже существует")


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [
        IsAuthorModeratorAdminPermission,
        permissions.IsAuthenticatedOrReadOnly,
    ]

    def get_queryset(self):
        review = get_object_or_404(Review, id=self.kwargs["review_id"])
        return Comment.objects.filter(review=review)

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs["review_id"])
        if serializer.is_valid:
            serializer.save(author=self.request.user, review=review)

    def perform_destroy(self, instance):
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_update(self, serializer):
        if self.request.user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        return serializer.save()
