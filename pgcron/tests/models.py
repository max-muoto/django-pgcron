from __future__ import annotations

from django.db import models


class NameTestModel(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        db_table = "name_model"
