# services.py

from decimal import Decimal, ROUND_HALF_UP
from django.db.models import Sum, F, Q, Count, OuterRef, Subquery, Avg
from django.utils import timezone
from datetime import timedelta

from .models import Shave, Barber, CashRegister, Item, ItemUsed, ItemPurchase, Payment, Transaction

class ShaveService:
    @staticmethod
    def get_total_shaves(salon, start_date=None, end_date=None):
        queryset = Shave.objects.filter(salon=salon, status=Shave.Status.COMPLETED)
        if start_date:
            queryset = queryset.filter(date_shave__gte=start_date)
        if end_date:
            queryset = queryset.filter(date_shave__lte=end_date)
        result = queryset.aggregate(
            total_count=Count('id'),
            total_amount=Sum('amount_in_default_currency')
        )
        return {
            'total_count': result['total_count'] or 0,
            'total_amount': result['total_amount'] or Decimal('0.00')
        }

    @staticmethod
    def get_monthly_shaves(salon, year, month):
        start_date = timezone.datetime(year, month, 1)
        end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        return ShaveService.get_total_shaves(salon, start_date, end_date)

class BarberService:
    @staticmethod
    def format_decimal(value):
        return Decimal(value).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @staticmethod
    def calculate_commission(barber, start_date=None, end_date=None):
        shaves = Shave.objects.filter(barber=barber, status=Shave.Status.COMPLETED)
        if start_date:
            shaves = shaves.filter(date_shave__gte=start_date)
        if end_date:
            shaves = shaves.filter(date_shave__lte=end_date)
        
        total_commission = Decimal('0.00')
        for shave in shaves:
            commission = shave.barber.commissions.filter(effective_date__lte=shave.date_shave).order_by('-effective_date').first()
            if commission:
                total_commission += (shave.amount_in_default_currency * commission.percentage / 100) + commission.fixed_amount
        
        return total_commission

    @staticmethod
    def calculate_balance(barber, start_date=None, end_date=None):
        total_commission = BarberService.calculate_commission(barber, start_date, end_date)
        payments = Payment.objects.filter(barber=barber)
        if start_date:
            payments = payments.filter(date_payment__gte=start_date)
        if end_date:
            payments = payments.filter(date_payment__lte=end_date)
        total_paid = payments.aggregate(total=Sum('amount_in_default_currency'))['total'] or Decimal('0.00')
        
        return BarberService.format_decimal(total_commission) - BarberService.format_decimal(total_paid)

class CashRegisterService:
    @staticmethod
    def update_balance(cash_register):
        income = Shave.objects.filter(cashregister=cash_register, status=Shave.Status.COMPLETED).aggregate(total=Sum('amount_in_default_currency'))['total'] or Decimal('0.00')
        income += Transaction.objects.filter(cashregister=cash_register, trans_type=Transaction.TransactionType.INCOME).aggregate(total=Sum('amount_in_default_currency'))['total'] or Decimal('0.00')
        
        profit_expense = Payment.objects.filter(cashregister=cash_register).aggregate(total=Sum('amount_in_default_currency'))['total'] or Decimal('0.00')
        profit_expense += Transaction.objects.filter(cashregister=cash_register, trans_type=Transaction.TransactionType.EXPENSE).aggregate(total=Sum('amount_in_default_currency'))['total'] or Decimal('0.00')
                
        items_used_cost = Decimal('0.00')
        for item_used in ItemUsed.objects.filter(shave__cashregister=cash_register, shave__status=Shave.Status.COMPLETED):
            items_used_cost += item_used.get_amount_in_default_currency()
        
        profit_expense += items_used_cost
        
        cash_register.balance_profit = income - profit_expense
        
        # Calculate expenses for cash balance
        cash_expense = Payment.objects.filter(cashregister=cash_register).aggregate(total=Sum('amount_in_default_currency'))['total'] or Decimal('0.00')
        cash_expense += Transaction.objects.filter(cashregister=cash_register, trans_type=Transaction.TransactionType.EXPENSE).aggregate(total=Sum('amount_in_default_currency'))['total'] or Decimal('0.00')
        cash_expense += ItemPurchase.objects.filter(cashregister=cash_register).aggregate(total=Sum('purchase_price_in_default_currency'))['total'] or Decimal('0.00')

        cash_register.balance_cash = income - cash_expense

        cash_register.save()

    @staticmethod
    def get_balance(cash_register):
        CashRegisterService.update_balance(cash_register)
        return {
            'profit_balance': cash_register.balance_profit or Decimal('0.00'),
            'cash_balance': cash_register.balance_cash or Decimal('0.00')
        }

