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

# Ajoutez des URLs similaires pour CashRegister, PaymentType, Payment, Transaction, HairstyleTariffHistory, et ItemUsed
]