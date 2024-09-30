from django import forms
from .models import (
    Salon, BarberType, Barber, Client, Commission, Currency, CashRegister,
    PaymentType, Payment, Transaction, Hairstyle, HairstyleTariffHistory,
    Shave, Item, ItemUsed, ItemPurchase
)

class TailwindFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50'
            })

class SalonForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Salon
        fields = ['name', 'description', 'address', 'phone', 'email', 'owner', 'is_active']

class BarberTypeForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = BarberType
        fields = ['name', 'description', 'salon']

class BarberForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Barber
        fields = ['user', 'salon', 'barber_type', 'contract', 'phone', 'address', 'start_date', 'end_date', 'is_active']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class ClientForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Client
        fields = ['user', 'name', 'salon', 'address', 'phone']

class CommissionForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Commission
        fields = ['barber', 'percentage', 'fixed_amount', 'effective_date']
        widgets = {
            'effective_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class CurrencyForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Currency
        fields = ['code', 'name', 'is_default', 'salon']

class CashRegisterForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = CashRegister
        fields = ['name', 'balance_profit', 'balance_cash', 'currency', 'salon']

class PaymentTypeForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = PaymentType
        fields = ['name', 'description', 'is_active', 'salon']

class PaymentForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['barber', 'amount', 'currency', 'exchange_rate', 'start_date', 'end_date', 'payment_type', 'cashregister', 'date_payment', 'salon']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'date_payment': forms.DateInput(attrs={'type': 'date'}),
        }

class TransactionForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['trans_name', 'amount', 'currency', 'exchange_rate', 'date_trans', 'trans_type', 'cashregister', 'salon']
        widgets = {
            'date_trans': forms.DateInput(attrs={'type': 'date'}),
        }

class HairstyleForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Hairstyle
        fields = ['name', 'current_tariff', 'currency', 'salon', 'image']

class HairstyleTariffHistoryForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = HairstyleTariffHistory
        fields = ['hairstyle', 'tariff', 'effective_date']
        widgets = {
            'effective_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class ShaveForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Shave
        fields = ['barber', 'hairstyle', 'amount', 'currency', 'exchange_rate', 'client', 'cashregister', 'date_shave', 'salon', 'status']
        widgets = {
            'date_shave': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class ItemForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'item_purpose', 'price', 'currency', 'exchange_rate', 'salon', 'current_stock']

class ItemUsedForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = ItemUsed
        fields = ['item', 'shave', 'barber', 'quantity', 'note', 'salon']

class ItemPurchaseForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = ItemPurchase
        fields = ['item', 'quantity', 'purchase_price', 'currency', 'exchange_rate', 'purchase_date', 'supplier', 'cashregister', 'salon']
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
        }

# Additional utility forms

class DateRangeForm(TailwindFormMixin, forms.Form):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

class BarberCommissionForm(TailwindFormMixin, forms.Form):
    barber = forms.ModelChoiceField(queryset=Barber.objects.all())
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))