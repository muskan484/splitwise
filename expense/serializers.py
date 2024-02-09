from rest_framework import serializers
from .models import Expense,Passbook
from user.serializers import UserSerializer

class PassbookSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    owes_to = UserSerializer()
    class Meta:
        model = Passbook
        fields = ['id', 'user', 'owes_to', 'amount']

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = ['id', 'payer', 'amount', 'expense_type', 'expense_name', 'created_at', 'updated_at']
