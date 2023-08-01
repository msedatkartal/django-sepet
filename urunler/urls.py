from django.urls import path
from .views import *

urlpatterns = [
    path('',index,name="index"),
    path('urun-detay-<str:pk>',detail,name='detail'),
    path('sepetim/',cards,name='cards'),
    path('payment/',payment,name='payment'),
    path('result/',result,name='result'),
    path('success/',success,name='success'),
    path('failure/',fail,name='failure')
]
