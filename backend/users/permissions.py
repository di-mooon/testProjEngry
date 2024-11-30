import logging
import os

from rest_framework.permissions import BasePermission

logger = logging.getLogger()


class IsAuthBotPermission(BasePermission):

    def has_permission(self, request, view):
        kwargs = request.META.get('HTTP_AUTHORIZATION', '').split(' ')
        if len(kwargs) != 2:
            logger.error('Не правильно указан заголовок авторизации')
            return False

        token_type, token_key = kwargs
        if not token_key or token_type not in ['Bot']:
            logger.error('Учетные данные не были предоставлены')
            return False

        if token_key != os.getenv('AUTH_BOT_TOKEN'):
            logger.error('Неверный токен')
            return False
        return True
