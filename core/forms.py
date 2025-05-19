from django import forms
from .models import ClothesProduct, Customer, Order, OrderItem


class ClothesProductForm(forms.ModelForm):
    class Meta:
        model = ClothesProduct
        fields = ['name', 'description', 'price', 'size', 'color', 'stock_quantity']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer', 'status']


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show products with stock available
        self.fields['product'].queryset = ClothesProduct.objects.filter(stock_quantity__gt=0)


# Form for creating multiple order items at once
class OrderItemFormSet(forms.BaseFormSet):
    def clean(self):
        """
        Validate that at least one order item is provided
        """
        if any(self.errors):
            return

        if not any(form.cleaned_data for form in self.forms):
            raise forms.ValidationError("At least one product must be added to the order.")


# Form for login
class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)
