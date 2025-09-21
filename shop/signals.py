from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import OrderItem


@receiver(post_save, sender=OrderItem)
def decrease_balance_on_item_save(sender, instance, created, **kwargs):
    member = instance.order.by
    amount = instance.quantity * instance.product.price

    if created:
        member.balance -= amount
    else:
        old_quantity = sender.objects.get(pk=instance.pk).quantity if instance.pk else 0
        diff = (instance.quantity - old_quantity) * instance.product.price
        member.balance -= diff

    member.save(update_fields=["balance"])


@receiver(post_delete, sender=OrderItem)
def increase_balance_on_item_delete(sender, instance, **kwargs):
    member = instance.order.by
    amount = instance.quantity * instance.product.price
    member.balance += amount
    member.save(update_fields=["balance"])
