#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AxeCollection.settings')
django.setup()

from axes.models import Transaction

print("Transaktioner i databasen:")
print("ID | Yxa ID | Typ | Pris | Frakt | Kontakt")
print("-" * 50)

for t in Transaction.objects.all()[:15]:
    contact_name = t.contact.name if t.contact else "Ingen"
    print(f"{t.id:2} | {t.axe.id:6} | {t.type:4} | {t.price:6} | {t.shipping_cost:5} | {contact_name}")

print("\nSpecifikt för yxa 38:")
for t in Transaction.objects.filter(axe_id=38):
    contact_name = t.contact.name if t.contact else "Ingen"
    print(f"ID: {t.id}, Typ: {t.type}, Pris: {t.price}, Frakt: {t.shipping_cost}, Kontakt: {contact_name}")

print("\nSpecifikt för yxa 172:")
for t in Transaction.objects.filter(axe_id=172):
    contact_name = t.contact.name if t.contact else "Ingen"
    print(f"ID: {t.id}, Typ: {t.type}, Pris: {t.price}, Frakt: {t.shipping_cost}, Kontakt: {contact_name}")

print("\nAlla transaktioner med negativa priser:")
for t in Transaction.objects.filter(price__lt=0):
    contact_name = t.contact.name if t.contact else "Ingen"
    print(f"Yxa {t.axe.id}: ID {t.id}, Typ: {t.type}, Pris: {t.price}, Frakt: {t.shipping_cost}, Kontakt: {contact_name}")

print("\nAlla transaktioner med negativa fraktkostnader:")
for t in Transaction.objects.filter(shipping_cost__lt=0):
    contact_name = t.contact.name if t.contact else "Ingen"
    print(f"Yxa {t.axe.id}: ID {t.id}, Typ: {t.type}, Pris: {t.price}, Frakt: {t.shipping_cost}, Kontakt: {contact_name}") 