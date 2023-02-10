from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .validators import validate_year


class User(AbstractUser):
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"

    ROLES = [
        (ADMIN, "Администратор"),
        (MODERATOR, "Модератор"),
        (USER, "Пользователь"),
    ]

    role = models.CharField(
        max_length=16, choices=ROLES, default=USER, verbose_name="Роль"
    )
    email = models.EmailField(
        max_length=254, unique=True, verbose_name="Электронная почта"
    )
    first_name = models.CharField(
        max_length=150, blank=True, verbose_name="Имя"
    )
    bio = models.TextField(blank=True, verbose_name="Описание")
    confirmation_code = models.CharField(
        max_length=50, blank=True, verbose_name="Код для авторизации"
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        constraints = [
            models.UniqueConstraint(
                fields=["username", "email"], name="unique_username_email"
            )
        ]

    @property
    def is_user(self):
        if self.role == self.USER:
            return True
        else:
            return False

    @property
    def is_moderator(self):
        if self.role == self.MODERATOR:
            return True
        else:
            return False

    @property
    def is_admin(self):
        if self.role == self.ADMIN:
            return True
        else:
            return False


class Genre(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=100)
    year = models.SmallIntegerField(
        verbose_name="Год", validators=[validate_year], db_index=True
    )
    description = models.TextField(blank=True)
    genre = models.ManyToManyField(Genre, through="GenreTitle")
    category = models.ForeignKey(
        Category,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="titles",
    )

    class Meta:
        verbose_name = "Произведение"
        verbose_name_plural = "Произведения"

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    genre = models.ForeignKey(
        Genre, on_delete=models.SET_NULL, blank=True, null=True
    )
    title = models.ForeignKey(
        Title, on_delete=models.SET_NULL, blank=True, null=True
    )

    def __str__(self):
        return f"{self.title} {self.genre}"


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    score = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1, "минимальная оценка - 1"),
            MaxValueValidator(10, "Максимальная оценка - 10"),
        ],
        verbose_name="Оценка",
    )
    pub_date = models.DateTimeField(
        "Дата публикации",
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        ordering = ["-pub_date"]
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        constraints = [
            models.UniqueConstraint(
                fields=["author", "title"], name="unique_author_review"
            )
        ]

    def __str__(self):
        return f"{self.title}, {self.score}, {self.author}"


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    pub_date = models.DateTimeField(
        "Дата публикации",
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        ordering = ["-pub_date"]
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self):
        return f"{self.author}, {self.pub_date}: {self.text}"