class InventoryService:
    @staticmethod
    def get_stock_level(salon):
        result = Item.objects.filter(salon=salon).aggregate(
            total_items=Sum('current_stock'),
            total_value=Sum(F('current_stock') * F('price'))
        )
        return {
            'total_items': result['total_items'] or 0,
            'total_value': result['total_value'] or Decimal('0.00')
        }

    @staticmethod
    def get_low_stock_items(salon, threshold=10):
        return Item.objects.filter(salon=salon, current_stock__lt=threshold)

   
class FinancialService:
    @staticmethod
    def format_decimal(value):
        return Decimal(value).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    @staticmethod
    def get_total_revenue(salon, start_date=None, end_date=None):
        shaves = Shave.objects.filter(salon=salon, status=Shave.Status.COMPLETED)

        if start_date:
            shaves = shaves.filter(date_shave__gte=start_date)
        if end_date:
            shaves = shaves.filter(date_shave__lte=end_date)
        
        total_revenue = shaves.aggregate(total=Sum('amount_in_default_currency'))['total'] or Decimal('0.00')

        return FinancialService.format_decimal(total_revenue)
    
    @staticmethod
    def get_total_profit(salon, start_date=None, end_date=None):
        total_revenue = FinancialService.get_total_revenue(salon, start_date, end_date)

        expenses = Payment.objects.filter(salon=salon)
        expense_transactions = Transaction.objects.filter(salon=salon, trans_type=Transaction.TransactionType.EXPENSE)
        items_used = ItemUsed.objects.filter(salon=salon, shave__status=Shave.Status.COMPLETED)

        if start_date:
            expenses = expenses.filter(date_payment__gte=start_date)
            expense_transactions = expense_transactions.filter(date_trans__gte=start_date)
            items_used = items_used.filter(shave__date_shave__gte=start_date)
        if end_date:
            expenses = expenses.filter(date_payment__lte=end_date)
            expense_transactions = expense_transactions.filter(date_trans__lte=end_date)
            items_used = items_used.filter(shave__date_shave__lte=end_date)

        total_expenses = expenses.aggregate(total=Sum('amount_in_default_currency'))['total'] or Decimal('0.00')
        total_expense_transactions = expense_transactions.aggregate(total=Sum('amount_in_default_currency'))['total'] or Decimal('0.00')

        items_used_cost = Decimal('0.00')
        for item_used in items_used:
            items_used_cost += item_used.get_amount_in_default_currency()

        total_expenses += total_expense_transactions + items_used_cost

        return FinancialService.format_decimal(total_revenue - total_expenses)

    @staticmethod
    def get_financial_summary(salon, start_date=None, end_date=None):
        total_revenue = FinancialService.get_total_revenue(salon, start_date, end_date)
        total_profit = FinancialService.get_total_profit(salon, start_date, end_date)

        shaves = Shave.objects.filter(salon=salon, status=Shave.Status.COMPLETED)
        if start_date:
            shaves = shaves.filter(date_shave__gte=start_date)
        if end_date:
            shaves = shaves.filter(date_shave__lte=end_date)
        total_shaves = shaves.count()

        stock_value = InventoryService.get_stock_level(salon)['total_value']

        return {
            'total_revenue': total_revenue,
            'profit': total_profit,
            'total_shaves': total_shaves,
            'stock_value': FinancialService.format_decimal(stock_value)
        }