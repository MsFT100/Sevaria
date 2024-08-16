from django.db import models
import uuid

class Payment(models.Model):
    TRANSACTION_STATUSES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    transaction_reference = models.CharField(max_length=255, unique=True, default=uuid.uuid4, editable=False)
    tracking_id = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    first_name = models.CharField(max_length=15, blank=True, null=True)
    last_name = models.CharField(max_length=15, blank=True, null=True)
    country = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUSES, default='PENDING')
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_reference} - {self.status}"

    class Meta:
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['date_created']),
        ]
