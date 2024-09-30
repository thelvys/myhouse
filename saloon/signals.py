# signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Shave, ItemUsed, ItemPurchase, Payment, Transaction, Item
from .services import CashRegisterService
from decimal import Decimal

@receiver(post_save, sender=Shave)
def update_cashregister_on_shave(sender, instance, created, **kwargs):
    if instance.status == Shave.Status.COMPLETED:
        CashRegisterService.update_balance(instance.cashregister)

@receiver(post_save, sender=Transaction)
def update_cashregister_on_transaction(sender, instance, created, **kwargs):
    CashRegisterService.update_balance(instance.cashregister)

@receiver(post_save, sender=ItemUsed)
def update_stock_and_cashregister_on_item_used(sender, instance, created, **kwargs):
    if created:
        instance.item.current_stock -= instance.quantity
        instance.item.save()
    CashRegisterService.update_balance(instance.shave.cashregister)

@receiver(post_save, sender=ItemPurchase)
def update_stock_and_cashregister_on_item_purchase(sender, instance, created, **kwargs):
    if created:
        instance.item.current_stock += instance.quantity
        instance.item.save()
    CashRegisterService.update_balance(instance.cashregister)

@receiver(post_save, sender=Payment)
def update_cashregister_on_payment(sender, instance, created, **kwargs):
    CashRegisterService.update_balance(instance.cashregister)

@receiver(post_delete, sender=Shave)
def revert_cashregister_on_shave_delete(sender, instance, **kwargs):
    if instance.status == Shave.Status.COMPLETED:
        CashRegisterService.update_balance(instance.cashregister)

@receiver(post_delete, sender=ItemUsed)
def revert_stock_and_cashregister_on_item_used_delete(sender, instance, **kwargs):
    instance.item.current_stock += instance.quantity
    instance.item.save()
    CashRegisterService.update_balance(instance.shave.cashregister)

@receiver(post_delete, sender=ItemPurchase)
def revert_stock_and_cashregister_on_item_purchase_delete(sender, instance, **kwargs):
    instance.item.current_stock -= instance.quantity
    instance.item.save()
    CashRegisterService.update_balance(instance.cashregister)

@receiver(post_delete, sender=Payment)
def revert_cashregister_on_payment_delete(sender, instance, **kwargs):
    CashRegisterService.update_balance(instance.cashregister)

@receiver(post_delete, sender=Transaction)
def revert_cashregister_on_transaction_delete(sender, instance, **kwargs):
    CashRegisterService.update_balance(instance.cashregister)

