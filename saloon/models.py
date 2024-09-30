# models.py

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.db.models import Sum, F
from django.utils import timezone
from django.conf import settings
from decimal import Decimal

# Constants
DECIMAL_MAX_DIGITS = 19
DECIMAL_PLACES = 2

class TimestampMixin(models.Model):
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    modified_at = models.DateTimeField(_("Modified at"), auto_now=True)

    class Meta:
        abstract = True

class Salon(TimestampMixin):
    name = models.CharField(_("Name"), max_length=255, unique=True)
    description = models.TextField(_("Description"), blank=True)
    address = models.CharField(_("Address"), max_length=255, blank=True, null=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."))
    phone = models.CharField(_("Phone"), validators=[phone_regex], max_length=17, blank=True, null=True)
    email = models.EmailField(_("Email"), blank=True, null=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_salons', verbose_name=_("Owner"))
    image = models.ImageField(_("Image"), upload_to='salons/', null=True, blank=True)
    is_active = models.BooleanField(_("Is active"), default=True)

    def __str__(self):
        return self.name

class BarberType(TimestampMixin):
    name = models.CharField(_("Name"), max_length=255)
    description = models.TextField(_("Description"), blank=True)
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='barber_types', verbose_name=_("Salon"))

    def __str__(self):
        return f"{self.name} - {self.salon.name}"

    class Meta:
        unique_together = ('name', 'salon')

class Barber(TimestampMixin):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("user"))
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='barbers', verbose_name=_("Salon"))
    barber_type = models.ForeignKey(BarberType, on_delete=models.CASCADE, verbose_name=_("barber type"))
    contract = models.FileField(_("Contract"), upload_to="contracts/", null=True, blank=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."))
    phone = models.CharField(_("Phone"), validators=[phone_regex], max_length=17, blank=True, null=True)
    address = models.CharField(_("Address"), max_length=255, null=True, blank=True)
    start_date = models.DateField(_("Start date"))
    end_date = models.DateField(_("End date"), null=True, blank=True)
    is_active = models.BooleanField(_("Is active"), default=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.salon.name if self.salon else 'No Salon'}"

    def clean(self):
        super().clean()
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError(_("Start date must be before end date."))
        if self.salon and self.barber_type and self.barber_type.salon != self.salon:
            raise ValidationError(_("Barber type must belong to the same salon."))
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class Client(TimestampMixin):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='clients', verbose_name=_("User"))
    name = models.CharField(_("Name"), max_length=255)
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='clients', verbose_name=_("Salon"))
    address = models.CharField(_("Address"), max_length=255, null=True, blank=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."))
    phone = models.CharField(_("Phone"), validators=[phone_regex], max_length=17, blank=True, null=True)

    def __str__(self):
        return self.name

class Commission(TimestampMixin):
    barber = models.ForeignKey(Barber, on_delete=models.CASCADE, related_name='commissions', verbose_name=_("Barber"))
    percentage = models.DecimalField(_("Commission Percentage"), max_digits=5, decimal_places=2, default=0.00) 
    fixed_amount = models.DecimalField(_("Fixed Amount"), max_digits=DECIMAL_MAX_DIGITS, decimal_places=DECIMAL_PLACES, default=0.00) 
    effective_date = models.DateTimeField(_("Effective Date"), default=timezone.now)

    def __str__(self):
        return f"{self.barber} - {self.percentage}% / {self.fixed_amount} - {self.effective_date}"

    class Meta:
        ordering = ['-effective_date']

class Currency(TimestampMixin):
    code = models.CharField(_("Code"), max_length=3)
    name = models.CharField(_("Name"), max_length=50)
    is_default = models.BooleanField(_("Is default"), default=False)
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='currencies', verbose_name=_("Salon"))

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        unique_together = ('code', 'salon')

