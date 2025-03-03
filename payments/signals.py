from django.db.models.signals import post_save
from django.dispatch import receiver
from payments.models import Address

@receiver(post_save, sender=Address)
def set_first_address_as_default(sender, instance, created, **kwargs):
    """
    Définit automatiquement la première adresse comme adresse par défaut.
    Désactive les autres si une nouvelle adresse est mise par défaut.
    """
    if created:
        # Si aucune adresse par défaut n'existe pour ce type, la première devient par défaut
        if not Address.objects.filter(user=instance.user, address_type=instance.address_type, is_default=True).exists():
            Address.objects.filter(id=instance.id).update(is_default=True)
    
    elif instance.is_default:
        # Si une nouvelle adresse est définie par défaut, les autres doivent être désactivées
        Address.objects.filter(user=instance.user, address_type=instance.address_type).exclude(id=instance.id).update(is_default=False)

@receiver(post_save, sender=Address)
def delete_non_default_addresses(sender, instance, created, **kwargs):
    """
    Supprime les anciennes adresses qui ne sont pas par défaut après chaque ajout/modification.
    """
    if instance.is_default:
        Address.objects.filter(user=instance.user, address_type=instance.address_type, is_default=False).delete()
