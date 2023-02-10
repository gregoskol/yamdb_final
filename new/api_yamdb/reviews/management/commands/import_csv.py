import csv
import os

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand
from django.shortcuts import get_object_or_404

from reviews.models import (  # isort:skip
    Category,
    Genre,
    GenreTitle,
    Title,
    User,
    Comment,
    Review,
)


def import_category(model, reader):
    for row in reader:
        model.objects.get_or_create(id=row[0], name=row[1], slug=row[2])
    print(f"Импорт в модель {model.__name__} завершен")


def import_comment(model, reader):
    for row in reader:
        review = get_object_or_404(Review, id=row[1])
        user = get_object_or_404(User, id=row[3])
        model.objects.get_or_create(
            id=row[0], review=review, text=row[2], author=user, pub_date=row[4]
        )
    print(f"Импорт в модель {model.__name__} завершен")


def import_genre(model, reader):
    for row in reader:
        model.objects.get_or_create(id=row[0], name=row[1], slug=row[2])
    print(f"Импорт в модель {model.__name__} завершен")


def import_genre_title(model, reader):
    for row in reader:
        genre = get_object_or_404(Genre, id=row[2])
        title = get_object_or_404(Title, id=row[1])
        model.objects.get_or_create(id=row[0], genre=genre, title=title)
    print(f"Импорт в модель {model.__name__} завершен")


def import_review(model, reader):
    for row in reader:
        title = get_object_or_404(Title, id=row[1])
        user = get_object_or_404(User, id=row[3])
        model.objects.get_or_create(
            id=row[0],
            title=title,
            text=row[2],
            author=user,
            score=row[4],
            pub_date=row[5],
        )
    print(f"Импорт в модель {model.__name__} завершен")


def import_title(model, reader):
    for row in reader:
        category = get_object_or_404(Category, id=row[3])
        model.objects.get_or_create(
            id=row[0], name=row[1], year=row[2], category=category
        )
    print(f"Импорт в модель {model.__name__} завершен")


def import_user(model, reader):
    for row in reader:
        model.objects.get_or_create(
            id=row[0],
            username=row[1],
            email=row[2],
            role=row[3],
            bio=row[4],
            first_name=row[5],
            last_name=row[6],
        )
    print(f"Импорт в модель {model.__name__} завершен")


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "-fn",
            "--file_name",
            type=str,
            help="Введите название базы - файл.csv",
        )
        parser.add_argument(
            "-mn", "--model_name", type=str, help="Введите название модели"
        )

    def handle(self, *args, **options):
        self.file_path = os.path.join(
            settings.BASE_DIR, "static/data", options["file_name"]
        )
        self.name_model = options["model_name"]
        self.model = apps.get_model("reviews", self.name_model)
        csv_file = open(self.file_path, "r", encoding="utf-8")
        reader = csv.reader(csv_file, delimiter=",")
        next(reader, None)
        models_func = {
            Category: import_category,
            Comment: import_comment,
            Genre: import_genre,
            GenreTitle: import_genre_title,
            Review: import_review,
            Title: import_title,
            User: import_user,
        }
        for model, func in models_func.items():
            if self.model is model:
                print(f"Выполняется импорт из {self.file_path}")
                func(self.model, reader)