class CashRegister(TimestampMixin):
    name = models.CharField(_("Name"), max_length=255)
    balance_profit = models.DecimalField(_("Profit Balance"), max_digits=DECIMAL_MAX_DIGITS, decimal_places=DECIMAL_PLACES, default=0)
    balance_cash = models.DecimalField(_("Cash Balance"), max_digits=DECIMAL_MAX_DIGITS, decimal_places=DECIMAL_PLACES, default=0)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name='cash_registers')
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='cash_registers', verbose_name=_("Salon"))
        
    def __str__(self):
        return f"{self.name} - {self.salon.name}"

class PaymentType(TimestampMixin):
    name = models.CharField(_("Name"), max_length=50)
    description = models.TextField(_("Description"), blank=True)
    is_active = models.BooleanField(_("Is active"), default=True)
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='payment_types', verbose_name=_("Salon"))

    def __str__(self):
        return self.name

class Payment(TimestampMixin):
    barber = models.ForeignKey(Barber, on_delete=models.CASCADE, related_name='payments', verbose_name=_("Barber"))
    amount = models.DecimalField(_("Amount"), max_digits=DECIMAL_MAX_DIGITS, decimal_places=DECIMAL_PLACES)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, verbose_name=_("Currency"))
    exchange_rate = models.DecimalField(_("Exchange rate"), max_digits=10, decimal_places=6, default=1.000000)
    amount_in_default_currency = models.DecimalField(_("Amount in default currency"), max_digits=DECIMAL_MAX_DIGITS, decimal_places=DECIMAL_PLACES, default=0)
    start_date = models.DateField(_("Start date"))
    end_date = models.DateField(_("End date"))
    payment_type = models.ForeignKey(PaymentType, on_delete=models.PROTECT, verbose_name=_("Payment type"))
    cashregister = models.ForeignKey(CashRegister, on_delete=models.CASCADE, related_name='payments', verbose_name=_("Cash Register"))
    date_payment = models.DateField(_("Payment date"), default=timezone.now)
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='payments', verbose_name=_("Salon"))

    def __str__(self):
        return f"{self.barber} - {self.amount} {self.currency.code} - {self.payment_type}"

    def clean(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError(_("Start date must be before end date."))
        if self.amount <= 0:
            raise ValidationError(_("Amount must be greater than zero."))
        if self.barber.salon != self.salon:
            raise ValidationError(_("Barber must belong to the same salon as the payment."))

class Transaction(TimestampMixin):
    class TransactionType(models.TextChoices):
        INCOME = 'INCOME', _('Income')
        EXPENSE = 'EXPENSE', _('Expense')

    trans_name = models.CharField(_("Description of Transaction"), max_length=255)
    amount = models.DecimalField(_("Amount"), max_digits=DECIMAL_MAX_DIGITS, decimal_places=DECIMAL_PLACES)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, verbose_name=_("Currency"))
    exchange_rate = models.DecimalField(_("Exchange rate"), max_digits=10, decimal_places=6, default=1.000000)
    amount_in_default_currency = models.DecimalField(_("Amount in default currency"), max_digits=DECIMAL_MAX_DIGITS, decimal_places=DECIMAL_PLACES, default=0)
    date_trans = models.DateField(_("Transaction date"), default=timezone.now)
    trans_type = models.CharField(_("Transaction type"), max_length=10, choices=TransactionType.choices)
    cashregister = models.ForeignKey(CashRegister, on_delete=models.CASCADE, related_name='transactions', verbose_name=_("Cash Register"))
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='transactions', verbose_name=_("Salon"))

    def __str__(self):
        return f"{self.trans_name} - {self.amount} {self.currency.code} - {self.get_trans_type_display()}"

    def clean(self):
        if self.amount <= 0:
            raise ValidationError(_("Amount must be greater than zero."))
        if self.cashregister.salon != self.salon:
            raise ValidationError(_("Cash register must belong to the same salon as the transaction."))

    class Meta:
        unique_together = ['trans_name', 'salon', 'date_trans']

