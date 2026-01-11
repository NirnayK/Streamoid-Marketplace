from rest_framework.serializers import ModelSerializer


class ModelSerializerBase(ModelSerializer):
    class Meta:
        fields = ("id", "created_at", "updated_at")
