from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class User(AbstractUser):
    ROLE_CHOICES = (
        ('USER', 'Regular User'),
        ('PARTNER', 'Partner'),
        ('ADMIN', 'Administrator')
    )
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='USER')
    partner_request_status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('APPROVED', 'Approved'),
            ('REJECTED', 'Rejected'),
            ('NONE', 'None')
        ],
        default='NONE'
    )
    partner_request_date = models.DateTimeField(null=True, blank=True)
    partner_documents = models.TextField(blank=True, null=True)

    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )
