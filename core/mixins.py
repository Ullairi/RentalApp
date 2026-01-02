from django.db import models
from django.utils import timezone


class TimestampMixin(models.Model):
    """Custom mixin that help tracking when record was created or changed"""
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Creation date')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Update date')

    class Meta:
        abstract = True


class SoftDeleteQuerySet(models.QuerySet):
    """Custom Queryset that help filter deleted and active records"""
    def delete(self): #soft deleting all records. Records still gonna be in database
        return self.update(deleted_at=timezone.now())

    def hard_delete(self): #permanently deletes all the records in queryset
        return super().delete()

    def show_not_deleted(self): #return records that are not soft-deleted
        return self.filter(deleted_at__isnull=True)

    def show_deleted(self): #return soft-deleted records
        return self.filter(deleted_at__isnull=False)


class SoftDeleteManager(models.Manager):
    """Manager for hiding soft-deleted records"""
    def get_queryset(self): #return only non-deleted records
        return SoftDeleteQuerySet(self.model, using=self._db).show_not_deleted()

    def all_records(self): #return both soft/non-soft deleted records
        return SoftDeleteQuerySet(self.model, using=self._db)

    def deleted_only(self): #return only soft-deleted records
        return SoftDeleteQuerySet(self.model, using=self._db).show_deleted()


class SoftDeleteMixin(models.Model):
    """
    Custom mixin for soft deletion
    Objects simply marks as deleted, instead of being removed from database
    """
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='Deletion date')
    objects = SoftDeleteManager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False): #soft-deleting of an object
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at'])

    def restore(self): #restoring of soft-deleted object
        self.deleted_at = None
        self.save(update_fields=['deleted_at'])

    def hard_delete(self): #full deletion of an object from db
        super().delete()