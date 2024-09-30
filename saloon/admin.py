from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from .models import (
    Salon, BarberType, Barber, Client, Commission, Currency, CashRegister,
    PaymentType, Payment, Transaction, Hairstyle, HairstyleTariffHistory,
    Shave, Item, ItemUsed, ItemPurchase
)
from .services import (
    ShaveService, BarberService, CashRegisterService, InventoryService, FinancialService
)

class SalonAdminMixin:
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'salon' in form.base_fields:
            qs = Salon.objects.filter(owner=request.user)
            form.base_fields['salon'].queryset = qs
            if not obj:  # Création d'un nouvel objet
                form.base_fields['salon'].initial = qs.first()
            form.base_fields['salon'].widget.attrs['readonly'] = True
            form.base_fields['salon'].required = False
        return form

    def save_model(self, request, obj, form, change):
        if hasattr(obj, 'salon_id') and not obj.salon_id:  # Création d'un nouvel objet avec champ salon
            obj.salon = Salon.objects.filter(owner=request.user).first()
        elif hasattr(obj, 'barber') and hasattr(obj.barber, 'salon'):  # Pour Commission
            obj.barber.salon = Salon.objects.filter(owner=request.user).first()
        elif hasattr(obj, 'hairstyle') and hasattr(obj.hairstyle, 'salon'):  # Pour HairstyleTariffHistory
            obj.hairstyle.salon = Salon.objects.filter(owner=request.user).first()
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if hasattr(qs.model, 'salon'):
            return qs.filter(salon__owner=request.user)
        elif hasattr(qs.model, 'barber'):  # Pour Commission
            return qs.filter(barber__salon__owner=request.user)
        elif hasattr(qs.model, 'hairstyle'):  # Pour HairstyleTariffHistory
            return qs.filter(hairstyle__salon__owner=request.user)
        return qs  # Fallback si aucune relation n'est trouvée
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "salon":
            kwargs["queryset"] = Salon.objects.filter(owner=request.user)
        elif db_field.name == "barber":
            kwargs["queryset"] = Barber.objects.filter(salon__owner=request.user)
        elif db_field.name == "hairstyle":
            kwargs["queryset"] = Hairstyle.objects.filter(salon__owner=request.user)
        elif db_field.name == "currency":
            kwargs["queryset"] = Currency.objects.filter(salon__owner=request.user)
        elif db_field.name == "cashregister":
            kwargs["queryset"] = CashRegister.objects.filter(salon__owner=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class AutoCalculateDefaultCurrencyMixin:
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        return list(readonly_fields) + ['amount_in_default_currency']
    
    def save_model(self, request, obj, form, change):
        if hasattr(obj, 'amount') and hasattr(obj, 'exchange_rate'):
            obj.amount_in_default_currency = obj.amount * obj.exchange_rate
        elif hasattr(obj, 'price') and hasattr(obj, 'exchange_rate'):
            obj.amount_in_default_currency = obj.price * obj.exchange_rate
        super().save_model(request, obj, form, change)

@admin.register(Salon)
class SalonAdmin(ModelAdmin):
    list_display = ('name', 'owner', 'is_active', 'total_revenue', 'total_profit')
    list_filter = ('is_active',)
    search_fields = ('name', 'owner__email')
    readonly_fields = ('owner',)

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj is None:  # Création d'un nouveau salon
            return (
                (None, {'fields': ('name', 'description', 'address', 'phone', 'email', 'is_active')}),
            )
        else:  # Modification d'un salon existant
            return (
                (None, {'fields': ('name', 'description', 'address', 'phone', 'email', 'is_active', 'owner')}),
            )

    def save_model(self, request, obj, form, change):
        if not change:  # Création d'un nouveau salon
            obj.owner = request.user
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Modification d'un salon existant
            return self.readonly_fields + ('owner',)
        return self.readonly_fields

    def total_revenue(self, obj):
        return FinancialService.get_financial_summary(obj)['total_revenue']
    total_revenue.short_description = _("Total Revenue")

    def total_profit(self, obj):
        return FinancialService.get_financial_summary(obj)['profit']
    total_profit.short_description = _("Total Profit")

@admin.register(BarberType)
class BarberTypeAdmin(SalonAdminMixin, ModelAdmin):
    list_display = ('name', 'salon')
    list_filter = ('salon',)
    search_fields = ('name', 'salon__name')

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Modification d'un type de barbe existant
            return self.readonly_fields + ('salon',)
        return self.readonly_fields
    
    def save_model(self, request, obj, form, change):
        if not change:  # Création d'un nouveau type de barbe
            obj.salon = Salon.objects.filter(owner=request.user).first()
        super().save_model(request, obj, form, change)

@admin.register(Barber)
class BarberAdmin(SalonAdminMixin, ModelAdmin):
    list_display = ('get_full_name', 'salon', 'barber_type', 'is_active', 'commission_balance')
    list_filter = ('salon', 'is_active', 'barber_type')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    list_select_related = ('user', 'salon', 'barber_type')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj:  # Création d'un nouveau barbe
            form.base_fields['salon'].initial = Salon.objects.filter(owner=request.user).first()
        return form

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "salon":
            kwargs["queryset"] = Salon.objects.filter(owner=request.user)
        elif db_field.name == "barber_type":
            if request.user.is_superuser:
                pass  # Don't filter the queryset
            else:
                salon = Salon.objects.filter(owner=request.user).first()
                if salon:
                    kwargs["queryset"] = BarberType.objects.filter(salon=salon)
                else:
                    kwargs["queryset"] = BarberType.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def save_model(self, request, obj, form, change):
        if not obj.salon:
            obj.salon = Salon.objects.filter(owner=request.user).first()
        super().save_model(request, obj, form, change)

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = _("Full Name")

    def commission_balance(self, obj):
        return BarberService.calculate_balance(obj)
    commission_balance.short_description = _("Commission Balance")

@admin.register(Client)
class ClientAdmin(SalonAdminMixin, ModelAdmin):
    list_display = ('name', 'salon', 'phone', 'address')
    list_filter = ('salon',)
    search_fields = ('name', 'phone', 'salon__name', 'address')

@admin.register(Commission)
class CommissionAdmin(SalonAdminMixin, ModelAdmin):
    list_display = ('barber', 'get_salon', 'percentage', 'fixed_amount', 'effective_date')
    list_filter = ('barber__salon', 'effective_date')
    search_fields = ('barber__user__email', 'barber__salon__name')
    list_select_related = ('barber', 'barber__salon')

    def get_salon(self, obj):
        return obj.barber.salon
    get_salon.short_description = _("Salon")
    get_salon.admin_order_field = 'barber__salon'

    def get_queryset(self, request):
        return super().get_queryset(request)

@admin.register(Currency)
class CurrencyAdmin(SalonAdminMixin, ModelAdmin):
    list_display = ('code', 'name', 'salon', 'is_default')
    list_filter = ('salon', 'is_default')
    search_fields = ('code', 'name', 'salon__name')

@admin.register(CashRegister)
class CashRegisterAdmin(SalonAdminMixin, ModelAdmin):
    list_display = ('name', 'salon', 'balance_profit', 'balance_cash')
    list_filter = ('salon',)
    search_fields = ('name', 'salon__name')
    readonly_fields = ('balance_profit', 'balance_cash')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        for cash_register in queryset:
            CashRegisterService.update_balance(cash_register)
        return queryset

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        CashRegisterService.update_balance(obj)

@admin.register(PaymentType)
class PaymentTypeAdmin(SalonAdminMixin, ModelAdmin):
    list_display = ('name', 'salon', 'is_active')
    list_filter = ('salon', 'is_active')
    search_fields = ('name', 'salon__name')

@admin.register(Payment)
class PaymentAdmin(SalonAdminMixin, AutoCalculateDefaultCurrencyMixin, ModelAdmin):
    list_display = ('barber', 'amount', 'currency', 'payment_type', 'date_payment', 'amount_in_default_currency')
    list_filter = ('salon', 'payment_type', 'currency', 'date_payment')
    search_fields = ('barber__user__email', 'salon__name')
    list_select_related = ('barber', 'currency', 'payment_type', 'salon')

@admin.register(Transaction)
class TransactionAdmin(SalonAdminMixin, AutoCalculateDefaultCurrencyMixin, ModelAdmin):
    list_display = ('trans_name', 'amount', 'currency', 'trans_type', 'date_trans', 'amount_in_default_currency')
    list_filter = ('salon', 'trans_type', 'currency', 'date_trans')
    search_fields = ('trans_name', 'salon__name')
    list_select_related = ('currency', 'salon')

@admin.register(Hairstyle)
class HairstyleAdmin(SalonAdminMixin, ModelAdmin):
    list_display = ('name', 'salon', 'current_tariff', 'currency')
    list_filter = ('salon', 'currency')
    search_fields = ('name', 'salon__name')
    list_select_related = ('salon', 'currency')

@admin.register(HairstyleTariffHistory)
class HairstyleTariffHistoryAdmin(SalonAdminMixin, ModelAdmin):
    list_display = ('hairstyle', 'tariff', 'effective_date')
    list_filter = ('hairstyle__salon', 'effective_date')
    search_fields = ('hairstyle__name', 'hairstyle__salon__name')
    list_select_related = ('hairstyle', 'hairstyle__salon')

    def get_salon(self, obj):
        return obj.hairstyle.salon
    get_salon.short_description = _("Salon")
    get_salon.admin_order_field = 'hairstyle__salon'
    
    def get_queryset(self, request):
        return super().get_queryset(request)

class ItemUsedInline(admin.TabularInline):
    model = ItemUsed
    extra = 1

@admin.register(Shave)
class ShaveAdmin(SalonAdminMixin, AutoCalculateDefaultCurrencyMixin, ModelAdmin):
    list_display = ('barber', 'hairstyle', 'amount', 'currency', 'status', 'date_shave', 'amount_in_default_currency')
    list_filter = ('salon', 'status', 'currency', 'date_shave')
    search_fields = ('barber__user__email', 'hairstyle__name', 'salon__name')
    list_select_related = ('barber', 'hairstyle', 'currency', 'salon')
    inlines = [ItemUsedInline]

    actions = ['mark_as_completed']

    @admin.action(description=_("Mark selected shaves as completed"))
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status=Shave.Status.COMPLETED)
        self.message_user(request, _(f"{updated} shaves were successfully marked as completed."))

