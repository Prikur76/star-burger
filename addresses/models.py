from django.db import models


class Place(models.Model):
    address = models.CharField(unique=True, max_length=255, verbose_name='aдрес')
    latitude = models.FloatField(verbose_name='широта', default=0.0)
    longitude = models.FloatField(verbose_name='долгота', default=0.0)
    created_at = models.DateTimeField(verbose_name='дата создания', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'адрес'
        verbose_name_plural = 'адреса'

    def __str__(self):
        return f"{self.address} ({self.latitude}, {self.longitude})"
