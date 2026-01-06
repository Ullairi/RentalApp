from django.contrib import admin
from django import forms
from .models import Booking, BookingStatusHistory
from .services import BookingService


class BookingAdminForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        listing = cleaned_data.get('listing')
        check_in = cleaned_data.get('check_in')
        check_out = cleaned_data.get('check_out')
        tenant = cleaned_data.get('tenant')

        if listing and check_in and check_out:
            if check_out <= check_in:
                raise forms.ValidationError({'check_out': 'Check-out must be after check-in'})

            overlapping = Booking.objects.filter(
                listing=listing,
                book_status='confirmed',
                check_in__lt=check_out,
                check_out__gt=check_in
            )
            if self.instance.pk:
                overlapping = overlapping.exclude(pk=self.instance.pk)

            if overlapping.exists():
                raise forms.ValidationError({'check_in': 'These dates are already booked (confirmed)'})

            if tenant and listing.owner == tenant:
                raise forms.ValidationError({'tenant': 'Owner cannot book their own listing'})

            nights = (check_out - check_in).days
            cleaned_data['total_price'] = listing.price_per_night * nights

        return cleaned_data


class BookingStatusHistoryInline(admin.TabularInline):
    """Inline view for booking status history"""
    model = BookingStatusHistory
    extra = 0
    readonly_fields = ['history_status', 'comment', 'changed_by', 'created_at']
    can_delete = False


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Admin config. for booking"""
    form = BookingAdminForm
    list_display = ['id', 'tenant', 'listing', 'check_in', 'check_out', 'book_status', 'get_total_price', 'created_at']
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

    @admin.display(description='Total price')
    def get_total_price(self, obj):
        return f"€{obj.total_price}" if obj.total_price else '-'

    def save_model(self, request, obj, form, change):
        if 'total_price' in form.cleaned_data:
            obj.total_price = form.cleaned_data['total_price']
        super().save_model(request, obj, form, change)


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