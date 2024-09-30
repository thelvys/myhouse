from decimal import Decimal
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Sum, Subquery, F, OuterRef, DecimalField
from django.db.models.expressions import ExpressionWrapper
from django.db.models.functions import Coalesce
from .models import Salon, Barber, Client, Hairstyle, Shave, Item, ItemPurchase, Commission, Currency, CashRegister, PaymentType, Payment, Transaction, HairstyleTariffHistory, ItemUsed
from .forms import (
    SalonForm, BarberForm, ClientForm, HairstyleForm, ShaveForm,
    ItemForm, ItemPurchaseForm, CommissionForm, CurrencyForm, CashRegisterForm, PaymentTypeForm, PaymentForm, TransactionForm, HairstyleTariffHistoryForm, ItemUsedForm
)

class OwnerRequiredMixin:
    def get_queryset(self):
        return super().get_queryset().filter(salon__owner=self.request.user)

class SalonOwnerRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not Salon.objects.filter(owner=request.user).exists():
            messages.error(request, "Vous devez d'abord créer un salon.")
            return redirect('salon_create')
        return super().dispatch(request, *args, **kwargs)

# Salon views
class SalonListView(LoginRequiredMixin, ListView):
    model = Salon
    template_name = 'saloon/salon_list.html'
    context_object_name = 'salons'

    def get_queryset(self):
        return Salon.objects.filter(owner=self.request.user)

class SalonDetailView(LoginRequiredMixin, DetailView):
    model = Salon
    template_name = 'saloon/salon_detail.html'

    def get_queryset(self):
        return Salon.objects.filter(owner=self.request.user)

