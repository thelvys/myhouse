from django.urls import path
from . import views

app_name = 'saloon'

urlpatterns = [
    # Salon URLs
    path('', views.SalonListView.as_view(), name='salon_list'),
    path('create/', views.SalonCreateView.as_view(), name='salon_create'),
    path('<int:pk>/', views.SalonDetailView.as_view(), name='salon_detail'),
    path('<int:pk>/update/', views.SalonUpdateView.as_view(), name='salon_update'),
    path('<int:pk>/delete/', views.SalonDeleteView.as_view(), name='salon_delete'),

    # Barber URLs
    path('<int:salon_id>/barbers/', views.BarberListView.as_view(), name='barber_list'),
    path('<int:salon_id>/barbers/create/', views.BarberCreateView.as_view(), name='barber_create'),
    path('<int:salon_id>/barbers/<int:pk>/update/', views.BarberUpdateView.as_view(), name='barber_update'),
    path('<int:salon_id>/barbers/<int:pk>/delete/', views.BarberDeleteView.as_view(), name='barber_delete'),

    # Client URLs
    path('<int:salon_id>/clients/', views.ClientListView.as_view(), name='client_list'),
    path('<int:salon_id>/clients/create/', views.ClientCreateView.as_view(), name='client_create'),
    path('<int:salon_id>/clients/<int:pk>/update/', views.ClientUpdateView.as_view(), name='client_update'),
    path('<int:salon_id>/clients/<int:pk>/delete/', views.ClientDeleteView.as_view(), name='client_delete'),

    # Hairstyle URLs
    path('<int:salon_id>/hairstyles/', views.HairstyleListView.as_view(), name='hairstyle_list'),
    path('<int:salon_id>/hairstyles/create/', views.HairstyleCreateView.as_view(), name='hairstyle_create'),
    path('<int:salon_id>/hairstyles/<int:pk>/update/', views.HairstyleUpdateView.as_view(), name='hairstyle_update'),
    path('<int:salon_id>/hairstyles/<int:pk>/delete/', views.HairstyleDeleteView.as_view(), name='hairstyle_delete'),

    # Shave URLs
    path('<int:salon_id>/shaves/', views.ShaveListView.as_view(), name='shave_list'),
    path('<int:salon_id>/shaves/create/', views.ShaveCreateView.as_view(), name='shave_create'),
    path('<int:salon_id>/shaves/<int:pk>/update/', views.ShaveUpdateView.as_view(), name='shave_update'),
    path('<int:salon_id>/shaves/<int:pk>/delete/', views.ShaveDeleteView.as_view(), name='shave_delete'),

    # Item URLs
    path('<int:salon_id>/items/', views.ItemListView.as_view(), name='item_list'),
    path('<int:salon_id>/items/create/', views.ItemCreateView.as_view(), name='item_create'),
    path('<int:salon_id>/items/<int:pk>/update/', views.ItemUpdateView.as_view(), name='item_update'),
    path('<int:salon_id>/items/<int:pk>/delete/', views.ItemDeleteView.as_view(), name='item_delete'),

    # ItemPurchase URLs
    path('<int:salon_id>/purchases/', views.ItemPurchaseListView.as_view(), name='item_purchase_list'),
    path('<int:salon_id>/purchases/create/', views.ItemPurchaseCreateView.as_view(), name='item_purchase_create'),
    path('<int:salon_id>/purchases/<int:pk>/update/', views.ItemPurchaseUpdateView.as_view(), name='item_purchase_update'),
    path('<int:salon_id>/purchases/<int:pk>/delete/', views.ItemPurchaseDeleteView.as_view(), name='item_purchase_delete'),

    # ItemUsed URLs
    path('<int:salon_id>/used/', views.ItemUsedListView.as_view(), name='item_used_list'),
    path('<int:salon_id>/used/create/', views.ItemUsedCreateView.as_view(), name='item_used_create'),
    path('<int:salon_id>/used/<int:pk>/update/', views.ItemUsedUpdateView.as_view(), name='item_used_update'),
    path('<int:salon_id>/used/<int:pk>/delete/', views.ItemUsedDeleteView.as_view(), name='item_used_delete'),

    # Commission URLs
    path('<int:salon_id>/commissions/', views.CommissionListView.as_view(), name='commission_list'),
    path('<int:salon_id>/commissions/create/', views.CommissionCreateView.as_view(), name='commission_create'),
    path('<int:salon_id>/commissions/<int:pk>/update/', views.CommissionUpdateView.as_view(), name='commission_update'),
    path('<int:salon_id>/commissions/<int:pk>/delete/', views.CommissionDeleteView.as_view(), name='commission_delete'),

    # Currency URLs
    path('<int:salon_id>/currencies/', views.CurrencyListView.as_view(), name='currency_list'),
    path('<int:salon_id>/currencies/create/', views.CurrencyCreateView.as_view(), name='currency_create'),
    path('<int:salon_id>/currencies/<int:pk>/update/', views.CurrencyUpdateView.as_view(), name='currency_update'),
    path('<int:salon_id>/currencies/<int:pk>/delete/', views.CurrencyDeleteView.as_view(), name='currency_delete'),

    # CashRegister URLs
    path('<int:salon_id>/cash_registers/', views.CashRegisterListView.as_view(), name='cash_register_list'),
    path('<int:salon_id>/cash_registers/create/', views.CashRegisterCreateView.as_view(), name='cash_register_create'),
    path('<int:salon_id>/cash_registers/<int:pk>/update/', views.CashRegisterUpdateView.as_view(), name='cash_register_update'),
    path('<int:salon_id>/cash_registers/<int:pk>/delete/', views.CashRegisterDeleteView.as_view(), name='cash_register_delete'),

    # PaymentType URLs
    path('<int:salon_id>/payment_types/', views.PaymentTypeListView.as_view(), name='payment_type_list'),
    path('<int:salon_id>/payment_types/create/', views.PaymentTypeCreateView.as_view(), name='payment_type_create'),
    path('<int:salon_id>/payment_types/<int:pk>/update/', views.PaymentTypeUpdateView.as_view(), name='payment_type_update'),
    path('<int:salon_id>/payment_types/<int:pk>/delete/', views.PaymentTypeDeleteView.as_view(), name='payment_type_delete'),

    # Payment URLs
    path('<int:salon_id>/payments/', views.PaymentListView.as_view(), name='payment_list'),
    path('<int:salon_id>/payments/create/', views.PaymentCreateView.as_view(), name='payment_create'),
    path('<int:salon_id>/payments/<int:pk>/update/', views.PaymentUpdateView.as_view(), name='payment_update'),
    path('<int:salon_id>/payments/<int:pk>/delete/', views.PaymentDeleteView.as_view(), name='payment_delete'),

    # Transaction URLs
    path('<int:salon_id>/transactions/', views.TransactionListView.as_view(), name='transaction_list'),
    path('<int:salon_id>/transactions/create/', views.TransactionCreateView.as_view(), name='transaction_create'),
    path('<int:salon_id>/transactions/<int:pk>/update/', views.TransactionUpdateView.as_view(), name='transaction_update'),
    path('<int:salon_id>/transactions/<int:pk>/delete/', views.TransactionDeleteView.as_view(), name='transaction_delete'),

    # HairstyleTariffHistory URLs
    path('<int:salon_id>/hairstyle_tariff_histories/', views.HairstyleTariffHistoryListView.as_view(), name='hairstyle_tariff_history_list'),
    path('<int:salon_id>/hairstyle_tariff_histories/create/', views.HairstyleTariffHistoryCreateView.as_view(), name='hairstyle_tariff_history_create'),
    path('<int:salon_id>/hairstyle_tariff_histories/<int:pk>/update/', views.HairstyleTariffHistoryUpdateView.as_view(), name='hairstyle_tariff_history_update'),
    path('<int:salon_id>/hairstyle_tariff_histories/<int:pk>/delete/', views.HairstyleTariffHistoryDeleteView.as_view(), name='hairstyle_tariff_history_delete'),

# Ajoutez des URLs similaires pour CashRegister, PaymentType, Payment, Transaction, HairstyleTariffHistory, et ItemUsed
]