from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import CatalogoAPIView
from .views import CatalogoViewSet
from . import views

router = DefaultRouter()
router.register(r'catalogo', CatalogoViewSet)

urlpatterns = [
    path('',views.home, name = 'home'),
    path('catalogo/', views.lista_catalogo, name='catalogo'),
    path('prestiti/', views.prestiti_utente, name ='prestiti'),
    path('utenti/',views.lista_utenti, name = "utenti"),
    path('richiedi_prestito/<int:libro_id>/', views.richiedi_prestito, name="richiedi_prestito"),
    path('restituisci_prestito/<int:libro_id>/', views.restituisci_prestito, name="restituisci_prestito"),
    path('registrazione/', views.registrazione, name = "registrazione"),
    path('recensione/<int:libro_id>/', views.aggiungi_recensione, name = "aggiungi_recensione"),
    path('risposta/', views.risposta, name = "risposta"),
    path('api/', CatalogoAPIView.as_view(), name ="api"),
    path('custom-api/', include(router.urls)),
]