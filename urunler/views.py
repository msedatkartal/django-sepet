from django.shortcuts import render,redirect
from .models import *
import iyzipay
import json
# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import requests
import pprint
from django.core.cache import cache


api_key = 'sandbox-fgjb0rrUAeZGnHeaXrYAzO9wdPETODOo'
secret_key = 'sandbox-RqeOcKeMqKDuvYHGwdUesNPMgwflbs6k'
base_url = 'sandbox-api.iyzipay.com'


options = {
    'api_key': api_key,
    'secret_key': secret_key,
    'base_url': base_url
}
sozlukToken = list()


def payment(request):
    context = dict()
    # odeme = Odeme.objects.get(user = request.user, odendiMi = False)
    userpay = Payment.objects.get(owner = request.user, isPayment = False)
    buyer={
        'id': 'BY789',
        'name': 'Sedat',
        'surname': 'Doe',
        'gsmNumber': '+905350000000',
        'email': 'msedatkartal@gmail.com',
        'identityNumber': '74300864791',
        'lastLoginDate': '2015-10-05 12:43:35',
        'registrationDate': '2013-04-21 15:12:09',
        'registrationAddress': 'Nidakule Göztepe, Merdivenköy Mah. Bora Sok. No:1',
        'ip': '85.34.78.112',
        'city': 'Istanbul',
        'country': 'Turkey',
        'zipCode': '34732'
    }

    address={
        'contactName': 'Jane Doe',
        'city': 'Istanbul',
        'country': 'Turkey',
        'address': 'Nidakule Göztepe, Merdivenköy Mah. Bora Sok. No:1',
        'zipCode': '34732'
    }

    basket_items=[
        {
            'id': 'BI101',
            'name': 'Binocular',
            'category1': 'Collectibles',
            'category2': 'Accessories',
            'itemType': 'PHYSICAL',
            'price': '0.3'
        },
        {
            'id': 'BI102',
            'name': 'Game code',
            'category1': 'Game',
            'category2': 'Online Game Items',
            'itemType': 'VIRTUAL',
            'price': '0.5'
        },
        {
            'id': 'BI103',
            'name': 'Usb',
            'category1': 'Electronics',
            'category2': 'Usb / Cable',
            'itemType': 'PHYSICAL',
            'price': '0.2'
        }
    ]

    request={
        'locale': 'tr',
        'conversationId': '123456789',
        'price': '1',
        'paidPrice': userpay.totalPrice,
        'currency': 'TRY',
        'basketId': 'B67832',
        'paymentGroup': 'PRODUCT',
        "callbackUrl": "http://127.0.0.1:8000/result/",
        "enabledInstallments": ['2', '3', '6', '9'],
        'buyer': buyer,
        'shippingAddress': address,
        'billingAddress': address,
        'basketItems': basket_items,
        # 'debitCardAllowed': True
    }

    checkout_form_initialize = iyzipay.CheckoutFormInitialize().create(request, options)

    #print(checkout_form_initialize.read().decode('utf-8'))
    page = checkout_form_initialize
    header = {'Content-Type': 'application/json'}
    content = checkout_form_initialize.read().decode('utf-8')
    json_content = json.loads(content)
    print(type(json_content))
    print(json_content["checkoutFormContent"])                
    print("************************")
    print(json_content["token"])
    print("************************")
    token = json_content['token']
    cache.set('token',token)
    sozlukToken.append(json_content["token"])
    return HttpResponse(f'<div id="iyzipay-checkout-form" class="responsive">{json_content["checkoutFormContent"]}</div>')


