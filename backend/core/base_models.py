from django.db import models


class AbstractBaseModel(models.Model):
    created_at = models.DateTimeField("Дата создания", auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField("Дата последнего обновления", auto_now=True, db_index=True)

    class Meta:
        abstract = True
        ordering = ('-created_at',)

    objects = models.Manager()
