from django.contrib import admin
from .models import Catalogo
from .models import Prestiti
from .models import Recensione

admin.site.register(Catalogo)
admin.site.register(Prestiti)
admin.site.register(Recensione)

# Register your models here.