@require_http_methods(['POST'])
@csrf_exempt
def result(request):
    context = dict()

    url = request.META.get('index')
    token = cache.get('token')
    
    request = {
        'locale': 'tr',
        'conversationId': '123456789',
        'token': token
    }
    checkout_form_result = iyzipay.CheckoutForm().retrieve(request, options)
    print("************************")
    print(type(checkout_form_result))
    result = checkout_form_result.read().decode('utf-8')
    print("************************")
    print(sozlukToken[0])   # Form oluşturulduğunda 
    print("************************")
    print("************************")
    sonuc = json.loads(result, object_pairs_hook=list)
    #print(sonuc[0][1])  # İşlem sonuç Durumu dönüyor
    #print(sonuc[5][1])   # Test ödeme tutarı
    print("************************")
    for i in sonuc:
        print(i)
    print("************************")
    print(sozlukToken)
    print("************************")
    if sonuc[0][1] == 'success':
        context['success'] = 'Başarılı İŞLEMLER'
        return HttpResponseRedirect(reverse('success'), context)

    elif sonuc[0][1] == 'failure':
        context['failure'] = 'Başarısız'
        return HttpResponseRedirect(reverse('failure'), context)

    return HttpResponse(url)


def success(request):
    shopcards = ShopCard.objects.filter(owner = request.user, isPayment = False)
    for card in shopcards:
        card.isPayment = True
        card.save()
    
    userpay = Payment.objects.get(owner = request.user, isPayment = False)
    userpay.isPayment = True
    userpay.save()
    
    return redirect('index')


def fail(request):
    context = dict()
    context['fail'] = 'İşlem Başarısız'
    # messages.error(request, 'İşlem başarısız')
    return redirect('index')

def index(request):
    products = Product.objects.all()
    if request.method == "POST":
        if request.user.is_authenticated:
            productId = request.POST.get('productId')
            count = request.POST.get('count')
            product = Product.objects.get(id = productId)
            if product.stock >= int(count):
                if ShopCard.objects.filter(owner = request.user,product = product, isPayment = False).exists():
                    shop = ShopCard.objects.get(owner = request.user, product=product, isPayment = False)
                    shop.count += int(count)
                    shop.totalPrice = product.price * shop.count
                    shop.save()
                else:
                    shop = ShopCard.objects.create(
                        owner = request.user,
                        product = product,
                        count = int(count),
                        totalPrice = product.price * int(count),
                    )
                    shop.save()
                product.stock -= int(count)
                product.save()
            else:
                print("stok yetersiz")
                return redirect('index')
    context = {
        "products" : products,
    }
    return render(request,'index.html',context)

def detail(request,pk):
    product = Product.objects.get(slug = pk)
    context = {
        'product':product
    }
    return render(request,'detail.html',context)

def cards(request):
    shopcards = ShopCard.objects.filter(owner = request.user, isPayment = False)
    toplam = 0
    for i in shopcards:
        toplam += i.totalPrice
    
    if request.method == "POST":
        if 'delete' in request.POST:
            cardId = request.POST.get('cardId')
            card = ShopCard.objects.get(id = cardId)
            card.product.stock += card.count
            card.product.save()
            card.delete()
            return redirect ('cards')
        if 'update' in request.POST:
            cardId = request.POST.get('cardId')
            card = ShopCard.objects.get(id= cardId)
            countForm = request.POST.get('adet')
            card.count = int(countForm)
            card.totalPrice = card.product.price * int(countForm)
            card.save()
            return redirect('cards')
        if 'payment' in request.POST:
            if Payment.objects.filter(owner = request.user,isPayment = False).exists():
                userpay = Payment.objects.get(owner = request.user, isPayment = False)
                userpay.totalPrice = toplam
                userpay.products.add(*shopcards)
                userpay.save()
                return redirect('payment')
            else:
                newPayment = Payment.objects.create(
                    owner = request.user,
                    totalPrice = toplam
                )
                newPayment.products.add(*shopcards)
                newPayment.save()
                return redirect('payment')
    context = {
        'shopcards': shopcards,
        'toplam':toplam,
    }
    return render(request,'shopcards.html',context)

def view_404(request,exception):
    return redirect('/')

def view_500(request):
    return render(request,"hata.html")