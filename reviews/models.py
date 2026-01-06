from django.db import models
from core.mixins import TimestampMixin
from core.validators import validate_rating


class Review(TimestampMixin):
    """Review model for listings"""
    listing = models.ForeignKey('listings.Listing', on_delete=models.CASCADE, related_name='reviews')
    author = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='reviews')
    booking = models.OneToOneField(
        'bookings.Booking', on_delete=models.CASCADE,
        related_name='review', null=True, blank=True
    )
    rating = models.PositiveIntegerField(validators=[validate_rating])
    comment = models.TextField()

    class Meta:
        db_table = 'reviews'
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ['-created_at']
        unique_together = ('listing', 'author')
        indexes = [
            models.Index(fields=['listing']),
            models.Index(fields=['author']),
            models.Index(fields=['rating']),
        ]

    def __str__(self):
        return f'Review by {self.author.username} for {self.listing.title}'


class ReviewImg(TimestampMixin):
    """Review model for images"""
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='images')
    img = models.ImageField(upload_to='reviews/%Y/%m/%d/')
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'review_imgs'
        verbose_name = 'Review image'
        verbose_name_plural = 'Review images'
        ordering = ['-created_at']

    def __str__(self):
        return f'Review image #{self.review.id}'