from django.db import models

class Payment(models.Model):
    TRANSACTION_STATUSES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    transaction_reference = models.CharField(max_length=255)
    tracking_id = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUSES, default='PENDING')
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_reference} - {self.status}"
