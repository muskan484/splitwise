from django.db import models
from user.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

class Expense(models.Model):
    expense_choice = [
        ('equal','Equal'),
        ('exact','Exact'),
        ('percent','Percent'),
    ]
    payer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses_paid',null = True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0),MaxValueValidator(100000000)],null =False)
    expense_type = models.CharField(max_length=10, choices=expense_choice , null =False)
    expense_name = models.CharField(max_length=200, blank = True)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self):
        return f'{self.amount} payed by {self.payer}'

class Passbook(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='balances')
    owes_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owed_balances')
    amount = models.DecimalField(max_digits=12, decimal_places=2)