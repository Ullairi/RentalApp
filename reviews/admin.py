from django.contrib import admin
from django import forms
from .models import Review, ReviewImg


class ReviewAdminForm(forms.ModelForm):
    rating = forms.ChoiceField(choices=[(i, i) for i in range(1, 6)])

    class Meta:
        model = Review
        fields = '__all__'


class ReviewImgInline(admin.TabularInline):
    model = ReviewImg
    extra = 1


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    form = ReviewAdminForm
    list_display = ['id', 'author', 'listing', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['author__email', 'listing__title', 'comment']
    inlines = [ReviewImgInline]
    readonly_fields = ['booking', 'created_at', 'updated_at']

    fieldsets = (
        ('Review Info', {'fields': ('listing', 'author', 'booking')}),
        ('Content', {'fields': ('rating', 'comment')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


@admin.register(ReviewImg)
class ReviewImgAdmin(admin.ModelAdmin):
    list_display = ['id', 'review', 'created_at']
    readonly_fields = ['created_at']