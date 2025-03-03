from django.shortcuts import get_object_or_404, render

from categories.models import Category
from store.models import Product


def product_by_category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category)
    return render(request, 'categories/category.html', {'category': category, 'products': products})

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'categories/category_list.html', {'categories': categories})
