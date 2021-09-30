from auctions.models import User


def add_variable_to_context(request):
    if request.user.is_authenticated:
        listings_in_watchlist = request.user.watchlist.listings.all().count()
    else:
        listings_in_watchlist = 0
    return {
        'listings_in_watchlist': listings_in_watchlist
    }