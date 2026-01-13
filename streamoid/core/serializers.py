from rest_framework.serializers import (
    CharField,
    IntegerField,
    JSONField,
    ModelSerializer,
    Serializer,
    ValidationError,
)


class DetailsBaseSerializer(ModelSerializer):
    class Meta:
        fields = ("id", "created_at", "updated_at")


class CreateBaseSerializer(ModelSerializer):
    def validate_name(self, name):
        model = getattr(self.Meta, "model", None)
        if model and model.objects.filter(name__iexact=name).exists():
            raise ValidationError("Name already exists.")
        return name


class BaseDetailResponseSerializer(Serializer):
    code = IntegerField()
    data = JSONField()
    errors = JSONField()
    message = CharField()


class BaseListResponseSerializer(Serializer):
    code = IntegerField()
    data = JSONField()
    errors = JSONField()
    message = CharField()
    total_page_number = IntegerField()
    total_count = IntegerField()


class ErrorResponseSerializer(BaseDetailResponseSerializer):
    pass
