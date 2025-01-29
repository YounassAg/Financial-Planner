from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    currency = models.CharField(max_length=10, default='USD')  # Currency preference
    monthly_income = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    savings_target = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.username}'s Profile"

# Signal to create a profile when a user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Category(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Null for default categories
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')  # For subcategories
    is_default = models.BooleanField(default=False)  # Default categories provided by the app

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    date = models.DateField()
    description = models.TextField(blank=True, null=True)
    is_recurring = models.BooleanField(default=False)  # Recurring expense flag
    recurrence_frequency = models.CharField(max_length=50, blank=True, null=True)  # e.g., "Monthly", "Weekly"
    payment_method = models.CharField(max_length=50, blank=True, null=True)  # e.g., "Credit Card", "Cash"

    def __str__(self):
        return f"{self.amount} - {self.category} - {self.date}"

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()  # Start of the budget period
    end_date = models.DateField()  # End of the budget period
    alert_threshold = models.DecimalField(max_digits=5, decimal_places=2, default=80)  # Percentage threshold for alerts

    def __str__(self):
        return f"{self.category} - {self.amount} ({self.start_date} to {self.end_date})"

class Goal(models.Model):
    GOAL_TYPES = [
        ('SAVINGS', 'Savings'),
        ('DEBT', 'Debt Repayment'),
        ('INVESTMENT', 'Investment'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)  # Goal name
    goal_type = models.CharField(max_length=50, choices=GOAL_TYPES, default='SAVINGS')
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deadline = models.DateField()
    is_completed = models.BooleanField(default=False)  # Track goal completion

    def __str__(self):
        return f"{self.name} - {self.target_amount} by {self.deadline}"
    
class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('INCOME', 'Income'),
        ('EXPENSE', 'Expense'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    date = models.DateField()
    description = models.TextField(blank=True, null=True)
    is_recurring = models.BooleanField(default=False)
    recurrence_frequency = models.CharField(max_length=50, blank=True, null=True)
    payment_method = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.amount} - {self.category} - {self.date}"
    
class Report(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    report_type = models.CharField(max_length=100)  # e.g., "Monthly Summary", "Spending Trends"
    generated_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField()  # Store report data in JSON format

    def __str__(self):
        return f"{self.report_type} - {self.generated_at}"