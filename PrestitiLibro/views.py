from django.shortcuts import render,get_object_or_404,redirect
from .models import Catalogo,Prestiti,Recensione
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone 
from ollama import chat
from ollama import ChatResponse
from django.http import JsonResponse
import datetime
import re
# Create your views here.

def home(request):
    return render(request, 'PrestitiLibro/base.html')

def lista_utenti(request):
    utenti = User.objects.all()
    return render(request, 'PrestitiLibro/lista_utenti.html', {'utenti': utenti})
@login_required
def prestiti_utente(request):
    prestiti = Prestiti.objects.filter(utente_id=request.user).order_by('-data_prestito')
    return render(request, 'PrestitiLibro/prestiti_utente.html', {'prestiti': prestiti})

def lista_catalogo(request):
    query = request.GET.get('q', '')
    cataloghi = Catalogo.objects.all()
    if query:
        cataloghi = cataloghi.filter(Q(titolo__icontains=query) | Q(autore__icontains=query))
    cataloghi = cataloghi.order_by('titolo')
    
    paginator = Paginator(cataloghi, 10)  # 10 libri per pagina
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    print("QuerySet:", cataloghi)  # Debug
    print("Page object:", page_obj)  # Debug
    
    return render(request, 'PrestitiLibro/lista_catalogo.html', {'page_obj': page_obj, 'query': query})




@login_required
def richiedi_prestito(request, libro_id):
    libro = get_object_or_404(Catalogo, id=libro_id)
    if Prestiti.objects.filter(utente_id=request.user, catalogo_id=libro, restituito=False).exists():
        messages.error(request, f"Hai già un prestito attivo per '{libro.titolo}'.")
        return redirect('catalogo')
   
    max_prestiti = 3 
    if Prestiti.objects.filter(utente_id=request.user, restituito=False).count() >= max_prestiti:
        messages.error(request, 'Hai raggiunto il limite massimo di prestiti attivi.')
        return redirect('catalogo')
    if libro.disponibilità:
        Prestiti.objects.create(
            utente_id=request.user,
            catalogo_id=libro,
            data_prestito=timezone.now().date(),
            data_scadenza=timezone.now().date() + timedelta(days=14),
            restituito=False
        )
        libro.disponibilità = False
        libro.save()
        messages.success(request, f"Prestito di '{libro.titolo}' richiesto con successo!")
    else:
        messages.error(request, f"Il libro '{libro.titolo}' non è disponibile.")
    return redirect('catalogo')

@login_required
@login_required
def restituisci_prestito(request, libro_id):
    libro = get_object_or_404(Catalogo, id=libro_id)
    prestiti = Prestiti.objects.filter(
        catalogo_id=libro,
        utente_id=request.user,
        restituito=False
    )
    
    if not prestiti.exists():
        messages.error(request, f"Non hai un prestito attivo per '{libro.titolo}'.")
        return redirect('prestiti')
    
    if prestiti.count() > 1:
     
        messages.warning(request, f"Anomalia: trovati più prestiti attivi per '{libro.titolo}'. Restituito il più recente.")
        
        prestito = prestiti.order_by('-data_prestito').first()
    else:
        prestito = prestiti.first()
    
    prestito.restituito = True
    prestito.data_restituzione = timezone.now().date()
    libro.disponibilità = True
    libro.save()
    prestito.save()
    messages.success(request, f"Hai restituito '{libro.titolo}' con successo!")
    return redirect('prestiti')


def registrazione(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registrazione completata! Ora puoi accedere.')
            return redirect('login')
        else:
            messages.error(request, 'Errore nella registrazione. Correggi i dati.')
    else:
        form = UserCreationForm()
    return render(request, 'PrestitiLibro/registration/registrazione.html', {'form': form})

@login_required
def aggiungi_recensione(request, libro_id):
    libro = get_object_or_404(Catalogo, id=libro_id)
    if request.method == 'POST':
        valutazione = request.POST.get('voto')
        commento = request.POST.get('commento', '')
        if valutazione and int(valutazione) in range(1, 6):
            Recensione.objects.create(
                utente_id=request.user,
                catalogo_id=libro,
                valutazione=valutazione,
                commento=commento
            )
            messages.success(request, 'Recensione aggiunta con successo!')
            return redirect('catalogo')
        else:
            messages.error(request, 'Voto non valido.')
    return render(request, 'PrestitiLibro/aggiungi_recensione.html', {'libro': libro})



def risposta(request):
    # Ottieni il mese e l'anno corrente in italiano
    now = datetime.datetime.now()
    month_names = {
        1: 'gennaio', 2: 'febbraio', 3: 'marzo', 4: 'aprile',
        5: 'maggio', 6: 'giugno', 7: 'luglio', 8: 'agosto',
        9: 'settembre', 10: 'ottobre', 11: 'novembre', 12: 'dicembre'
    }
    current_month = month_names[now.month]
    current_year = now.year
    current_period = f"{current_month} {current_year}"
    
    # Prompt dinamico
    prompt = f"Quali sono i 5 libri più letti in Italia a {current_period}? Elenca titolo, autore e un motivo breve per ciascuno."
    
    try:
        response = chat(
            model='gemma3:4b', 
            messages=[{'role': 'user', 'content': prompt}]
        )
        answer = response['message']['content']
        context = {
            'current_month': current_month,
            'period': current_period,
            'answer': answer,
        }
        # Passa la risposta e il periodo al template (opzionale, per mostrare il mese)
        return render(request, 'PrestitiLibro/risposta.html', context)
    except Exception as e:
        return render(request, 'PrestitiLibro/risposta.html', {'error': f'Errore Ollama: {str(e)}'})
  