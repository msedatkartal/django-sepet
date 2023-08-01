from .models import *

def get_count(request):
    if request.user.is_authenticated:
        cardsCount = ShopCard.objects.filter(owner = request.user, isPayment = False).count()
    else:
        cardsCount = None

    context = {
        'cardsCount':cardsCount
    }
    return context