class Hairstyle(TimestampMixin):
    name = models.CharField(_("Name"), max_length=255)
    current_tariff = models.DecimalField(_("Current Tariff"), max_digits=DECIMAL_MAX_DIGITS, decimal_places=DECIMAL_PLACES)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, verbose_name=_("Currency"))
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='hairstyles', verbose_name=_("Salon"))
    image = models.ImageField(_("Image"), upload_to='hairstyles/', null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.salon.name}"

    def clean(self):
        if self.current_tariff < 0:
            raise ValidationError(_("Current tariff cannot be negative."))

    class Meta:
        unique_together = ['name', 'salon']

class HairstyleTariffHistory(TimestampMixin):
    hairstyle = models.ForeignKey(Hairstyle, on_delete=models.CASCADE, related_name='tariff_history', verbose_name=_("Hairstyle"))
    tariff = models.DecimalField(_("Tariff"), max_digits=DECIMAL_MAX_DIGITS, decimal_places=DECIMAL_PLACES)
    effective_date = models.DateTimeField(_("Effective Date"), default=timezone.now)

    def __str__(self):
        return f"{self.hairstyle.name} - {self.tariff} - {self.effective_date}"

    class Meta:
        ordering = ['-effective_date']

class Shave(TimestampMixin):
    class Status(models.TextChoices):
        SCHEDULED = 'SCHEDULED', _('Scheduled')
        IN_PROGRESS = 'IN_PROGRESS', _('In Progress')
        COMPLETED = 'COMPLETED', _('Completed')
        CANCELLED = 'CANCELLED', _('Cancelled')

    barber = models.ForeignKey(Barber, on_delete=models.PROTECT, related_name='shaves', verbose_name=_("Barber"))
    hairstyle = models.ForeignKey(Hairstyle, on_delete=models.PROTECT, related_name='shaves', verbose_name=_("Hairstyle"))
    amount = models.DecimalField(_("Amount"), max_digits=DECIMAL_MAX_DIGITS, decimal_places=DECIMAL_PLACES)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name='shaves', verbose_name=_("Currency"))
    exchange_rate = models.DecimalField(_("Exchange rate"), max_digits=10, decimal_places=6, default=1.000000)
    amount_in_default_currency = models.DecimalField(_("Amount in default currency"), max_digits=DECIMAL_MAX_DIGITS, decimal_places=DECIMAL_PLACES)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, related_name='shaves', verbose_name=_("Client"))
    cashregister = models.ForeignKey(CashRegister, on_delete=models.PROTECT, related_name='shaves', verbose_name=_("Cash Register"))
    date_shave = models.DateTimeField(_("Shave date"), default=timezone.now)
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='shaves', verbose_name=_("Salon"))
    status = models.CharField(_("Status"), max_length=20, choices=Status.choices, default=Status.SCHEDULED)

    def __str__(self):
        return f"{self.barber} - {self.hairstyle} - {self.date_shave}"

    def clean(self):
        if self.amount < 0:
            raise ValidationError(_("Amount cannot be negative."))
        if self.barber.salon != self.salon:
            raise ValidationError(_("Barber must belong to the same salon as the shave."))
        if self.hairstyle.salon != self.salon:
            raise ValidationError(_("Hairstyle must belong to the same salon as the shave."))
        if self.cashregister.salon != self.salon:
            raise ValidationError(_("Cash register must belong to the same salon as the shave."))

class Item(TimestampMixin):
    name = models.CharField(_("Name"), max_length=255)
    item_purpose = models.ManyToManyField(Hairstyle, related_name='items', verbose_name=_("Item purpose"))
    price = models.DecimalField(_("Price"), max_digits=DECIMAL_MAX_DIGITS, decimal_places=DECIMAL_PLACES)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name='items', verbose_name=_("Currency"))
    exchange_rate = models.DecimalField(_("Exchange rate"), max_digits=10, decimal_places=6, default=1.000000)
    amount_in_default_currency = models.DecimalField(_("Amount in default currency"), max_digits=DECIMAL_MAX_DIGITS, decimal_places=DECIMAL_PLACES)
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='items', verbose_name=_("Salon"))
    current_stock = models.PositiveIntegerField(_("Current stock"), default=0)

    def __str__(self):
        return f"{self.name} - {self.salon.name}"
    
    def clean(self):
        if self.price < 0:
            raise ValidationError(_("Price cannot be negative."))

    class Meta:
        verbose_name = _("Item")
        verbose_name_plural = _("Items")
        unique_together = ['name', 'salon']

