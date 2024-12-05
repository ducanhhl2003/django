### PAYment
import hashlib
import hmac
import json
import urllib
import urllib.parse
import urllib.request
import random
import requests
from datetime import datetime
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from urllib.parse import quote
from app.models import PaymentForm
from app.vnpay import vnpay
from django.views.decorators.csrf import csrf_exempt
##Payment
from django.shortcuts import render,redirect,get_object_or_404
import json
# Create your views here.
from django.http import HttpResponse,JsonResponse
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.db.models import Sum, Count, F

from django.db.models import Sum, F

def order_statistics(request):
    # Tổng số đơn hàng
    total_orders = Order.objects.count()

    # Tổng doanh thu từ tất cả đơn hàng
    total_revenue = OrderItem.objects.annotate(
        product_price=F('product__price')  # Truy cập giá từ Product thông qua ForeignKey
    ).aggregate(total=Sum(F('product_price') * F('quantity')))['total']

    # Số lượng sản phẩm đã bán
    total_quantity = OrderItem.objects.aggregate(total_quantity=Sum('quantity'))['total_quantity']

    # Doanh thu theo từng sản phẩm
    revenue_by_product = OrderItem.objects.values('product__name').annotate(
        total_quantity_sold=Sum('quantity'),
        total_revenue=Sum(F('product__price') * F('quantity'))  # Sửa cú pháp truy cập giá
    )

    context = {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_quantity': total_quantity,
        'revenue_by_product': revenue_by_product
    }

    return render(request, 'app/order_statistics.html', context)

