from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.forms import formset_factory
from django.db.models import Sum
from django.core.paginator import Paginator
from django.contrib import messages
from django.db import transaction

from .models import ClothesProduct, Customer, Order, OrderItem
from .forms import (
    ClothesProductForm, CustomerForm, OrderForm,
    OrderItemForm, OrderItemFormSet, LoginForm
)


# Authentication views
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None and user.is_staff:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Invalid credentials or not authorized')
    else:
        form = LoginForm()
    return render(request, 'core/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


# Home view
@login_required
def home(request):
    # Get featured products (newest 5)
    featured_products = ClothesProduct.objects.order_by('-created_at')[:5]

    # Get recent orders
    recent_orders = Order.objects.order_by('-order_date')[:5]

    # Get customer count
    customer_count = Customer.objects.count()

    # Get total products
    product_count = ClothesProduct.objects.count()

    context = {
        'featured_products': featured_products,
        'recent_orders': recent_orders,
        'customer_count': customer_count,
        'product_count': product_count,
    }
    return render(request, 'core/home.html', context)


# Product views
@login_required
def product_list(request):
    products = ClothesProduct.objects.all().order_by('name')

    # Pagination
    paginator = Paginator(products, 10)  # Show 10 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/products/list.html', {'page_obj': page_obj})


@login_required
def product_detail(request, pk):
    product = get_object_or_404(ClothesProduct, pk=pk)
    return render(request, 'core/products/detail.html', {'product': product})


@login_required
def product_create(request):
    if request.method == 'POST':
        form = ClothesProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product created successfully')
            return redirect('product_list')
    else:
        form = ClothesProductForm()

    return render(request, 'core/products/form.html', {'form': form, 'title': 'Create Product'})


@login_required
def product_update(request, pk):
    product = get_object_or_404(ClothesProduct, pk=pk)

    if request.method == 'POST':
        form = ClothesProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully')
            return redirect('product_detail', pk=product.pk)
    else:
        form = ClothesProductForm(instance=product)

    return render(request, 'core/products/form.html', {'form': form, 'title': 'Update Product'})


# Customer views
@login_required
def customer_list(request):
    customers = Customer.objects.all().order_by('last_name', 'first_name')
    return render(request, 'core/customers/list.html', {'customers': customers})


@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    orders = customer.orders.all().order_by('-order_date')
    return render(request, 'core/customers/detail.html', {'customer': customer, 'orders': orders})


@login_required
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer created successfully')
            return redirect('customer_list')
    else:
        form = CustomerForm()

    return render(request, 'core/customers/form.html', {'form': form, 'title': 'Create Customer'})


@login_required
def customer_update(request, pk):
    customer = get_object_or_404(Customer, pk=pk)

    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer updated successfully')
            return redirect('customer_detail', pk=customer.pk)
    else:
        form = CustomerForm(instance=customer)

    return render(request, 'core/customers/form.html', {'form': form, 'title': 'Update Customer'})


# Order views
@login_required
def order_list(request):
    orders = Order.objects.all().order_by('-order_date')
    return render(request, 'core/orders/list.html', {'orders': orders})


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    items = order.items.all()
    return render(request, 'core/orders/detail.html', {'order': order, 'items': items})


@login_required
def order_create(request):
    OrderItemFormSetFactory = formset_factory(OrderItemForm, formset=OrderItemFormSet, extra=1)

    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        item_formset = OrderItemFormSetFactory(request.POST, prefix='items')

        if order_form.is_valid() and item_formset.is_valid():
            with transaction.atomic():
                # Create order
                order = order_form.save(commit=False)

                # Calculate total amount
                total_amount = 0
                for form in item_formset:
                    if form.cleaned_data:
                        product = form.cleaned_data['product']
                        quantity = form.cleaned_data['quantity']
                        total_amount += product.price * quantity

                order.total_amount = total_amount
                order.save()

                # Create order items
                for form in item_formset:
                    if form.cleaned_data:
                        product = form.cleaned_data['product']
                        quantity = form.cleaned_data['quantity']

                        # Create order item
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=quantity,
                            price=product.price
                        )

                        # Update product stock
                        product.stock_quantity -= quantity
                        product.save()

                messages.success(request, 'Order created successfully')
                return redirect('order_detail', pk=order.pk)
    else:
        order_form = OrderForm()
        item_formset = OrderItemFormSetFactory(prefix='items')

    context = {
        'order_form': order_form,
        'item_formset': item_formset,
        'title': 'Create Order'
    }
    return render(request, 'core/orders/form.html', context)


@login_required
def order_update_status(request, pk):
    order = get_object_or_404(Order, pk=pk)

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, 'Order status updated successfully')
            return redirect('order_detail', pk=order.pk)
    else:
        form = OrderForm(instance=order)

    return render(request, 'core/orders/status_form.html', {'form': form, 'order': order})