class SalonCreateView(LoginRequiredMixin, CreateView):
    model = Salon
    form_class = SalonForm
    template_name = 'saloon/generic_form.html'
    success_url = reverse_lazy('saloon:salon_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'Salon'
        return context

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class SalonUpdateView(LoginRequiredMixin, UpdateView):
    model = Salon
    form_class = SalonForm
    template_name = 'saloon/generic_form.html'
    success_url = reverse_lazy('saloon:salon_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'Salon'
        return context

    def get_queryset(self):
        return Salon.objects.filter(owner=self.request.user)

class SalonDeleteView(LoginRequiredMixin, DeleteView):
    model = Salon
    template_name = 'saloon/salon_confirm_delete.html'
    success_url = reverse_lazy('saloon:salon_list')

    def get_queryset(self):
        return Salon.objects.filter(owner=self.request.user)

# Barber views
class BarberListView(LoginRequiredMixin, SalonOwnerRequiredMixin, OwnerRequiredMixin, ListView):
    model = Barber
    template_name = 'saloon/barber_list.html'
    context_object_name = 'barbers'

    def get_queryset(self):
        salon_id = self.kwargs.get('salon_id')
        return Barber.objects.filter(salon__id=salon_id, salon__owner=self.request.user)

class BarberCreateView(LoginRequiredMixin, SalonOwnerRequiredMixin, CreateView):
    model = Barber
    form_class = BarberForm
    template_name = 'saloon/generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'Barber'
        return context

    def form_valid(self, form):
        salon = get_object_or_404(Salon, id=self.kwargs.get('salon_id'), owner=self.request.user)
        form.instance.salon = salon
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('saloon:barber_list', kwargs={'salon_id': self.object.salon.id})

class BarberUpdateView(LoginRequiredMixin, SalonOwnerRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Barber
    form_class = BarberForm
    template_name = 'saloon/generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'Barber'
        return context

    def get_success_url(self):
        return reverse_lazy('saloon:barber_list', kwargs={'salon_id': self.object.salon.id})

class BarberDeleteView(LoginRequiredMixin, SalonOwnerRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Barber
    template_name = 'saloon/generic_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('saloon:barber_list', kwargs={'salon_id': self.object.salon.id})

# Client views
class ClientListView(LoginRequiredMixin, SalonOwnerRequiredMixin, OwnerRequiredMixin, ListView):
    model = Client
    template_name = 'saloon/client_list.html'
    context_object_name = 'clients'

    def get_queryset(self):
        salon_id = self.kwargs.get('salon_id')
        return Client.objects.filter(salon__id=salon_id, salon__owner=self.request.user)

class ClientCreateView(LoginRequiredMixin, SalonOwnerRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'saloon/generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'Client'
        return context

    def form_valid(self, form):
        salon = get_object_or_404(Salon, id=self.kwargs.get('salon_id'), owner=self.request.user)
        form.instance.salon = salon
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('saloon:client_list', kwargs={'salon_id': self.object.salon.id})

class ClientUpdateView(LoginRequiredMixin, SalonOwnerRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'saloon/generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'Client'
        return context

    def get_success_url(self):
        return reverse_lazy('saloon:client_list', kwargs={'salon_id': self.object.salon.id})

class ClientDeleteView(LoginRequiredMixin, SalonOwnerRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Client
    template_name = 'saloon/generic_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('saloon:client_list', kwargs={'salon_id': self.object.salon.id})

# Hairstyle views
class HairstyleListView(LoginRequiredMixin, SalonOwnerRequiredMixin, OwnerRequiredMixin, ListView):
    model = Hairstyle
    template_name = 'saloon/hairstyle_list.html'
    context_object_name = 'hairstyles'

    def get_queryset(self):
        salon_id = self.kwargs.get('salon_id')
        return Hairstyle.objects.filter(salon__id=salon_id, salon__owner=self.request.user)

class HairstyleCreateView(LoginRequiredMixin, SalonOwnerRequiredMixin, CreateView):
    model = Hairstyle
    form_class = HairstyleForm
    template_name = 'saloon/generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'Hairstyle'
        return context

    def form_valid(self, form):
        salon = get_object_or_404(Salon, id=self.kwargs.get('salon_id'), owner=self.request.user)
        form.instance.salon = salon
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('saloon:hairstyle_list', kwargs={'salon_id': self.object.salon.id})

class HairstyleUpdateView(LoginRequiredMixin, SalonOwnerRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Hairstyle
    form_class = HairstyleForm
    template_name = 'saloon/generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'Hairstyle'
        return context

    def get_success_url(self):
        return reverse_lazy('saloon:hairstyle_list', kwargs={'salon_id': self.object.salon.id})

class HairstyleDeleteView(LoginRequiredMixin, SalonOwnerRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Hairstyle
    template_name = 'saloon/generic_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('saloon:hairstyle_list', kwargs={'salon_id': self.object.salon.id})

# Shave views
class ShaveListView(LoginRequiredMixin, SalonOwnerRequiredMixin, OwnerRequiredMixin, ListView):
    model = Shave
    template_name = 'saloon/shave_list.html'
    context_object_name = 'shaves'

    def get_queryset(self):
        salon_id = self.kwargs.get('salon_id')
        return Shave.objects.filter(salon__id=salon_id, salon__owner=self.request.user)

class ShaveCreateView(LoginRequiredMixin, SalonOwnerRequiredMixin, CreateView):
    model = Shave
    form_class = ShaveForm
    template_name = 'saloon/generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'Shave'
        return context

    def form_valid(self, form):
        salon = get_object_or_404(Salon, id=self.kwargs.get('salon_id'), owner=self.request.user)
        form.instance.salon = salon
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('saloon:shave_list', kwargs={'salon_id': self.object.salon.id})

class ShaveUpdateView(LoginRequiredMixin, SalonOwnerRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Shave
    form_class = ShaveForm
    template_name = 'saloon/generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'Shave'
        return context

    def get_success_url(self):
        return reverse_lazy('saloon:shave_list', kwargs={'salon_id': self.object.salon.id})

class ShaveDeleteView(LoginRequiredMixin, SalonOwnerRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Shave
    template_name = 'saloon/generic_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('saloon:shave_list', kwargs={'salon_id': self.object.salon.id})

# Item views
class ItemListView(LoginRequiredMixin, SalonOwnerRequiredMixin, OwnerRequiredMixin, ListView):
    model = Item
    template_name = 'saloon/item_list.html'
    context_object_name = 'items'

    def get_queryset(self):
        salon_id = self.kwargs.get('salon_id')
        
        items = Item.objects.filter(salon__id=salon_id, salon__owner=self.request.user).annotate(
            total_used=Coalesce(Sum('uses__quantity'), 0),
            total_purchased=Coalesce(Sum('purchases__quantity'), 0),
            total_purchase_amount=Coalesce(Sum('purchases__purchase_price_in_default_currency'), Decimal('0')),
            remaining_quantity=ExpressionWrapper(
                F('total_purchased') - F('total_used'),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            )
        ).select_related('salon', 'currency')

        for item in items:
            item_used_queryset = ItemUsed.objects.filter(item=item)
            item.total_used_amount = sum(use.get_amount_in_default_currency() for use in item_used_queryset)
            item.remaining_amount = item.total_purchase_amount - Decimal(str(item.total_used_amount))
            item.avg_remaining_price = item.remaining_amount / item.remaining_quantity if item.remaining_quantity else None

        return items

class ItemCreateView(LoginRequiredMixin, SalonOwnerRequiredMixin, CreateView):
    model = Item
    form_class = ItemForm
    template_name = 'saloon/generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'Item'
        return context

    def form_valid(self, form):
        salon = get_object_or_404(Salon, id=self.kwargs.get('salon_id'), owner=self.request.user)
        form.instance.salon = salon
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('saloon:item_list', kwargs={'salon_id': self.object.salon.id})

class ItemUpdateView(LoginRequiredMixin, SalonOwnerRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Item
    form_class = ItemForm
    template_name = 'saloon/generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'Item'
        return context

    def get_success_url(self):
        return reverse_lazy('saloon:item_list', kwargs={'salon_id': self.object.salon.id})

class ItemDeleteView(LoginRequiredMixin, SalonOwnerRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Item
    template_name = 'saloon/generic_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('saloon:item_list', kwargs={'salon_id': self.object.salon.id})

# ItemPurchase views
class ItemPurchaseListView(LoginRequiredMixin, SalonOwnerRequiredMixin, OwnerRequiredMixin, ListView):
    model = ItemPurchase
    template_name = 'saloon/item_purchase_list.html'
    context_object_name = 'purchases'

    def get_queryset(self):
        salon_id = self.kwargs.get('salon_id')
        return ItemPurchase.objects.filter(salon__id=salon_id, salon__owner=self.request.user)

class ItemPurchaseCreateView(LoginRequiredMixin, SalonOwnerRequiredMixin, CreateView):
    model = ItemPurchase
    form_class = ItemPurchaseForm
    template_name = 'saloon/generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'Item Purchase'
        return context

    def form_valid(self, form):
        salon = get_object_or_404(Salon, id=self.kwargs.get('salon_id'), owner=self.request.user)
        form.instance.salon = salon
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('saloon:item_purchase_list', kwargs={'salon_id': self.object.salon.id})

class ItemPurchaseUpdateView(LoginRequiredMixin, SalonOwnerRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = ItemPurchase
    form_class = ItemPurchaseForm
    template_name = 'saloon/generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'Item Purchase'
        return context

    def get_success_url(self):
        return reverse_lazy('saloon:item_purchase_list', kwargs={'salon_id': self.object.salon.id})

class ItemPurchaseDeleteView(LoginRequiredMixin, SalonOwnerRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = ItemPurchase
    template_name = 'saloon/generic_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('saloon:item_purchase_list', kwargs={'salon_id': self.object.salon.id})

# ItemUsed views
class ItemUsedListView(LoginRequiredMixin, SalonOwnerRequiredMixin, OwnerRequiredMixin, ListView):
    model = ItemUsed
    template_name = 'saloon/item_used_list.html'
    context_object_name = 'uses'

    def get_queryset(self):
        salon_id = self.kwargs.get('salon_id')
        return ItemUsed.objects.filter(salon__id=salon_id, salon__owner=self.request.user)

class ItemUsedCreateView(LoginRequiredMixin, SalonOwnerRequiredMixin, CreateView):
    model = ItemUsed
    form_class = ItemUsedForm
    template_name = 'saloon/generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'Item Used'
        return context

    def form_valid(self, form):
        salon = get_object_or_404(Salon, id=self.kwargs.get('salon_id'), owner=self.request.user)
        form.instance.salon = salon
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('saloon:item_used_list', kwargs={'salon_id': self.object.salon.id})

class ItemUsedUpdateView(LoginRequiredMixin, SalonOwnerRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = ItemUsed
    form_class = ItemUsedForm
    template_name = 'saloon/generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'Item Used'
        return context

    def get_success_url(self):
        return reverse_lazy('saloon:item_used_list', kwargs={'salon_id': self.object.salon.id})

class ItemUsedDeleteView(LoginRequiredMixin, SalonOwnerRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = ItemUsed
    template_name = 'saloon/generic_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('saloon:item_used_list', kwargs={'salon_id': self.object.salon.id})

# Commission views
class CommissionListView(LoginRequiredMixin, SalonOwnerRequiredMixin, OwnerRequiredMixin, ListView):
    model = Commission
    template_name = 'saloon/commission_list.html'
    context_object_name = 'commissions'

    def get_queryset(self):
        salon_id = self.kwargs.get('salon_id')
        return Commission.objects.filter(barber__salon__id=salon_id, barber__salon__owner=self.request.user)

class CommissionCreateView(LoginRequiredMixin, SalonOwnerRequiredMixin, CreateView):
    model = Commission
    form_class = CommissionForm
    template_name = 'saloon/generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'Commission'
        return context

    def form_valid(self, form):
        salon = get_object_or_404(Salon, id=self.kwargs.get('salon_id'), owner=self.request.user)
        form.instance.barber.salon = salon
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('saloon:commission_list', kwargs={'salon_id': self.kwargs.get('salon_id')})

class CommissionUpdateView(LoginRequiredMixin, SalonOwnerRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Commission
    form_class = CommissionForm
    template_name = 'saloon/generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'Commission'
        return context

    def get_success_url(self):
        return reverse_lazy('saloon:commission_list', kwargs={'salon_id': self.kwargs.get('salon_id')})

class CommissionDeleteView(LoginRequiredMixin, SalonOwnerRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Commission
    template_name = 'saloon/generic_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('saloon:commission_list', kwargs={'salon_id': self.kwargs.get('salon_id')})

# Currency views
class CurrencyListView(LoginRequiredMixin, SalonOwnerRequiredMixin, OwnerRequiredMixin, ListView):
    model = Currency
    template_name = 'saloon/currency_list.html'
    context_object_name = 'currencies'

    def get_queryset(self):
        salon_id = self.kwargs.get('salon_id')
        return Currency.objects.filter(salon__id=salon_id, salon__owner=self.request.user)

class CurrencyCreateView(LoginRequiredMixin, SalonOwnerRequiredMixin, CreateView):
    model = Currency
    form_class = CurrencyForm
    template_name = 'saloon/generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'Currency'
        return context

    def form_valid(self, form):
        salon = get_object_or_404(Salon, id=self.kwargs.get('salon_id'), owner=self.request.user)
        form.instance.salon = salon
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('saloon:currency_list', kwargs={'salon_id': self.kwargs.get('salon_id')})

class CurrencyUpdateView(LoginRequiredMixin, SalonOwnerRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Currency
    form_class = CurrencyForm
    template_name = 'saloon/generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'Currency'
        return context

    def get_success_url(self):
        return reverse_lazy('saloon:currency_list', kwargs={'salon_id': self.kwargs.get('salon_id')})

class CurrencyDeleteView(LoginRequiredMixin, SalonOwnerRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Currency
    template_name = 'saloon/generic_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('saloon:currency_list', kwargs={'salon_id': self.kwargs.get('salon_id')})

# Ajoutez des vues similaires pour CashRegister, PaymentType, Payment, Transaction, HairstyleTariffHistory, et ItemUsed

# ChashRegister views
class CashRegisterListView(LoginRequiredMixin, SalonOwnerRequiredMixin, OwnerRequiredMixin, ListView):
    model = CashRegister
    template_name = 'saloon/cash_register_list.html'
    context_object_name = 'cash_registers'

    def get_queryset(self):
        salon_id = self.kwargs.get('salon_id')
        return CashRegister.objects.filter(salon__id=salon_id, salon__owner=self.request.user)

class CashRegisterCreateView(LoginRequiredMixin, SalonOwnerRequiredMixin, CreateView):
    model = CashRegister
    form_class = CashRegisterForm
    template_name = 'saloon/generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'Cash Register'
        return context

    def form_valid(self, form):
        salon = get_object_or_404(Salon, id=self.kwargs.get('salon_id'), owner=self.request.user)
        form.instance.salon = salon
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('saloon:cash_register_list', kwargs={'salon_id': self.kwargs.get('salon_id')})

class CashRegisterUpdateView(LoginRequiredMixin, SalonOwnerRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = CashRegister
    form_class = CashRegisterForm
    template_name = 'saloon/generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'Cash Register'
        return context

    def get_success_url(self):
        return reverse_lazy('saloon:cash_register_list', kwargs={'salon_id': self.kwargs.get('salon_id')})

class CashRegisterDeleteView(LoginRequiredMixin, SalonOwnerRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = CashRegister
    template_name = 'saloon/generic_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('saloon:cash_register_list', kwargs={'salon_id': self.kwargs.get('salon_id')})

# PaymentType views
class PaymentTypeListView(LoginRequiredMixin, SalonOwnerRequiredMixin, OwnerRequiredMixin, ListView):
    model = PaymentType
    template_name = 'saloon/payment_type_list.html'
    context_object_name = 'payment_types'

    def get_queryset(self):
        salon_id = self.kwargs.get('salon_id')
        return PaymentType.objects.filter(salon__id=salon_id, salon__owner=self.request.user)

class PaymentTypeCreateView(LoginRequiredMixin, SalonOwnerRequiredMixin, CreateView):
    model = PaymentType
    form_class = PaymentTypeForm
    template_name = 'saloon/generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'Payment Type'
        return context

    def form_valid(self, form):
        salon = get_object_or_404(Salon, id=self.kwargs.get('salon_id'), owner=self.request.user)
        form.instance.salon = salon
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('saloon:payment_type_list', kwargs={'salon_id': self.kwargs.get('salon_id')})

class PaymentTypeUpdateView(LoginRequiredMixin, SalonOwnerRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = PaymentType
    form_class = PaymentTypeForm
    template_name = 'saloon/generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'Payment Type'
        return context

    def get_success_url(self):
        return reverse_lazy('saloon:payment_type_list', kwargs={'salon_id': self.kwargs.get('salon_id')})

class PaymentTypeDeleteView(LoginRequiredMixin, SalonOwnerRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = PaymentType
    template_name = 'saloon/generic_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('saloon:payment_type_list', kwargs={'salon_id': self.kwargs.get('salon_id')})

# Payment views
class PaymentListView(LoginRequiredMixin, SalonOwnerRequiredMixin, OwnerRequiredMixin, ListView):
    model = Payment
    template_name = 'saloon/payment_list.html'
    context_object_name = 'payments'

    def get_queryset(self):
        salon_id = self.kwargs.get('salon_id')
        return Payment.objects.filter(salon__id=salon_id, salon__owner=self.request.user)

class PaymentCreateView(LoginRequiredMixin, SalonOwnerRequiredMixin, CreateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'saloon/generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'Payment'
        return context

    def form_valid(self, form):
        salon = get_object_or_404(Salon, id=self.kwargs.get('salon_id'), owner=self.request.user)
        form.instance.salon = salon
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('saloon:payment_list', kwargs={'salon_id': self.kwargs.get('salon_id')})

class PaymentUpdateView(LoginRequiredMixin, SalonOwnerRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'saloon/generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'Payment'
        return context

    def get_success_url(self):
        return reverse_lazy('saloon:payment_list', kwargs={'salon_id': self.kwargs.get('salon_id')})

class PaymentDeleteView(LoginRequiredMixin, SalonOwnerRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Payment
    template_name = 'saloon/generic_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('saloon:payment_list', kwargs={'salon_id': self.kwargs.get('salon_id')})

# Transaction views
class TransactionListView(LoginRequiredMixin, SalonOwnerRequiredMixin, OwnerRequiredMixin, ListView):
    model = Transaction 
    template_name = 'saloon/transaction_list.html'
    context_object_name = 'transactions'

    def get_queryset(self):
        salon_id = self.kwargs.get('salon_id')
        return Transaction.objects.filter(salon__id=salon_id, salon__owner=self.request.user)

class TransactionCreateView(LoginRequiredMixin, SalonOwnerRequiredMixin, CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'saloon/generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'Transaction'
        return context

    def form_valid(self, form):
        salon = get_object_or_404(Salon, id=self.kwargs.get('salon_id'), owner=self.request.user)
        form.instance.salon = salon
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('saloon:transaction_list', kwargs={'salon_id': self.kwargs.get('salon_id')})

class TransactionUpdateView(LoginRequiredMixin, SalonOwnerRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'saloon/generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'Transaction'
        return context

    def get_success_url(self):
        return reverse_lazy('saloon:transaction_list', kwargs={'salon_id': self.kwargs.get('salon_id')})

class TransactionDeleteView(LoginRequiredMixin, SalonOwnerRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Transaction
    template_name = 'saloon/generic_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('saloon:transaction_list', kwargs={'salon_id': self.kwargs.get('salon_id')})

# HairstyleTariffHistory views
class HairstyleTariffHistoryListView(LoginRequiredMixin, SalonOwnerRequiredMixin, OwnerRequiredMixin, ListView):
    model = HairstyleTariffHistory
    template_name = 'saloon/hairstyle_tariff_history_list.html'
    context_object_name = 'tariff_history'

    def get_queryset(self):
        salon_id = self.kwargs.get('salon_id')
        return HairstyleTariffHistory.objects.filter(hairstyle__salon__id=salon_id, hairstyle__salon__owner=self.request.user)

class HairstyleTariffHistoryCreateView(LoginRequiredMixin, SalonOwnerRequiredMixin, CreateView):
    model = HairstyleTariffHistory
    form_class = HairstyleTariffHistoryForm
    template_name = 'saloon/generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'Hairstyle Tariff History'
        return context

    def form_valid(self, form):
        salon = get_object_or_404(Salon, id=self.kwargs.get('salon_id'), owner=self.request.user)
        form.instance.hairstyle.salon = salon
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('saloon:hairstyle_tariff_history_list', kwargs={'salon_id': self.kwargs.get('salon_id')})

class HairstyleTariffHistoryUpdateView(LoginRequiredMixin, SalonOwnerRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = HairstyleTariffHistory
    form_class = HairstyleTariffHistoryForm
    template_name = 'saloon/generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'Hairstyle Tariff History'
        return context

    def get_success_url(self):
        return reverse_lazy('saloon:hairstyle_tariff_history_list', kwargs={'salon_id': self.kwargs.get('salon_id')})

class HairstyleTariffHistoryDeleteView(LoginRequiredMixin, SalonOwnerRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = HairstyleTariffHistory
    template_name = 'saloon/generic_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('saloon:hairstyle_tariff_history_list', kwargs={'salon_id': self.kwargs.get('salon_id')})

