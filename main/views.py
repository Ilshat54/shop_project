from django.shortcuts import render
from django.http import Http404
from .models import User, Product, Category, Order, OrderItem
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse
# Create your views here.
def index(request):
    return render(request, 'main/index.html')
def about(request):
    return render(request, 'main/about.html')
# главная страница с категориями
def index(request):
    categories = Category.objects.all()
    return render(request, 'main/index.html', {"categories": categories})

# страница конкретной категории с товарами
def category_view(request, category_id):
    category = get_object_or_404(Category, category_id=category_id)
    products = Product.objects.filter(category=category)
    return render(request, 'main/category.html', {"category": category, "products": products})

# страница конкретного товара (детали)
def product_view(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    return render(request, 'main/product.html', {"product": product})

# регистрация
def register_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")

        # проверка что email не занят
        if User.objects.filter(email=email).exists():
            messages.error(request, "Этот email уже зарегистрирован")
            return redirect("register")

        # создание нового пользователя
        user = User(name=name, email=email, password=make_password(password))
        user.save()

        messages.success(request, "Регистрация успешна! Теперь войдите.")
        return redirect("login")

    return render(request, "main/register.html")


# вход
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = User.objects.get(email=email)
            if check_password(password, user.password):  #  проверка хеша
                request.session["user_id"] = user.user_id
                request.session["is_admin"] = user.is_admin
                request.session["user_name"] = user.name
                messages.success(request, f"Добро пожаловать, {user.name}!")
                return redirect("index")
            else:
                messages.error(request, "Неверный логин или пароль")
                return redirect("login")
        except User.DoesNotExist:
            messages.error(request, "Неверный логин или пароль")
            return redirect("login")

    return render(request, "main/login.html")


# выход
def logout_view(request):
    request.session.flush()
    messages.info(request, "Вы вышли из системы")
    return redirect("index")


# личный кабинет
def profile_view(request):
    if "user_id" not in request.session:
        messages.warning(request, "Сначала войдите в систему")
        return redirect("login")

    user_name = request.session.get("user_name")
    return render(request, "main/profile.html", {"user_name": user_name})

# Добавить в корзину (с проверкой входа)
def add_to_cart(request, product_id):
    if not request.session.get("user_id"):
        messages.warning(request, "Для начала войдите в систему или зарегистрируйтесь.")
        return redirect(request.META.get("HTTP_REFERER", "/login/"))

    product = get_object_or_404(Product, pk=product_id)
    cart = request.session.get('cart', {})

    pid = str(product_id)
    if pid in cart:
        cart[pid]['quantity'] += 1
    else:
        cart[pid] = {
            'product_id': product_id,
            'name': product.name,
            'price': float(product.price),
            'quantity': 1,
            'image': product.image or ''
        }

    request.session['cart'] = cart
    request.session.modified = True
    messages.success(request, "Товар добавлен в корзину!")
    return redirect('cart')

# Просмотр корзины
def cart_view(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0.0

    for pid, item in cart.items():
        subtotal = item['price'] * item['quantity']
        total += subtotal
        cart_items.append({
            'product_id': pid,
            'name': item['name'],
            'price': item['price'],
            'quantity': item['quantity'],
            'image': item.get('image', ''),
            'subtotal': subtotal,
        })

    return render(request, 'main/cart.html', {
        'cart_items': cart_items,
        'total': total,
    })

# Обновить количество
def update_cart(request, product_id):
    if request.method == "POST":
        cart = request.session.get('cart', {})
        quantity = int(request.POST.get('quantity', 1))
        pid = str(product_id)
        if pid in cart:
            if quantity <= 0:
                del cart[pid]
            else:
                cart[pid]['quantity'] = quantity
        request.session['cart'] = cart
        request.session.modified = True
    return redirect('cart')

# Удалить из корзины
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    pid = str(product_id)
    if pid in cart:
        del cart[pid]
        request.session['cart'] = cart
        request.session.modified = True
        messages.info(request, "Товар удалён из корзины.")
    return redirect('cart')

# Оформить заказ (с адресом и временем)
def checkout(request):
    if not request.session.get("user_id"):
        messages.warning(request, "Для оформления заказа войдите в систему.")
        return redirect(request.META.get("HTTP_REFERER", "/login/"))

    cart = request.session.get('cart', {})
    if not cart:
        messages.warning(request, "Корзина пуста.")
        return redirect('cart')

    if request.method == "POST":
        address = request.POST.get('address')
        delivery_time = request.POST.get('delivery_time')
        user_id = request.session.get("user_id")

        # Создаём заказ в таблице orders
        order = Order.objects.create(
            user_id=user_id,
            order_date=timezone.now(),
            status="Новый",
            address=address,
            delivery_time=delivery_time
        )

        # Добавляем товары в order_items
        for pid, item in cart.items():
            OrderItem.objects.create(
                order=order,
                product_id=int(pid),
                quantity=item['quantity'],
                price=item['price']
            )

        # очищаем корзину
        request.session['cart'] = {}
        request.session.modified = True
        messages.success(request, "Заказ успешно оформлен!")
        return redirect('orders_list')  # перенаправляем к списку заказов

    total = sum(item['price'] * item['quantity'] for item in cart.values())
    return render(request, 'main/checkout.html', {
        'cart': cart,
        'total': total,
    })

# Мои заказы (текущие, которые еще выполняются)
def orders_list(request):
    if not request.session.get("user_id"):
        messages.warning(request, "Сначала войдите в систему.")
        return redirect("login")

    orders = Order.objects.filter(
        user_id=request.session["user_id"],
        status__in=["В обработке", "Новый", "Ожидает оплаты"]
    ).order_by("-order_date")

    return render(request, "main/orders_list.html", {"orders": orders})


# История заказов (уже завершённые или отменённые)
def orders_history(request):
    if not request.session.get("user_id"):
        messages.warning(request, "Сначала войдите в систему.")
        return redirect("login")

    orders = Order.objects.filter(
        user_id=request.session["user_id"]
    ).exclude(
        status__in=["В обработке", "Новый", "Ожидает оплаты"]
    ).order_by("-order_date")

    return render(request, "main/orders_history.html", {"orders": orders})

#  Админ-панель
def admin_panel(request):
    if not request.session.get("is_admin"):
        messages.error(request, "Доступ запрещён. Только для администратора.")
        return redirect("index")

    users = User.objects.all().order_by("user_id")
    products = Product.objects.all().order_by("product_id")
    orders = Order.objects.all().order_by("-order_date")
    categories = Category.objects.all().order_by("name")

    return render(request, "main/admin_panel.html", {
        "users": users,
        "products": products,
        "orders": orders,
        "categories": categories
    })
#  Удаление пользователя
def delete_user(request, user_id):
    if not request.session.get("is_admin"):
        return redirect("index")
    user = get_object_or_404(User, pk=user_id)
    user.delete()
    messages.success(request, "Пользователь удалён.")
    return redirect("admin_panel")

#  Удаление товара
def delete_product(request, product_id):
    if not request.session.get("is_admin"):
        return redirect("index")
    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    messages.success(request, "Товар удалён.")
    return redirect("admin_panel")

#  Изменение статуса заказа
def change_order_status(request, order_id):
    if not request.session.get("is_admin"):
        return redirect("index")

    order = get_object_or_404(Order, pk=order_id)
    new_status = request.GET.get("status")
    if new_status:
        order.status = new_status
        order.save()
        messages.success(request, f"Статус заказа №{order_id} изменён на '{new_status}'.")
    return redirect("/admin-panel/?tab=orders")

def add_product(request):
    if not request.session.get("is_admin"):
        return redirect("index")

    if request.method == "POST":
        name = request.POST.get("name")
        price = request.POST.get("price")
        category_id = request.POST.get("category")
        description = request.POST.get("description")
        image = request.POST.get("image")

        if name and price and category_id:
            Product.objects.create(
                name=name,
                price=price,
                category_id=category_id,
                description=description,
                image=image
            )
            messages.success(request, "Товар успешно добавлен.")
        else:
            messages.error(request, "Заполните все обязательные поля.")
        return redirect("/admin-panel/?tab=products")

    return redirect("/admin-panel/?tab=products")

def edit_product(request, product_id):
    if not request.session.get("is_admin"):
        return redirect("index")

    product = get_object_or_404(Product, pk=product_id)

    if request.method == "POST":
        product.name = request.POST.get("name")
        product.price = request.POST.get("price")
        product.category_id = request.POST.get("category")
        product.description = request.POST.get("description")
        product.image = request.POST.get("image")
        product.save()
        messages.success(request, f"Товар «{product.name}» успешно обновлён.")
        return redirect("/admin-panel/?tab=products")

    categories = Category.objects.all()
    return render(request, "main/edit_product.html", {"product": product, "categories": categories})

def search(request):
    query = request.GET.get("q", "").strip()
    results = []
    categories = []

    if query:
        # Ищем совпадения в товарах и категориях
        products = Product.objects.filter(name__icontains=query)
        categories = Category.objects.filter(name__icontains=query)

        if not products.exists() and not categories.exists():
            messages.info(request, "Ничего не найдено.")
        else:
            results = products

    return render(request, "main/search_results.html", {
        "query": query,
        "products": results,
        "categories": categories,
    })

def search_suggestions(request):
    query = request.GET.get("q", "").strip()
    suggestions = []

    if query:
        products = Product.objects.filter(name__icontains=query)[:5]
        categories = Category.objects.filter(name__icontains=query)[:5]

        for p in products:
            suggestions.append({
                "name": p.name,
                "url": f"/product/{p.product_id}/",
                "type": "Товар"
            })
        for c in categories:
            suggestions.append({
                "name": c.name,
                "url": f"/category/{c.id}/",
                "type": "Категория"
            })

    return JsonResponse({"suggestions": suggestions})