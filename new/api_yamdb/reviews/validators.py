import datetime as dt

from rest_framework import serializers


def validate_year(val):
    current_year = dt.date.today().year
    if val > current_year:
        raise serializers.ValidationError(
            "Год создания не может быть из будущего!"
        )
