from django.contrib import admin
from django import forms
from .models import Review, ReviewImg


class ReviewAdminForm(forms.ModelForm):
    """Admin form for reviews"""
    RATING_CHOICES = [(i, f'{i}') for i in range(1, 6)]

    rating = forms.ChoiceField(choices=RATING_CHOICES, widget=forms.Select, label='Rating')

    class Meta:
        model = Review
        fields = '__all__'

    def clean_rating(self):
        return int(self.cleaned_data['rating'])


class ReviewImgInline(admin.TabularInline):
    """Inline admin view for reviews images"""
    model = ReviewImg
    extra = 1
    fields = ['img']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin config. for reviews"""
    form = ReviewAdminForm
    list_display = ['id', 'listing', 'author', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['author__username', 'listing__title', 'comment']
    inlines = [ReviewImgInline]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['author', 'listing', 'booking', 'created_at', 'updated_at']
        return ['created_at', 'updated_at']

    fieldsets = (
        ('Review Info', {'fields': ('listing', 'author', 'booking')}),
        ('Content', {'fields': ('rating', 'comment')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author', 'listing', 'booking')


@admin.register(ReviewImg)
class ReviewImgAdmin(admin.ModelAdmin):
    """Admin view for reviws images"""
    list_display = ['id', 'review', 'created_at']
    list_filter = ['created_at']
    readonly_fields = ['created_at']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('review')