@admin.register(Item)
class ItemAdmin(SalonAdminMixin, AutoCalculateDefaultCurrencyMixin, ModelAdmin):
    list_display = ('name', 'salon', 'price', 'currency', 'current_stock', 'amount_in_default_currency')
    list_filter = ('salon', 'currency')
    search_fields = ('name', 'salon__name')
    list_select_related = ('salon', 'currency')

@admin.register(ItemUsed)
class ItemUsedAdmin(SalonAdminMixin, ModelAdmin):
    list_display = ('item', 'shave', 'barber', 'quantity', 'get_amount_in_default_currency')
    list_filter = ('salon', 'item')
    search_fields = ('item__name', 'shave__barber__user__email', 'salon__name')
    list_select_related = ('item', 'shave', 'barber', 'salon')

    def get_amount_in_default_currency(self, obj):
        return obj.get_amount_in_default_currency()
    get_amount_in_default_currency.short_description = _("Amount in default currency")

@admin.register(ItemPurchase)
class ItemPurchaseAdmin(SalonAdminMixin, ModelAdmin):
    list_display = ('item', 'quantity', 'purchase_price', 'currency', 'purchase_date', 'purchase_price_in_default_currency')
    list_filter = ('salon', 'currency', 'item', 'purchase_date')
    search_fields = ('item__name', 'salon__name', 'supplier')
    list_select_related = ('item', 'currency', 'salon')

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        return list(readonly_fields) + ['total_purchase_price', 'purchase_price_in_default_currency']

    def save_model(self, request, obj, form, change):
        if not change:
            obj.total_purchase_price = obj.purchase_price * obj.quantity
            obj.purchase_price_in_default_currency = obj.total_purchase_price * obj.exchange_rate
        super().save_model(request, obj, form, change)