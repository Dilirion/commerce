from django.contrib import admin
from .models import Comment, User, Listing, Bid, WatchList

class WatchListAdmin(admin.ModelAdmin):
    filter_horizontal = ('listings',)

# Register your models here.
admin.site.register(User)
admin.site.register(Listing)
admin.site.register(Bid)
admin.site.register(WatchList, WatchListAdmin)
admin.site.register(Comment)