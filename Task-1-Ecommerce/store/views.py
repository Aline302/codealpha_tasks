from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Product, Order, OrderItem


# =========================================================
# HOME
# =========================================================

def home(request):
    products = Product.objects.all()

    return render(request, "store/home.html", {
        "products": products
    })


# =========================================================
# PRODUCT DETAILS
# =========================================================

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    return render(request, "store/product_detail.html", {
        "product": product
    })


# =========================================================
# CART
# =========================================================

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart = request.session.get("cart", {})
    product_key = str(product.id)

    current_quantity = cart.get(product_key, 0)

    if product.stock <= 0:
        messages.error(
            request,
            f"{product.name} is currently out of stock."
        )
        return redirect("cart")

    if current_quantity >= product.stock:
        messages.warning(
            request,
            f"Only {product.stock} units of {product.name} are available."
        )
        return redirect("cart")

    cart[product_key] = current_quantity + 1

    request.session["cart"] = cart
    request.session.modified = True

    messages.success(
        request,
        f"{product.name} added to your cart."
    )

    return redirect("cart")

def cart(request):
    cart_data = request.session.get("cart", {})

    cart_items = []
    total = 0

    for product_id, quantity in cart_data.items():

        product = get_object_or_404(
            Product,
            id=product_id
        )

        subtotal = product.price * quantity
        total += subtotal

        cart_items.append({
            "product": product,
            "quantity": quantity,
            "subtotal": subtotal
        })

    return render(request, "store/cart.html", {
        "cart_items": cart_items,
        "total": total
    })


def increase_quantity(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart = request.session.get("cart", {})
    product_key = str(product.id)

    if product_key in cart:
        if cart[product_key] < product.stock:
            cart[product_key] += 1

            messages.success(
                request,
                f"{product.name} quantity updated."
            )
        else:
            messages.warning(
                request,
                f"Only {product.stock} units are available."
            )

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("cart")


def decrease_quantity(request, product_id):
    cart = request.session.get("cart", {})

    product_key = str(product_id)

    if product_key in cart:

        cart[product_key] -= 1

        if cart[product_key] <= 0:
            del cart[product_key]

    request.session["cart"] = cart

    return redirect("cart")


def remove_from_cart(request, product_id):
    cart = request.session.get("cart", {})

    product_key = str(product_id)

    if product_key in cart:
        del cart[product_key]

    request.session["cart"] = cart

    return redirect("cart")


# =========================================================
# REGISTER
# =========================================================

def register_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:

            messages.error(
                request,
                "Passwords do not match."
            )

            return redirect("register")


        if User.objects.filter(username=username).exists():

            messages.error(
                request,
                "Username already exists."
            )

            return redirect("register")


        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, user)

        return redirect("home")


    return render(
        request,
        "store/register.html"
    )


# =========================================================
# LOGIN
# =========================================================

def login_view(request):

    if request.method == "POST":

        form = AuthenticationForm(
            request,
            data=request.POST
        )

        if form.is_valid():

            user = form.get_user()

            login(request, user)

            return redirect("home")

    else:

        form = AuthenticationForm()


    return render(request, "store/login.html", {
        "form": form
    })


# =========================================================
# LOGOUT
# =========================================================

def logout_view(request):

    logout(request)

    return redirect("home")


# =========================================================
# CHECKOUT
# =========================================================

@login_required
def checkout(request):
    cart_data = request.session.get("cart", {})

    if not cart_data:
        messages.warning(request, "Your cart is empty.")
        return redirect("cart")

    cart_items = []
    total = 0

    for product_id, quantity in cart_data.items():
        product = get_object_or_404(
            Product,
            id=product_id
        )

        subtotal = product.price * quantity
        total += subtotal

        cart_items.append({
            "product": product,
            "quantity": quantity,
            "subtotal": subtotal
        })

    return render(request, "store/checkout.html", {
        "cart_items": cart_items,
        "total": total
    })


@login_required
@transaction.atomic
def place_order(request):

    if request.method != "POST":
        return redirect("checkout")

    cart_data = request.session.get("cart", {})

    if not cart_data:
        messages.warning(request, "Your cart is empty.")
        return redirect("cart")

    total = 0
    order_items = []

    # Validate every product before creating the order
    for product_id, quantity in cart_data.items():

        product = get_object_or_404(
            Product,
            id=product_id
        )

        if quantity <= 0:
            messages.error(
                request,
                "Invalid product quantity."
            )
            return redirect("cart")

        if quantity > product.stock:
            messages.error(
                request,
                f"Only {product.stock} units of "
                f"{product.name} are available."
            )
            return redirect("cart")

        subtotal = product.price * quantity
        total += subtotal

        order_items.append({
            "product": product,
            "quantity": quantity
        })

    # Create order
    order = Order.objects.create(
        user=request.user,
        total=total,
        status="confirmed"
    )

    # Create order items and update stock
    for item in order_items:

        product = item["product"]
        quantity = item["quantity"]

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=product.price
        )

        product.stock -= quantity
        product.save()

    # Clear cart only after successful processing
    request.session["cart"] = {}
    request.session.modified = True

    return redirect(
        "order_success",
        order_id=order.id
    )



# =========================================================
# ORDER SUCCESS
# =========================================================

@login_required
def order_success(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )


    return render(
        request,
        "store/order_success.html",
        {
            "order": order
        }
    )