def profile(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        full_name = f"{first_name} {last_name}"
        user = request.user
        customer = request.user
        order,created = Order.objects.get_or_create(customer = customer,complete = False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        user_not_login = "hidden"
        user_login = "show"
    else:
        items = []
        order={'get_cart_items':0,'get_cart_total':0}
        cartItems = order['get_cart_items']
        user_not_login = "show"
        user_login = "hidden"
    context = {'user':user,'full_name': full_name,'cartItems':cartItems,'user_not_login':user_not_login,'user_login':user_login,'items':items}
    return render(request,'app/profile.html',context)
# def detail(request):
#     if request.user.is_authenticated:
#         customer = request.user
#         # Lấy đơn hàng chưa hoàn tất của khách hàng
#         order, created = Order.objects.get_or_create(customer=customer, complete=False)
#         items = order.orderitem_set.all()
#         cartItems = order.get_cart_items
#         user_not_login = "hidden"
#         user_login = "show"
#     else:
#         items = []
#         order = {'get_cart_items': 0, 'get_cart_total': 0}
#         cartItems = order['get_cart_items']
#         user_not_login = "show"
#         user_login = "hidden"

#     # Lấy id sản phẩm từ query string
#     product_id = request.GET.get('id', '')
#     if not product_id:
#         return render(request, 'app/404.html')  # Nếu không có id sản phẩm, trả về trang lỗi

#     # Lấy sản phẩm với id đã cho
#     products = Product.objects.filter(id=product_id)
#     if not products.exists():
#         return render(request, 'app/404.html')  # Nếu sản phẩm không tồn tại, trả về trang lỗi

#     # Lấy các danh mục sản phẩm
#     categories = Category.objects.filter(is_sub=False)
#     category_slug = request.GET.get('category')
#     if category_slug:
#         products = products.filter(category__slug=category_slug)
#     # Tính số lượng tồn kho và số lượng đã thanh toán cho sản phẩm
#     for product in products:
#         # Lấy số lượng sản phẩm còn trong kho từ InputProduct
#         input_product = InputProduct.objects.filter(product=product).first()
#         quantity_in_stock = input_product.quantity if input_product else 0

#         # Tính tổng số lượng đã thanh toán (state = 'paid') từ Invoice
#         paid_quantity = Invoice.objects.filter(product=product, state='paid').aggregate(total_paid_quantity=Sum('quantity'))['total_paid_quantity'] or 0

#         # Cập nhật số lượng tồn kho thực tế sau khi trừ số lượng đã thanh toán
#         product.quantity_in_stock = quantity_in_stock - paid_quantity

#     context = {
#         'items': items,
#         'categories': categories,
#         'products': products,
#         'cartItems': cartItems,
#         'user_not_login': user_not_login,
#         'user_login': user_login,
#     }

#     return render(request, 'app/detail.html', context)
def detail(request):
    # Kiểm tra người dùng đã đăng nhập hay chưa
    if request.user.is_authenticated:
        customer = request.user
        # Lấy đơn hàng chưa hoàn tất của khách hàng
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        user_not_login = "hidden"
        user_login = "show"
    else:
        items = []
        order = {'get_cart_items': 0, 'get_cart_total': 0}
        cartItems = order['get_cart_items']
        user_not_login = "show"
        user_login = "hidden"

    active_category = request.GET.get('category', '')
    productcategory = Product.objects.all()  # Bắt đầu với tất cả sản phẩm

    if active_category:
        productcategory = productcategory.filter(category__slug=active_category)

    # Lấy id sản phẩm từ query string
    product_id = request.GET.get('id', '')
    if not product_id:
        return render(request, 'app/404.html')  # Nếu không có id sản phẩm, trả về trang lỗi

    # Lấy sản phẩm duy nhất từ id
    product = get_object_or_404(Product, id=product_id)

    # Lấy các danh mục mà sản phẩm thuộc về (nếu có nhiều danh mục)
    categories = product.category.all()

    # Lọc các sản phẩm có cùng category, loại trừ sản phẩm hiện tại
    products_in_same_category = Product.objects.filter(category__in=categories).exclude(id=product_id)

    # Lấy các danh mục sản phẩm (chỉ lấy danh mục cấp 1)
    categories = Category.objects.filter(is_sub=False)
    
    # Tính số lượng tồn kho và số lượng đã thanh toán cho sản phẩm
    for p in [product] + list(products_in_same_category):  # Lặp qua sản phẩm hiện tại và các sản phẩm cùng category
        # Lấy số lượng sản phẩm còn trong kho từ InputProduct
        input_product = InputProduct.objects.filter(product=p).first()
        quantity_in_stock = input_product.quantity if input_product else 0

        # Tính tổng số lượng đã thanh toán (state = 'paid') từ Invoice
        paid_quantity = Invoice.objects.filter(product=p, state='paid').aggregate(total_paid_quantity=Sum('quantity'))['total_paid_quantity'] or 0

        # Cập nhật số lượng tồn kho thực tế sau khi trừ số lượng đã thanh toán
        p.quantity_in_stock = quantity_in_stock - paid_quantity
    
    total_quantity = Invoice.objects.filter(product=product, state='paid').aggregate(total_paid_quantity=Sum('quantity'))['total_paid_quantity'] or 0
    context = {
        'items': items,
        'categories': categories,
        'product': product,  # Thêm sản phẩm chi tiết vào context (đối tượng duy nhất)
        'products_in_same_category': products_in_same_category,  # Các sản phẩm cùng category
        'cartItems': cartItems,
        'user_not_login': user_not_login,
        'user_login': user_login,
        'total_quantity': total_quantity
    }

    return render(request, 'app/detail.html', context)

def category(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_items': 0, 'get_cart_total': 0}
        cartItems = order['get_cart_items']

    categories = Category.objects.filter(is_sub=False)
    active_category = request.GET.get('category', '')
    category_slug = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    # Lấy danh sách sản phẩm theo category_slug
    products = Product.objects.all()  # Bắt đầu với tất cả sản phẩm
    if category_slug:
        products = products.filter(category__slug=category_slug)

    # Lọc theo giá
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    # Lọc theo active_category nếu có
    if active_category:
        products = products.filter(category__slug=active_category)

    # Sắp xếp sản phẩm
    orderby = request.GET.get('orderby', 'menu_order')
    if orderby == 'date':
        products = products.order_by('-date_added')  # Điều chỉnh theo mô hình của bạn
    elif orderby == 'price':
        products = products.order_by('price')
    elif orderby == 'price-desc':
        products = products.order_by('-price')
    else:
        products = products.order_by('id')  # Sắp xếp mặc định\
    # Tính số lượng tồn kho và số lượng đã thanh toán cho sản phẩm
    for product in products:
        # Lấy số lượng sản phẩm còn trong kho từ InputProduct
        input_product = InputProduct.objects.filter(product=product).first()
        quantity_in_stock = input_product.quantity if input_product else 0

        # Tính tổng số lượng đã thanh toán (state = 'paid') từ Invoice
        paid_quantity = Invoice.objects.filter(product=product, state='paid').aggregate(total_paid_quantity=Sum('quantity'))['total_paid_quantity'] or 0

        # Cập nhật số lượng tồn kho thực tế sau khi trừ số lượng đã thanh toán
        product.quantity_in_stock = quantity_in_stock - paid_quantity
    context = {
        'min_price': min_price,
        'max_price': max_price,
        'items': items,
        'cartItems': cartItems,
        'categories': categories,
        'active_category': active_category,
        'products': products
    }
    return render(request, 'app/category.html', context)

def search(request):
    searched = request.POST['searched']
    keys = Product.objects.filter(name__contains = searched)
    categories = Category.objects.filter(is_sub = False)
    # Tính số lượng tồn kho và số lượng đã thanh toán cho sản phẩm
    for product in keys:
        # Lấy số lượng sản phẩm còn trong kho từ InputProduct
        input_product = InputProduct.objects.filter(product=product).first()
        quantity_in_stock = input_product.quantity if input_product else 0

        # Tính tổng số lượng đã thanh toán (state = 'paid') từ Invoice
        paid_quantity = Invoice.objects.filter(product=product, state='paid').aggregate(total_paid_quantity=Sum('quantity'))['total_paid_quantity'] or 0

        # Cập nhật số lượng tồn kho thực tế sau khi trừ số lượng đã thanh toán
        product.quantity_in_stock = quantity_in_stock - paid_quantity
    if request.user.is_authenticated:
        customer = request.user
        order,created = Order.objects.get_or_create(customer = customer,complete = False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        user_not_login = "hidden"
        user_login = "show"
    else:
        items = []
        order={'get_cart_items':0,'get_cart_total':0}
        cartItems = order['get_cart_items']
        user_not_login = "show"
        user_login = "hidden"
    return render(request,'app/search.html',{'searched':searched,'keys':keys,'categories':categories,'cartItems' : cartItems,'user_not_login':user_not_login,'user_login':user_login})  

def register(request):
    form = CreateUserForm()  # Khởi tạo form trống

    if request.method == "POST":
        form = CreateUserForm(request.POST)  # Khởi tạo form với dữ liệu POST
        if form.is_valid():  # Kiểm tra xem form có hợp lệ không
            form.save()  # Lưu dữ liệu vào cơ sở dữ liệu
            return redirect('home')  # Chuyển hướng đến trang chủ nếu thành công
        else:
            # Nếu form không hợp lệ, giữ lại form và hiển thị lỗi
            return render(request, 'app/register.html', {'form': form})
    
    # Nếu là GET request, trả về form trống
    return render(request, 'app/register.html', {'form': form})
from django.utils import timezone  # Thêm import này để sử dụng timezone
from datetime import timedelta
def loginPage(request):
    # Kiểm tra nếu người dùng đã đăng nhập
    if request.user.is_authenticated:
        return redirect('home')
    
    # Kiểm tra xem người dùng đã thử đăng nhập quá số lần cho phép chưa
    failed_attempts = request.session.get('failed_attempts', 0)  # Lấy số lần đăng nhập thất bại từ session
    last_failed_time_str = request.session.get('last_failed_time', None)  # Lấy thời gian lần đăng nhập thất bại cuối cùng (dưới dạng chuỗi)

    # Chuyển đổi last_failed_time_str thành datetime nếu có
    last_failed_time = None
    if last_failed_time_str:
        last_failed_time = timezone.datetime.fromisoformat(last_failed_time_str)

    # Kiểm tra xem có cần chờ không
    if failed_attempts >= 3:
        # Nếu đã đạt 3 lần đăng nhập sai, kiểm tra thời gian chờ
        if last_failed_time:
            time_diff = timezone.now() - last_failed_time
            if time_diff < timedelta(minutes=2):
                # Nếu chưa đủ 2 phút, thông báo cho người dùng và yêu cầu chờ
                remaining_time = timedelta(minutes=2) - time_diff
                minutes = remaining_time.seconds // 60
                messages.error(request, f"Bạn đăng nhập sai quá số lần, xin vui lòng chờ {minutes}:00 để đăng nhập lại.")
                return render(request, 'app/login.html')  # Hiển thị lại trang đăng nhập
            else:
                # Nếu đã đủ 2 phút, reset lại số lần đăng nhập sai
                request.session['failed_attempts'] = 0
                request.session['last_failed_time'] = None
    
    if request.method == "POST":
        username = request.POST.get('username')  # Lấy tên đăng nhập từ POST
        password = request.POST.get('password')  # Lấy mật khẩu từ POST

        # Kiểm tra nếu tên đăng nhập bị trống hoặc chỉ chứa khoảng trắng
        if not username or username.strip() == '':
            messages.error(request, 'Tài khoản hoặc mật khẩu không hợp lệ!')
        elif not password or password.strip() == '':
            messages.error(request, 'Bạn vui lòng nhập vào Password hợp lệ.')
        else:
            # Kiểm tra nếu tên đăng nhập có tồn tại trong hệ thống
            user = User.objects.filter(username=username).first()
            
            if user is None:
                # Nếu tên đăng nhập không tồn tại
                messages.error(request, 'Username không tồn tại. Bạn vui lòng đăng ký để đăng nhập.')
            else:
                # Tiến hành xác thực người dùng nếu tên đăng nhập tồn tại
                user = authenticate(request, username=username, password=password)
                
                if user is not None:
                    login(request, user)  # Đăng nhập người dùng
                    # Reset số lần đăng nhập thất bại khi đăng nhập thành công
                    request.session['failed_attempts'] = 0
                    request.session['last_failed_time'] = None
                    return redirect('home')
                else:
                    # Nếu mật khẩu không khớp
                    messages.error(request, 'Password không đúng. Bạn vui lòng nhập lại.')
                    
                    # Tăng số lần đăng nhập thất bại
                    request.session['failed_attempts'] = failed_attempts + 1
                    request.session['last_failed_time'] = timezone.now().isoformat()  # Lưu thời gian dưới dạng chuỗi ISO
    
    context = {}
    return render(request, 'app/login.html', context)
def logoutPage(request):
    logout(request)
    return redirect('login')
def home(request):
    if request.user.is_superuser:
        admin_login = "show"
    else:
        admin_login ="hidden"
    categories = Category.objects.all()[:3]
    categorized_products = {category.name: Product.objects.filter(category=category)[:10] for category in categories}
    # Lặp qua các danh mục
    for category in categories:
        products = Product.objects.filter(category=category)
        
        for product in products:
            # Lấy số lượng sản phẩm còn trong kho từ InputProduct
            input_product = InputProduct.objects.filter(product=product).first()
            if input_product:
                quantity_in_stock = input_product.quantity
            else:
                quantity_in_stock = 0

            # Tính tổng số lượng đã thanh toán (state = 'paid') từ Invoice
            paid_quantity = Invoice.objects.filter(product=product, state='paid').aggregate(total_paid_quantity=Sum('quantity'))['total_paid_quantity'] or 0

            # Cập nhật thuộc tính quantity_in_stock cho sản phẩm
            product.quantity_in_stock = quantity_in_stock - paid_quantity  # Số lượng tồn kho = số lượng nhập vào - số lượng đã thanh toán
            
        categorized_products[category.name] = products
    if request.user.is_authenticated:
        customer = request.user
        order,created = Order.objects.get_or_create(customer = customer,complete = False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        user_not_login = "hidden"
        user_login = "show"
    else:
        items = []
        order={'get_cart_items':0,'get_cart_total':0}
        cartItems = order['get_cart_items']
        user_not_login = "show"
        user_login = "hidden"
    
        
    # products = Product.objects.all()[:4]
    products = Product.objects.all()
    categories = Category.objects.filter(is_sub = False)
    
    context = {'admin_login':admin_login,'items':items,'categorized_products': categorized_products,'categories':categories,'products':products,'cartItems' : cartItems,'user_not_login':user_not_login,'user_login':user_login}
    return render(request,'app/home.html',context)
def cart(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer = customer,complete = False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        user_not_login = "hidden"
        user_login = "show"
    else:
        items = []
        order={'get_cart_items':0,'get_cart_total':0}
        cartItems = order['get_cart_items']
        user_not_login = "show"
        user_login = "hidden"
    context = {'items':items,'order':order,'cartItems' : cartItems,'user_not_login':user_not_login,'user_login':user_login}
    return render(request, 'app/cart.html', context)

# def checkout(request):
#     if request.user.is_authenticated:
#         customer = request.user
#         order, created = Order.objects.get_or_create(customer = customer,complete = False)
#         items = order.orderitem_set.all()
#     else:
#         items = []
#         order={'get_cart_items':0,'get_cart_total':0}
#     context = {'items':items,'order':order}
#     return render(request,'app/checkout.html',context)
def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    customer = request.user
    product = Product.objects.get(id = productId)
    order, created = Order.objects.get_or_create(customer = customer,complete = False)
    orderItem, created = OrderItem.objects.get_or_create(order = order,product = product)
    if action =='add':
        orderItem.quantity += 1
    elif action == 'remove':
        orderItem.quantity -=1
    orderItem.save()
    if orderItem.quantity <=  0:
        orderItem.delete()
    
    return JsonResponse('added',safe=False)
def checkout(request):
    form = CheckoutForm()
    order = None
    items = []
    cart_total = 0

    # Lấy thông tin giỏ hàng khi người dùng đã đăng nhập
    if request.user.is_authenticated:
        try:
            order = Order.objects.get(customer=request.user, complete=False)
            items = order.orderitem_set.all()
            cart_total = order.get_cart_total
            cartItems = order.get_cart_items
            user_not_login = "hidden"
            user_login = "show"
        except Order.DoesNotExist:
            # Xử lý khi không tìm thấy đơn hàng
            order = None
            cartItems = order['get_cart_items']
            user_not_login = "show"
            user_login = "hidden"

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Tạo khách hàng dựa trên trạng thái đăng nhập
            customer = request.user if request.user.is_authenticated else None

            # Đảm bảo rằng `order` không phải là `None` trước khi sử dụng
            if order is None:
                # Nếu `order` là `None`, có thể tạo mới hoặc xử lý lỗi
                return HttpResponse("Order not found", status=404)

            # Lưu thông tin giao hàng
            shipping_address = ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=form.cleaned_data['address'],
                phone=form.cleaned_data['phone'],
                typepayment=form.cleaned_data['typepayment']
            )
            if form.cleaned_data['typepayment'] == '2':
                return redirect('index')

            # Tạo Invoice cho từng sản phẩm trong giỏ hàng
            for item in items:
                Invoice.objects.create(
                    customer=customer,
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    product_name=item.product.name,  # Lưu tên sản phẩm vào invoice
                    address=form.cleaned_data['address'],
                    phone=form.cleaned_data['phone'],
                    typepayment=form.cleaned_data['typepayment'],
                )
                order.orderitem_set.all().delete()  # Xóa tất cả OrderItems
            
            # Nếu cần, bạn cũng có thể đánh dấu đơn hàng là hoàn tất
                # order.complete = True
                # order.save()
            # Điều hướng đến trang xác nhận thanh toán (hoặc trang cảm ơn)
            return redirect('checkoutsuccess')

    context = {'form': form, 'items': items, 'order': order, 'cart_total': cart_total,'cartItems' : cartItems,'user_not_login':user_not_login,'user_login':user_login}
    return render(request, 'app/checkout.html', context)
def checkoutsuccess(request):
    return render(request,'app/checkoutsuccess.html')




### PAYment


def index(request):
    return render(request, "payment/index.html", {"title": "Danh sách demo"})


def hmacsha512(key, data):
    byteKey = key.encode('utf-8')
    byteData = data.encode('utf-8')
    return hmac.new(byteKey, byteData, hashlib.sha512).hexdigest()


def payment(request):

    if request.method == 'POST':
        # Process input data and build url payment
        form = PaymentForm(request.POST)
        if form.is_valid():
            order_type = form.cleaned_data['order_type']
            order_id = form.cleaned_data['order_id']
            amount = form.cleaned_data['amount']
            order_desc = form.cleaned_data['order_desc']
            bank_code = form.cleaned_data['bank_code']
            language = form.cleaned_data['language']
            ipaddr = get_client_ip(request)
            # Build URL Payment
            vnp = vnpay()
            vnp.requestData['vnp_Version'] = '2.1.0'
            vnp.requestData['vnp_Command'] = 'pay'
            vnp.requestData['vnp_TmnCode'] = settings.VNPAY_TMN_CODE
            vnp.requestData['vnp_Amount'] = amount * 100
            vnp.requestData['vnp_CurrCode'] = 'VND'
            vnp.requestData['vnp_TxnRef'] = order_id
            vnp.requestData['vnp_OrderInfo'] = order_desc
            vnp.requestData['vnp_OrderType'] = order_type
            # Check language, default: vn
            if language and language != '':
                vnp.requestData['vnp_Locale'] = language
            else:
                vnp.requestData['vnp_Locale'] = 'vn'
                # Check bank_code, if bank_code is empty, customer will be selected bank on VNPAY
            if bank_code and bank_code != "":
                vnp.requestData['vnp_BankCode'] = bank_code

            vnp.requestData['vnp_CreateDate'] = datetime.now().strftime('%Y%m%d%H%M%S')  # 20150410063022
            vnp.requestData['vnp_IpAddr'] = ipaddr
            vnp.requestData['vnp_ReturnUrl'] = settings.VNPAY_RETURN_URL
            vnpay_payment_url = vnp.get_payment_url(settings.VNPAY_PAYMENT_URL, settings.VNPAY_HASH_SECRET_KEY)
            print(vnpay_payment_url)
            return redirect(vnpay_payment_url)
        else:
            print("Form input not validate")
    else:
        return render(request, "payment/payment.html", {"title": "Thanh toán"})


def payment_ipn(request):
    inputData = request.GET
    if inputData:
        vnp = vnpay()
        vnp.responseData = inputData.dict()
        order_id = inputData['vnp_TxnRef']
        amount = inputData['vnp_Amount']
        order_desc = inputData['vnp_OrderInfo']
        vnp_TransactionNo = inputData['vnp_TransactionNo']
        vnp_ResponseCode = inputData['vnp_ResponseCode']
        vnp_TmnCode = inputData['vnp_TmnCode']
        vnp_PayDate = inputData['vnp_PayDate']
        vnp_BankCode = inputData['vnp_BankCode']
        vnp_CardType = inputData['vnp_CardType']

        
        if vnp.validate_response(settings.VNPAY_HASH_SECRET_KEY):
            # Check & Update Order Status in your Database
            # Your code here
            firstTimeUpdate = True
            totalamount = True
            if totalamount:
                if firstTimeUpdate:
                    if vnp_ResponseCode == '00':
                        print('Payment Success. Your code implement here')
                    else:
                        print('Payment Error. Your code implement here')

                    # Return VNPAY: Merchant update success
                    result = JsonResponse({'RspCode': '00', 'Message': 'Confirm Success'})
                else:
                    # Already Update
                    result = JsonResponse({'RspCode': '02', 'Message': 'Order Already Update'})
            else:
                # invalid amount
                result = JsonResponse({'RspCode': '04', 'Message': 'invalid amount'})
        else:
            # Invalid Signature
            result = JsonResponse({'RspCode': '97', 'Message': 'Invalid Signature'})
    else:
        result = JsonResponse({'RspCode': '99', 'Message': 'Invalid request'})

    return result

def payment_return(request):
    inputData = request.GET
    if inputData:
        vnp = vnpay()
        vnp.responseData = inputData.dict()
        order_id = inputData['vnp_TxnRef']
        amount = int(inputData['vnp_Amount']) / 100
        order_desc = inputData['vnp_OrderInfo']
        vnp_TransactionNo = inputData['vnp_TransactionNo']
        vnp_ResponseCode = inputData['vnp_ResponseCode']
        vnp_TmnCode = inputData['vnp_TmnCode']
        vnp_PayDate = inputData['vnp_PayDate']
        vnp_BankCode = inputData['vnp_BankCode']
        vnp_CardType = inputData['vnp_CardType']
        payment = Payment_VNPay.objects.create(
            order_id =order_id,
            amount = amount,
            order_desc = order_desc,
            vnp_TransactionNo = vnp_TransactionNo,
            vnp_ResponseCode = vnp_ResponseCode
        )
        if vnp.validate_response(settings.VNPAY_HASH_SECRET_KEY):
            if vnp_ResponseCode == "00":
                return render(request, "payment/payment_return.html", {"title": "Kết quả thanh toán",
                                                               "result": "Thành công", "order_id": order_id,
                                                               "amount": amount,
                                                               "order_desc": order_desc,
                                                               "vnp_TransactionNo": vnp_TransactionNo,
                                                               "vnp_ResponseCode": vnp_ResponseCode})
            else:
                return render(request, "payment/payment_return.html", {"title": "Kết quả thanh toán",
                                                               "result": "Lỗi", "order_id": order_id,
                                                               "amount": amount,
                                                               "order_desc": order_desc,
                                                               "vnp_TransactionNo": vnp_TransactionNo,
                                                               "vnp_ResponseCode": vnp_ResponseCode})
        else:
            return render(request, "payment/payment_return.html",
                          {"title": "Kết quả thanh toán", "result": "Lỗi", "order_id": order_id, "amount": amount,
                           "order_desc": order_desc, "vnp_TransactionNo": vnp_TransactionNo,
                           "vnp_ResponseCode": vnp_ResponseCode, "msg": "Sai checksum"})
    else:
        return render(request, "payment/payment_return.html", {"title": "Kết quả thanh toán", "result": ""})


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

n = random.randint(10**11, 10**12 - 1)
n_str = str(n)
while len(n_str) < 12:
    n_str = '0' + n_str


def query(request):
    if request.method == 'GET':
        return render(request, "payment/query.html", {"title": "Kiểm tra kết quả giao dịch"})

    url = settings.VNPAY_API_URL
    secret_key = settings.VNPAY_HASH_SECRET_KEY
    vnp_TmnCode = settings.VNPAY_TMN_CODE
    vnp_Version = '2.1.0'

    vnp_RequestId = n_str
    vnp_Command = 'querydr'
    vnp_TxnRef = request.POST['order_id']
    vnp_OrderInfo = 'kiem tra gd'
    vnp_TransactionDate = request.POST['trans_date']
    vnp_CreateDate = datetime.now().strftime('%Y%m%d%H%M%S')
    vnp_IpAddr = get_client_ip(request)

    hash_data = "|".join([
        vnp_RequestId, vnp_Version, vnp_Command, vnp_TmnCode,
        vnp_TxnRef, vnp_TransactionDate, vnp_CreateDate,
        vnp_IpAddr, vnp_OrderInfo
    ])

    secure_hash = hmac.new(secret_key.encode(), hash_data.encode(), hashlib.sha512).hexdigest()

    data = {
        "vnp_RequestId": vnp_RequestId,
        "vnp_TmnCode": vnp_TmnCode,
        "vnp_Command": vnp_Command,
        "vnp_TxnRef": vnp_TxnRef,
        "vnp_OrderInfo": vnp_OrderInfo,
        "vnp_TransactionDate": vnp_TransactionDate,
        "vnp_CreateDate": vnp_CreateDate,
        "vnp_IpAddr": vnp_IpAddr,
        "vnp_Version": vnp_Version,
        "vnp_SecureHash": secure_hash
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        response_json = json.loads(response.text)
    else:
        response_json = {"error": f"Request failed with status code: {response.status_code}"}

    return render(request, "payment/query.html", {"title": "Kiểm tra kết quả giao dịch", "response_json": response_json})

def refund(request):
    if request.method == 'GET':
        return render(request, "payment/refund.html", {"title": "Hoàn tiền giao dịch"})

    url = settings.VNPAY_API_URL
    secret_key = settings.VNPAY_HASH_SECRET_KEY
    vnp_TmnCode = settings.VNPAY_TMN_CODE
    vnp_RequestId = n_str
    vnp_Version = '2.1.0'
    vnp_Command = 'refund'
    vnp_TransactionType = request.POST['TransactionType']
    vnp_TxnRef = request.POST['order_id']
    vnp_Amount = request.POST['amount']
    vnp_OrderInfo = request.POST['order_desc']
    vnp_TransactionNo = '0'
    vnp_TransactionDate = request.POST['trans_date']
    vnp_CreateDate = datetime.now().strftime('%Y%m%d%H%M%S')
    vnp_CreateBy = 'user01'
    vnp_IpAddr = get_client_ip(request)

    hash_data = "|".join([
        vnp_RequestId, vnp_Version, vnp_Command, vnp_TmnCode, vnp_TransactionType, vnp_TxnRef,
        vnp_Amount, vnp_TransactionNo, vnp_TransactionDate, vnp_CreateBy, vnp_CreateDate,
        vnp_IpAddr, vnp_OrderInfo
    ])

    secure_hash = hmac.new(secret_key.encode(), hash_data.encode(), hashlib.sha512).hexdigest()

    data = {
        "vnp_RequestId": vnp_RequestId,
        "vnp_TmnCode": vnp_TmnCode,
        "vnp_Command": vnp_Command,
        "vnp_TxnRef": vnp_TxnRef,
        "vnp_Amount": vnp_Amount,
        "vnp_OrderInfo": vnp_OrderInfo,
        "vnp_TransactionDate": vnp_TransactionDate,
        "vnp_CreateDate": vnp_CreateDate,
        "vnp_IpAddr": vnp_IpAddr,
        "vnp_TransactionType": vnp_TransactionType,
        "vnp_TransactionNo": vnp_TransactionNo,
        "vnp_CreateBy": vnp_CreateBy,
        "vnp_Version": vnp_Version,
        "vnp_SecureHash": secure_hash
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        response_json = json.loads(response.text)
    else:
        response_json = {"error": f"Request failed with status code: {response.status_code}"}

    return render(request, "payment/refund.html", {"title": "Kết quả hoàn tiền giao dịch", "response_json": response_json})



from django.shortcuts import render
from django.db.models import Sum, F
from django.db.models.functions import TruncMonth
from django.http import HttpResponseForbidden
from django.contrib import messages
from .models import Invoice

def revenue_report(request):
    if not request.user.is_superuser:
        messages.error(request, "Bạn không có quyền truy cập trang này.")
        return HttpResponseForbidden()

    # Lọc theo tháng nếu có
    search_month = request.GET.get('search_month')
    if search_month:
        try:
            year, month = map(int, search_month.split('-'))
            paid_invoices = Invoice.objects.filter(state='paid', date_added__year=year, date_added__month=month)
        except ValueError:
            messages.error(request, "Thông tin tháng không hợp lệ.")
            paid_invoices = Invoice.objects.filter(state='paid')
    else:
        paid_invoices = Invoice.objects.filter(state='paid')
    # Thống kê tổng hợp
    total_profit = paid_invoices.aggregate(total=Sum(F('quantity') * (F('product__price') - F('product__origin_price'))))['total'] or 0
    total_orders = paid_invoices.count()
    total_quantity = paid_invoices.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
    total_revenue = paid_invoices.aggregate(total=Sum(F('quantity') * F('product__price')))['total'] or 0
    # Lợi nhuận và số lượng theo sản phẩm
    profit_by_product = paid_invoices.values('product__name').annotate(
        total_quantity_sold=Sum('quantity'),
        total_profit=Sum(F('quantity') * (F('product__price') - F('product__origin_price')))
    )
    # Doanh thu và số lượng theo sản phẩm
    revenue_by_product = paid_invoices.values('product__name').annotate(
        total_quantity_sold=Sum('quantity'),
        total_revenue=Sum(F('quantity') * F('product__price'))
    )
    # Chuẩn bị dữ liệu cho biểu đồ
    product_names = [item['product__name'] for item in profit_by_product]
    product_profits = [item['total_profit'] for item in profit_by_product]

    context = {
        'total_profit': total_profit,
        'total_orders': total_orders,
        'total_quantity': total_quantity,
        'profit_by_product': profit_by_product,
        'total_profit_from_products': sum(item['total_profit'] for item in profit_by_product),
        'total_revenue_from_products': sum(item['total_revenue'] for item in revenue_by_product),
        'search_month': search_month,
        'product_names': product_names,
        'product_profits': product_profits,
        'total_revenue': total_revenue,
        'revenue_by_product':revenue_by_product
    }

    return render(request, 'admin/changelist.html', context)

def quantity(request):
    if not request.user.is_superuser:
        messages.error(request, "Bạn không có quyền truy cập trang này.")
        return HttpResponseForbidden()

    # Lọc theo tháng nếu có
    search_month = request.GET.get('search_month')
    if search_month:
        try:
            year, month = map(int, search_month.split('-'))
            paid_invoices = Invoice.objects.filter(state='paid', date_added__year=year, date_added__month=month)
        except ValueError:
            messages.error(request, "Thông tin tháng không hợp lệ.")
            paid_invoices = Invoice.objects.filter(state='paid')
    else:
        paid_invoices = Invoice.objects.filter(state='paid')

    # Thống kê tổng hợp
    total_revenue = paid_invoices.aggregate(total=Sum(F('quantity') * F('product__price')))['total'] or 0
    total_orders = paid_invoices.count()
    total_quantity = paid_invoices.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0

    # Doanh thu và số lượng theo sản phẩm
    revenue_by_product = paid_invoices.values('product__name').annotate(
        total_quantity_sold=Sum('quantity'),
        total_revenue=Sum(F('quantity') * F('product__price'))
    )
    top_3_sold_products = sorted(revenue_by_product, key=lambda x: x['total_quantity_sold'], reverse=True)[:3]
    bottom_3_sold_products = sorted(revenue_by_product, key=lambda x: x['total_quantity_sold'])[:3]
    if revenue_by_product.exists():
        most_sold_product = max(revenue_by_product, key=lambda x: x['total_quantity_sold'])
        least_sold_product = min(revenue_by_product, key=lambda x: x['total_quantity_sold'])
    else:
        most_sold_product = least_sold_product = None

    

    # Chuẩn bị dữ liệu cho biểu đồ
    product_names = [item['product__name'] for item in revenue_by_product]
    product_revenues = [item['total_revenue'] for item in revenue_by_product]
    product_quantity = [item['total_quantity_sold'] for item in revenue_by_product]

    context = {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'total_quantity': total_quantity,
        'revenue_by_product': revenue_by_product,
        'total_revenue_from_products': sum(item['total_revenue'] for item in revenue_by_product),
        'search_month': search_month,
        'product_names': product_names,
        'product_revenues': product_revenues,
        'product_quantity' : product_quantity,
        'most_sold_product' : most_sold_product,
        'least_sold_product':least_sold_product,
        'top_3_sold_products':top_3_sold_products,
        'bottom_3_sold_products':bottom_3_sold_products
    }

    return render(request, 'admin/quantity.html', context)
# View để xử lý trang thống kê doanh thu
def revenue_report_month(request):
    # Giới hạn quyền truy cập chỉ cho admin
    if not request.user.is_superuser:
        return HttpResponseForbidden("Bạn không có quyền truy cập trang này.")

    # Tính tổng doanh thu và số đơn hàng
    total_revenue = Invoice.objects.filter(state='paid').aggregate(total=Sum(F('quantity') * F('product__price')))['total'] or 0
    total_orders = Invoice.objects.filter(state='paid').count()
    total_quantity = Invoice.objects.filter(state='paid').aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0

    # Doanh thu và số lượng bán theo sản phẩm
    revenue_by_product = Invoice.objects.filter(state='paid').values('product__name').annotate(
        total_quantity_sold=Sum('quantity'),
        total_revenue=Sum(F('quantity') * F('product__price'))
    )
    total_revenue_from_products = sum(item['total_revenue'] for item in revenue_by_product)

    # Doanh thu theo tháng
    revenue_by_month = Invoice.objects.filter(state='paid').annotate(
        month=TruncMonth('date_added')
    ).values('month').annotate(
        total_revenue=Sum(F('quantity') * F('product__price'))
    ).order_by('month')

    # Xử lý tìm kiếm theo tháng
    search_month = request.GET.get('search_month')
    if search_month:
        year, month = map(int, search_month.split('-'))
        revenue_by_month = revenue_by_month.filter(month__year=year, month__month=month)

    # Chuẩn bị dữ liệu cho biểu đồ
    months = [item['month'].strftime("%Y-%m") for item in revenue_by_month]
    revenues = [item['total_revenue'] for item in revenue_by_month]

    context = {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'total_quantity': total_quantity,
        'revenue_by_product': revenue_by_product,
        'total_revenue_from_products': total_revenue_from_products,
        'search_month': search_month,
        'months': months,
        'revenues': revenues,
    }

    # Render template với context đã tính toán
    return render(request, 'admin/doanhthuthang.html', context)

def gioi_thieu(request):
    categories = Category.objects.all()
    categories = Category.objects.filter(is_sub = False)
    if request.user.is_authenticated:
        user = request.user
        customer = request.user
        order,created = Order.objects.get_or_create(customer = customer,complete = False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        user_not_login = "hidden"
        user_login = "show"
    else:
        items = []
        order={'get_cart_items':0,'get_cart_total':0}
        cartItems = order['get_cart_items']
        user_not_login = "show"
        user_login = "hidden"
    context = {'categories':categories,'cartItems':cartItems,'user_not_login':user_not_login,'user_login':user_login,'items':items}
    return render(request,'app/gioithieu.html',context)
def contact(request):
    categories = Category.objects.all()
    categories = Category.objects.filter(is_sub = False)
    if request.user.is_authenticated:
        user = request.user
        customer = request.user
        order,created = Order.objects.get_or_create(customer = customer,complete = False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        user_not_login = "hidden"
        user_login = "show"
    else:
        items = []
        order={'get_cart_items':0,'get_cart_total':0}
        cartItems = order['get_cart_items']
        user_not_login = "show"
        user_login = "hidden"
    context = {'categories':categories,'cartItems':cartItems,'user_not_login':user_not_login,'user_login':user_login,'items':items}
    return render(request,'app/contact.html',context)
def kho(request):
    # Kiểm tra quyền admin
    if not request.user.is_superuser:
        messages.error(request, "Bạn không có quyền truy cập trang này.")
        return HttpResponseForbidden()

    # Lọc theo tháng nếu có
    search_month = request.GET.get('search_month')
    if search_month:
        try:
            year, month = map(int, search_month.split('-'))
        except ValueError:
            messages.error(request, "Thông tin tháng không hợp lệ.")
            year, month = None, None
    else:
        year, month = None, None

    # Lấy tất cả các sản phẩm và tính toán số lượng nhập và tồn kho
    products = Product.objects.all()
    product_data = []
    stock_quantities = []  # Dữ liệu tồn kho cho biểu đồ
    product_names = []  # Dữ liệu tên sản phẩm cho biểu đồ

    for product in products:
        # Lọc số lượng nhập vào từ InputProduct trong tháng đã chọn
        input_product_query = InputProduct.objects.filter(product=product)
        if year and month:
            input_product_query = input_product_query.filter(date_added__year=year, date_added__month=month)
        total_quantity_in = input_product_query.aggregate(total_in=Sum('quantity'))['total_in'] or 0

        # Lọc số lượng đã bán (state='paid') từ Invoice trong tháng đã chọn
        invoice_query = Invoice.objects.filter(product=product, state='paid')
        if year and month:
            invoice_query = invoice_query.filter(date_added__year=year, date_added__month=month)
        total_sold_quantity = invoice_query.aggregate(total_sold=Sum('quantity'))['total_sold'] or 0

        # Tính số lượng tồn kho trong tháng
        stock_quantity = total_quantity_in - total_sold_quantity
        if stock_quantity < 0:
            stock_quantity = 0

        # Thêm thông tin sản phẩm vào danh sách
        product_data.append({
            'product': product,
            'total_quantity_in': total_quantity_in,
            'total_sold_quantity': total_sold_quantity,
            'stock_quantity': stock_quantity
        })

        # Chuẩn bị dữ liệu cho biểu đồ
        product_names.append(product.name)
        stock_quantities.append(stock_quantity)

    context = {
        'product_data': product_data,  # Dữ liệu sản phẩm
        'search_month': search_month,  # Tháng đã tìm kiếm
        'product_names': product_names,  # Danh sách tên sản phẩm
        'stock_quantities': stock_quantities,  # Danh sách số lượng tồn kho của sản phẩm
    }

    return render(request, 'admin/kho.html', context)