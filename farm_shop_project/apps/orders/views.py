# apps/orders/views.py
from django.shortcuts import render
from django.views.generic import TemplateView

class CartView(TemplateView):
    template_name = 'orders/cart.html'

class CheckoutView(TemplateView):
    template_name = 'orders/checkout.html'

class OrderHistoryView(TemplateView):
    template_name = 'orders/order_history.html'