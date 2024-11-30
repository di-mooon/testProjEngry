from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'phone', 'full_name',
                  'role', 'tg_id',)
        read_only_fields = ('phone', 'tg_id', 'role')


class UserCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('full_name',)


class BotUserLoginSerializer(serializers.Serializer):
    tg_id = serializers.IntegerField(required=False, allow_null=True)
    whatsapp_id = serializers.IntegerField(required=False, allow_null=True)

    def validate(self, attrs):
        if not attrs.get('tg_id') and not attrs.get('whatsapp_id'):
            raise serializers.ValidationError('Не указано значение')
        return attrs


class BotTokenCheckSerializer(serializers.Serializer):
    token = serializers.UUIDField()


class BotUserCreateSerializer(serializers.Serializer):
    phone = serializers.IntegerField()
    last_name = serializers.CharField(required=False, allow_null=True)
    first_name = serializers.CharField(required=False, allow_null=True)
    tg_username = serializers.CharField(required=False, allow_null=True)
    tg_id = serializers.IntegerField(required=False, allow_null=True)
    whatsapp_id = serializers.IntegerField(required=False, allow_null=True)
    token = serializers.UUIDField()
    referral_user_id = serializers.IntegerField(required=False, allow_null=True)

    def validate(self, attrs):
        if not attrs.get('tg_id') and not attrs.get('whatsapp_id'):
            raise serializers.ValidationError('Не указано значение bot_id')
        return attrs
