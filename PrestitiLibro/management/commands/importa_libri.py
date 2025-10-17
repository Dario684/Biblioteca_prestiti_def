from django.core.management.base import BaseCommand
from PrestitiLibro.models import Catalogo
import csv
from datetime import datetime

class Command(BaseCommand):
    help = 'Importa libri da un file CSV'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Percorso del file CSV')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        try:
            with open(csv_file, newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        data_pubblicazione = datetime.strptime(row['data_pubblicazione'], '%Y-%m-%d').date()
                        disponibilità = row['disponibilità'].lower() in ('true', '1', 'yes')
                        libro = Catalogo.objects.create(
                            titolo=row['titolo'],
                            autore=row['autore'],
                            data_pubblicazione=data_pubblicazione,
                            disponibilità=disponibilità
                        )
                        self.stdout.write(self.style.SUCCESS(f"Importato: {libro.titolo}"))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Errore importando {row['titolo']}: {str(e)}"))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File {csv_file} non trovato."))