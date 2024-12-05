from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from ckeditor.fields import RichTextField

from django.utils.text import slugify

class Category(models.Model):
    sub_category = models.ForeignKey('self', on_delete=models.CASCADE, related_name='categories', null=True, blank=True)
    is_sub = models.BooleanField(default=False)
    name = models.CharField(max_length=200, null=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)  # Chúng ta cho phép trường này trống để tự động điền trong save()

    def save(self, *args, **kwargs):
        if not self.slug:  # Nếu slug chưa được tạo
            self.slug = slugify(self.name)  # Tạo slug từ name
        super(Category, self).save(*args, **kwargs)  # Gọi save của lớp cha

    def __str__(self):
        return self.name
# class Category(models.Model):
#     sub_category = models.ForeignKey('self',on_delete = models.CASCADE,related_name = 'categories',null = True,blank = True)
#     is_sub = models.BooleanField(default = False)
#     name = models.CharField(max_length = 200,null = True)
#     slug = models.SlugField(max_length = 200,unique = True)
    

#     def __str__(self):
#         return self.name
    class Meta: 
        verbose_name = "Danh mục sản phẩm"
        verbose_name_plural = "Danh mục sản phẩm"
import re
from django import forms
from django.core.exceptions import ValidationError


def validate_name(value):
    """Validator để kiểm tra tên chỉ chứa chữ cái (có dấu) và khoảng trắng."""
    # Biểu thức chính quy cho phép chữ cái viết hoa, chữ cái thường, ký tự có dấu trong tiếng Việt và khoảng trắng
    if not re.match(r'^[A-Za-zÀ-ÿ\s]+$', value):  # Cho phép chữ cái viết hoa, chữ cái thường và ký tự có dấu
        raise forms.ValidationError('Tên không hợp lệ. Tên chỉ được chứa chữ cái (có dấu) và khoảng trắng.')
def validate_username(value):
    """Validator để kiểm tra Username không chứa khoảng trắng."""
    # Kiểm tra nếu Username có chứa khoảng trắng
    if ' ' in value:
        raise forms.ValidationError('Username không được chứa khoảng trắng.')
    return value
class CreateUserForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Họ'}),
        validators=[validate_name]  # Áp dụng validator cho trường "Tên"
    )    
    last_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Tên'}),
        validators=[validate_name]  # Áp dụng validator cho trường "Tên"
    )     
    username = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Username'}),
        validators=[validate_username]  # Áp dụng validator cho Username
    )    
    email = forms.EmailField(max_length=200, required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    class Meta:
        model = User
        fields = ['username','email','first_name','last_name','password1','password2']
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email đã tồn tại.")
        return email
    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        # Kiểm tra nếu mật khẩu chứa khoảng trắng
        if len(password) < 8:
            raise ValidationError('Mật khẩu phải từ 8 ký tự trở lên.')
        
        # Kiểm tra nếu mật khẩu chứa ít nhất một chữ cái, một số và một ký tự đặc biệt
        if not re.search(r'[A-Za-z]', password):
            raise ValidationError('Mật khẩu phải chứa ít nhất một chữ cái,một chữ số,một ký tự đặc biệt.')
        if not re.search(r'[0-9]', password):
            raise ValidationError('Mật khẩu phải chứa ít nhất một chữ cái,một chữ số,một ký tự đặc biệt.')
        if not re.search(r'[\W_]', password):  # Kiểm tra ký tự đặc biệt
            raise ValidationError('Mật khẩu phải chứa ít nhất một chữ cái,một chữ số,một ký tự đặc biệt.')
        if not re.search(r'[A-Z]', password):  # Kiểm tra chữ cái in hoa
            raise ValidationError('Mật khẩu phải chứa ít nhất một chữ cái in hoa.')
        if ' ' in password:
            raise ValidationError('Mật khẩu không được chứa khoảng trắng.')
        return password

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 != password2:
            raise ValidationError('Mật khẩu và mật khẩu nhập lại không khớp.')
        return password2
class Product(models.Model):
    category = models.ManyToManyField(Category,related_name='product')
    name = models.CharField(max_length=200, null=True)
    origin_price = models.FloatField()
    price = models.FloatField()
    old_price = models.FloatField()
    digital = models.BooleanField(default=False, null=True, blank=False)
    description = RichTextField()
    image = models.ImageField(null=True,blank=True)
    image1 = models.ImageField(null=True, blank=True)
    image2 = models.ImageField(null=True, blank=True)
    image3 = models.ImageField(null=True, blank=True)
    date_added = models.DateField(auto_now_add=True)
    input_quantity =  models.IntegerField(default=0, null=True, blank=False)
    content = RichTextField()
    sale = models.IntegerField(default=0, null=True, blank=False)
    hot = models.BooleanField(default=False, null=True, blank=False)

    def __str__(self):
        return self.name
    # @property 
    # def ImageUrl(self):
    #     try:
    #         url = self.image.url
    #     except:
    #         url = ''
    #     return url
    def get_image_url(self, image_field):
        """Returns the URL of the image field, or an empty string if no image exists."""
        try:
            return getattr(self, image_field).url
        except:
            return ''

    @property
    def ImageUrl(self):
        return self.get_image_url('image')

    @property
    def ImageUrl1(self):
        return self.get_image_url('image1')

    @property
    def ImageUrl2(self):
        return self.get_image_url('image2')

    @property
    def ImageUrl3(self):
        return self.get_image_url('image3')
    class Meta:
        verbose_name = "Sản phẩm"
        verbose_name_plural = "Sản phẩm"

class InputProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(default=0, null=True, blank=False)
    date_added = models.DateField(auto_now_add=True)
class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date_order = models.DateField(auto_now_add=True)
    complete = models.BooleanField(default=False, null=True, blank=False)
    transaction_id = models.CharField(max_length=200, null=True)

    def __str__(self):
        return str(self.id)
    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for  item in orderitems])
        return total
    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        # total = sum([item.get_total or 0 for item in orderitems])
        total = sum([item.get_total for  item in orderitems])
        return total
    class Meta:
        verbose_name = "Đơn hàng"
        verbose_name_plural = "Đơn hàng"
