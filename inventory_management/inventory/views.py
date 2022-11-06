from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from .forms import InventoryItemForm, UserRegisterForm
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic, View
from .models import InventoryItem, Category
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from inventory_management.settings import LOW_QUANTITY

class Index(TemplateView):
    template_name = 'inventory/index.html'

class SignUpView(generic.View):
    def get(self, request):
        form = UserRegisterForm()
        return render(request, 'inventory/signup.html', {'form':form})
    def post(self, request):
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')

class Dashboard(LoginRequiredMixin, generic.View):
    def get(self, request):
        items = InventoryItem.objects.filter(user=self.request.user.id).order_by('id')

        low_inventory = InventoryItem.objects.filter(
            user=self.request.user.id,
            quantity__lte=LOW_QUANTITY
        )

        if low_inventory.count() > 0:
            # print(low_inventory.count())
            if low_inventory.count() > 1:
                messages.error(request, f'{low_inventory.count()} items have low inventory')
            else:
                messages.error(request, f'{low_inventory.count()} item has low inventory')

        low_inventory_ids = InventoryItem.objects.filter(
            user=self.request.user.id,
            quantity__lte=LOW_QUANTITY
        ).values_list('id', flat=True)

        return render(request, 'inventory/dashboard.html', {'items': items, 'low_inventory_ids': low_inventory_ids})

class AddItem(LoginRequiredMixin, generic.CreateView):
    model = InventoryItem
    form_class = InventoryItemForm
    template_name = 'inventory/item_form.html'
    success_url = reverse_lazy('dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class EditItem(LoginRequiredMixin, generic.UpdateView):
    model = InventoryItem
    form_class = InventoryItemForm
    template_name = 'inventory/item_form.html'
    success_url = reverse_lazy('dashboard')

class DeleteItem(LoginRequiredMixin, generic.DeleteView):
    model = InventoryItem
    template_name = 'inventory/delete_item.html'
    success_url = reverse_lazy('dashboard')
    context_object_name = 'item'