class ItemUsed(TimestampMixin):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='uses', verbose_name=_("Item"))
    shave = models.ForeignKey(Shave, on_delete=models.CASCADE, related_name='items_used', verbose_name=_("Shave"))
    barber = models.ForeignKey(Barber, on_delete=models.PROTECT, verbose_name=_("Barber"))
    quantity = models.PositiveIntegerField(_("Quantity"))
    note = models.TextField(_("Note"), blank=True)
    used_date = models.DateField(_("Used date"), default=timezone.now)
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='items_used', verbose_name=_("Salon"))

    def __str__(self):
        return f"{self.item} - {self.quantity} - {self.shave}"

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError(_("Quantity must be positive."))
        if self.item.current_stock < self.quantity:
            raise ValidationError(_("Not enough items in stock."))
        if self.shave.status != Shave.Status.COMPLETED:
            raise ValidationError(_("Items can only be used for completed shaves."))
        if self.item.salon != self.salon or self.shave.salon != self.salon or self.barber.salon != self.salon:
            raise ValidationError(_("Item, Shave, and Barber must belong to the same salon."))

    class Meta:
        unique_together = ('item', 'shave', 'salon')

    def get_amount_in_default_currency(self):
        avg_purchase_price = self.item.purchases.aggregate(
            avg_price=Sum('purchase_price_in_default_currency') / Sum('quantity')
        )['avg_price'] or Decimal('0.00')
        return avg_purchase_price * self.quantity

class ItemPurchase(TimestampMixin):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='purchases', verbose_name=_("Item"))
    quantity = models.PositiveIntegerField(_("Quantity"))
    purchase_price = models.DecimalField(_("Purchase price"), max_digits=DECIMAL_MAX_DIGITS, decimal_places=DECIMAL_PLACES)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, verbose_name=_("Currency"))
    exchange_rate = models.DecimalField(_("Exchange rate"), max_digits=10, decimal_places=6, default=1.000000)
    total_purchase_price = models.DecimalField(_("Total purchase price"), max_digits=DECIMAL_MAX_DIGITS, decimal_places=DECIMAL_PLACES, default=0)
    purchase_price_in_default_currency = models.DecimalField(_("Purchase price in default currency"), max_digits=DECIMAL_MAX_DIGITS, decimal_places=DECIMAL_PLACES)
    purchase_date = models.DateField(_("Purchase date"), default=timezone.now)
    supplier = models.CharField(_("Supplier"), max_length=255, blank=True)
    cashregister = models.ForeignKey(CashRegister, on_delete=models.PROTECT, related_name='purchases', verbose_name=_("Cash Register"))
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='item_purchases', verbose_name=_("Salon"))

    def __str__(self):
        return f"{self.item.name} - {self.quantity} - {self.purchase_date}"
    
    def save(self, *args, **kwargs):
        if self.quantity is not None and self.purchase_price is not None:
            self.total_purchase_price = self.purchase_price * self.quantity
            if self.exchange_rate is not None:
                self.purchase_price_in_default_currency = self.total_purchase_price * self.exchange_rate
        super().save(*args, **kwargs)
    
    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super().from_db(db, field_names, values)
        instance._loaded_values = dict(zip(field_names, values))
        return instance
    def calculate_total_purchase_price(self):
        if 'quantity' in self._loaded_values and 'purchase_price' in self._loaded_values:
            return self._loaded_values['purchase_price'] * self._loaded_values['quantity']
        return self.quantity * self.purchase_price
    
    def clean(self):
        if self.purchase_price <= 0:
            raise ValidationError(_("Purchase price must be positive."))
        if self.quantity <= 0:
            raise ValidationError(_("Quantity must be positive."))
        if self.item.salon != self.salon or self.cashregister.salon != self.salon:
            raise ValidationError(_("Item and Cash Register must belong to the same salon as the purchase."))