class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(default=0, null=True, blank=False)
    date_added = models.DateField(auto_now_add=True)
    @property
    def get_total(self):
        # if self.product is not None:
        #    total = self.product.price * self.quantity
        # else:
        #    total = 0
        total = self.product.price * self.quantity
        return  total
    class Meta: 
         verbose_name = "Mặt hàng trong đơn"
         verbose_name_plural = "Mặt hàng trong đơn"
class ShippingAddress(models.Model):
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    orderitem = models.ForeignKey(OrderItem, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.CharField(max_length=200, null=True)
    typepayment = models.CharField(max_length=200, null=True)
    phone = models.CharField(max_length=200, null=True)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.address
    class Meta:
        verbose_name = "Địa chỉ giao hàng"
        verbose_name_plural = "Địa chỉ giao hàng"
    # forms.py
class CheckoutForm(forms.Form):
    name = forms.CharField(max_length=200, required=True)
    email = forms.EmailField(max_length=200, required=True)
    address = forms.CharField(max_length=200, required=True)
    phone = forms.CharField(max_length=15, required=True)
    typepayment = forms.ChoiceField(choices=(('1', 'COD'), ('2', 'Chuyển khoản')), required=True)
class Invoice(models.Model):
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    orderitem = models.ForeignKey(OrderItem, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.CharField(max_length=200, null=True)
    typepayment = models.CharField(max_length=200, null=True)
    phone = models.CharField(max_length=200, null=True)

    ORDER_STATUS_CHOICES = [
        ('pending', 'Đang giao hàng'),
        ('paid', 'Đã thanh toán'),
    ]

    state = models.CharField(
        max_length=15,
        choices=ORDER_STATUS_CHOICES,
        default='pending',  # Đặt giá trị mặc định
    )
    
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(default=0, null=True, blank=False)
    date_added = models.DateField(auto_now_add=True)
    product_name = models.CharField(max_length=200, null=True)

    @property
    def get_total(self):
        # if self.product is not None:
        #    total = self.product.price * self.quantity
        # else:
        #    total = 0
        total = self.product.price * self.quantity
        return  total
class PaymentForm(forms.Form):

    order_id = forms.CharField(max_length=250)
    order_type = forms.CharField(max_length=20)
    amount = forms.IntegerField()
    order_desc = forms.CharField(max_length=100)
    bank_code = forms.CharField(max_length=20, required=False)
    language = forms.CharField(max_length=2)
class Payment_VNPay(models.Model):
    id = models.IntegerField(primary_key=True)
    amount = models.FloatField(default = 0.0,null = True,blank = True)
    order_desc = models.CharField(max_length = 200,null = True,blank = True)
    vnp_TransactionNo = models.CharField(max_length = 200,null = True,blank = True)
    vnp_ResponseCode = models.CharField(max_length = 200,null = True,blank = True)
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    orderitem = models.ForeignKey(OrderItem, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.CharField(max_length=200, null=True)
    phone = models.CharField(max_length=200, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    product_name = models.CharField(max_length=200, null=True)
