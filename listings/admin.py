from django.contrib import admin
from .models import Address, Amenity, Listing, ListingImg, SearchHistory, ViewHistory


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """Admin configuration for addresses"""
    list_display = ['get_street', 'city', 'land', 'postal_code', 'country']
    search_fields = ['city', 'street', 'postal_code']
    list_filter = ['land']

    @admin.display(description='Street')
    def get_street(self, obj):
        addr = f'{obj.street} {obj.house_number}'
        if obj.apartment_number:
            addr += f', Apartment {obj.apartment_number}'
        return addr

@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    """Admin config. for amenities"""
    list_display = ['name', 'category', 'created_at']
    list_filter = ['category']


class ListingImageInline(admin.TabularInline):
    """Admin for listing  images"""
    model = ListingImg
    extra = 1


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    """Admin config. for listings"""
    list_display = ['title', 'owner', 'city_land', 'house_type', 'get_price', 'is_active', 'created_at']
    list_filter = ['house_type', 'is_active', 'created_at', 'address__land']
    date_hierarchy = 'created_at'
    search_fields = ['title', 'description', 'address__city']
    inlines = [ListingImageInline]
    filter_horizontal = ['amenities']
    readonly_fields = ['views_count', 'created_at', 'updated_at']
    actions = ['activate_listings', 'deactivate_listings']

    @admin.display(description='Location')
    def city_land(self, obj):
        if obj.address:
            return f"{obj.address.city}, {obj.address.land}" if obj.address.land else obj.address.city
        return '-'

    @admin.display(description='Price per night')
    def get_price(self, obj):
        return f"€{obj.price_per_night}"

    @admin.action(description='Activate selected listings')
    def activate_listings(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} listing(s) activated')

    @admin.action(description='Deactivate selected listings')
    def deactivate_listings(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} listing(s) deactivated')

@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    """Admin config. for search history"""
    list_display = ['query', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['query', 'user__email']
    readonly_fields = ['query', 'user', 'created_at']

    def has_add_permission(self, request):
        return False


@admin.register(ViewHistory)
class ViewHistoryAdmin(admin.ModelAdmin):
    """Ability to search history"""
    list_display = ['listing', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['listing__title', 'user__email']
    readonly_fields = ['listing', 'user', 'created_at']

    def has_add_permission(self, request):
        return False