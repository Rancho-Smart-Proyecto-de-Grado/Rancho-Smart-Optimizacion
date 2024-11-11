from django.db import models

class Vaca(models.Model):
    id = models.AutoField(primary_key=True)
    raza = models.CharField(max_length=50)
    genero = models.CharField(max_length=10)
    peso = models.FloatField()
    produccion_leche_anual = models.FloatField()
    enfermedad = models.BooleanField(default=False)
    problemas_reproductivos = models.BooleanField(default=False)
    familiares = models.JSONField(default=list)  # Almacena IDs de familiares

    def __str__(self):
        return f"{self.raza} ({self.genero})"