import logging

from core.mixins import GetSerializerClassMixin
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from users import permissions
from users.models import User, TgUserToken
from users.serializers import (UserSerializer, BotUserLoginSerializer,
                               BotUserCreateSerializer, BotTokenCheckSerializer, UserCreateUpdateSerializer)

logger = logging.getLogger()


@extend_schema(tags=['Users'])
class UserViewSet(GetSerializerClassMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    serializer_class_by_action = {
        'me': UserSerializer,
        'update_me': UserCreateUpdateSerializer
    }

    @action(methods=['GET'],
            detail=False,
            permission_classes=(IsAuthenticated,),
            serializer_class=UserSerializer)
    def me(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.request.user)
        return Response(serializer.data)

    @me.mapping.patch
    def update_me(self, request, *args, **kwargs):
        serializer = UserCreateUpdateSerializer(instance=self.request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(exclude=True)
    @action(detail=False,
            methods=['POST'],
            serializer_class=BotUserLoginSerializer,
            permission_classes=[permissions.IsAuthBotPermission])
    def check_bot_user(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tg_id = serializer.validated_data['tg_id']
        exists_user = User.objects.filter(tg_id=tg_id).exists()
        return Response({'exists_user': exists_user})

    @extend_schema(exclude=True)
    @action(detail=False,
            methods=['POST'],
            serializer_class=BotUserCreateSerializer,
            permission_classes=[permissions.IsAuthBotPermission])
    def create_bot_user(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']
        if not TgUserToken.objects.filter(token=token).exists():
            return Response({'success': False, 'data': 'Что-то пошло не так, перейдите по ссылке еще раз'})
        user_token = TgUserToken.objects.get(token=token)
        phone = serializer.validated_data['phone']
        tg_id = serializer.validated_data.get('tg_id')
        whatsapp_id = serializer.validated_data.get('whatsapp_id')
        tg_username = serializer.validated_data['tg_username'] or ''
        last_name = serializer.validated_data['last_name'] or ''
        referral_user_id = serializer.validated_data.get('referral_user_id')
        first_name = serializer.validated_data['first_name'] or last_name or tg_username or ''
        full_name = last_name + ' ' + first_name
        if User.objects.filter(phone=phone).exists():
            user = User.objects.get(phone=phone)
            user.tg_id = tg_id
            user.tg_username = tg_username
            user.whatsapp_id = whatsapp_id
            user_token.user = user
            user.save()
            user_token.save()
            return Response({'success': True, 'data': 'Вы успешно авторизовались в системе.'})

        user = User.objects.create_user(
            phone=phone,
            password=str(token),
            full_name=full_name,
            tg_id=tg_id,
            whatsapp_id=whatsapp_id,
            tg_username=tg_username,
            referral_user_id=referral_user_id
        )
        user_token.user = user
        user_token.save()
        return Response({'success': True, 'data': 'Вы успешно авторизовались в системе.'})


@extend_schema(tags=['Tokens'])
class TokenViewSet(GenericViewSet):
    @action(detail=False, methods=['post'], serializer_class=BotTokenCheckSerializer)
    def check_auth_bot(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']
        if not TgUserToken.objects.filter(token=token).exists():
            raise ValidationError({'token': 'Неверный токен'})
        user_token = TgUserToken.objects.get(token=token)
        if user_token.user is None:
            return Response({'activated': False, 'access_token': ''})

        refresh = RefreshToken.for_user(user_token.user)
        return Response({'access_token': str(refresh.access_token), 'activated': True})

    @action(detail=False, methods=['post'], serializer_class=None)
    def create_bot_token(self, request, *args, **kwargs):
        user_token = TgUserToken.objects.create()
        return Response({'token': user_token.token})
