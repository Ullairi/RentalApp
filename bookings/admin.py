from django.contrib import admin
from .models import Booking, BookingStatusHistory


class BookingStatusHistoryInline(admin.TabularInline):
    """Inline view for booking status history"""
    model = BookingStatusHistory
    extra = 0
    readonly_fields = ['history_status', 'comment', 'changed_by', 'created_at']
    can_delete = False


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Admin config. for booking"""
    list_display = ['id', 'tenant', 'listing', 'check_in', 'check_out', 'book_status', 'total_price', 'created_at']
    list_filter = ['book_status', 'check_in', 'created_at']
    search_fields = ['tenant__username', 'listing__title']
    readonly_fields = ['total_price', 'created_at', 'updated_at']
    inlines = [BookingStatusHistoryInline]

    fieldsets = (
        ('Booking Info', {'fields': ('listing', 'tenant', 'stayers', 'book_status')}),
        ('Dates', {'fields': ('check_in', 'check_out')}),
        ('Price', {'fields': ('total_price',), 'description': 'Calculated automatically'}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('tenant', 'listing')


@admin.register(BookingStatusHistory)
class BookingStatusHistoryAdmin(admin.ModelAdmin):
    """Admin view for booking status history"""
    list_display = ['id', 'booking', 'history_status', 'changed_by', 'created_at']
    list_filter = ['history_status', 'created_at']
    readonly_fields = ['booking', 'history_status', 'comment', 'changed_by', 'created_at']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False