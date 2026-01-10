from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model for employees, managers, and admins.
    """

    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('MANAGER', 'Manager'),
        ('EMPLOYEE', 'Employee'),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='EMPLOYEE'
    )
    
    employee_id = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True
    )
    
    department = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    
    position = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )
    
    date_joined_company = models.DateField(
        blank=True,
        null=True
    )
    
    is_active_employee = models.BooleanField(
        default=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def save(self, *args, **kwargs):
        if not self.employee_id and self.role != 'ADMIN':
            last_user = User.objects.filter(employee_id__isnull=False).order_by('-id').first()
            if last_user and last_user.employee_id:
                try:
                    last_id = int(last_user.employee_id.split('-')[-1])
                    new_id = last_id + 1
                except (ValueError, IndexError):
                    new_id = 1001
            else:
                new_id = 1001
            self.employee_id = f"EMP-{new_id:04d}"
        
        super().save(*args, **kwargs)
