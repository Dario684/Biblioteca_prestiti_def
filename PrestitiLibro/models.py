from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User


class Catalogo(models.Model):
    titolo = models.CharField(max_length=50)
    autore = models.CharField(max_length=40)
    data_pubblicazione = models.DateField()
    disponibilità = models.BooleanField(default = True)

    def __str__(self):
        return self.titolo

class Prestiti(models.Model):
    utente_id = models.ForeignKey(User, on_delete=models.CASCADE)
    catalogo_id = models.ForeignKey(Catalogo, on_delete=models.CASCADE)
    data_prestito = models.DateField(auto_now_add=True)
    data_scadenza = models.DateField()
    data_restituzione = models.DateField(null=True, blank=True)
    restituito = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.catalogo_id.titolo} - {self.utente_id.username}"

    
class Recensione(models.Model):
    utente_id = models.ForeignKey(User, on_delete= models.CASCADE)
    catalogo_id = models.ForeignKey(Catalogo, on_delete = models.CASCADE)
    valutazione = models.IntegerField(choices = [(i, i) for i in range(1,6)])
    commento = models.TextField(blank = True)
    data = models.DateField(auto_now_add = True)
    
    def __str__(self):
        return f"{self.utente_id.username}-{self.catalogo_id.titolo}-({self.valutazione})"