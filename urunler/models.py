from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class Product(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE,verbose_name="Satıcı")
    name = models.CharField(max_length=100,verbose_name="Ürün İsmi")
    content = models.TextField(verbose_name="Ürün Açıklaması")
    price= models.IntegerField(verbose_name="Ürün Fiyatı")
    image = models.ImageField( upload_to="product/", verbose_name="Ürün Resmi")
    slug = models.SlugField(blank=True)
    stock = models.IntegerField(default=0,null=True,verbose_name="Ürün Stok Durumu")
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name.replace('ı','i'))
        super(Product,self).save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Ürünler"
        verbose_name = "Ürün"
        

        
class ShopCard(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE,verbose_name="Ekleyen")
    product = models.ForeignKey(Product, on_delete=models.CASCADE,verbose_name="Eklenen Ürün")
    count = models.IntegerField(verbose_name="Adet")
    totalPrice = models.IntegerField(verbose_name="Toplam Fiyat",editable=False)
    isPayment = models.BooleanField(default=False,verbose_name="Ödendi mi?")
    created_at = models.DateTimeField( auto_now_add=True)


    def __str__(self):
        return self.product.name

    class Meta:
        verbose_name_plural = "Sepetteki Ürünler"
        verbose_name = "Sepet"
        
    def save(self,*args, **kwargs):
        self.totalPrice = self.product.price * self.count    
        super(ShopCard,self).save(*args, **kwargs)
        
class Payment(models.Model):
    owner = models.ForeignKey(User, verbose_name=("Satın Alan"), on_delete=models.CASCADE)
    products = models.ManyToManyField(ShopCard, verbose_name=("Satın Alınan Ürünler"))
    totalPrice = models.IntegerField(verbose_name="Toplam Fiyat")
    isPayment = models.BooleanField(default=False,verbose_name="Ödendi Mi?")
    
    def __str__(self):
        return self.owner.username