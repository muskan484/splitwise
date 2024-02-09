from django.urls import path
from .views import (AddExpense,
                    RetreiveExpense,
                    ListPassbook,
                    UserPassbook)

urlpatterns = [
    path('expense',AddExpense.as_view()), # endpoint for creating new expense and listing all the expenses
    path('expense/<int:user>',RetreiveExpense.as_view()), # endpoint to show user specific expenses
    path('passbook',ListPassbook.as_view()), # endpoint for listing all passbook entries
    path('passbook/<int:user>',UserPassbook.as_view()), # endpoint to show user specific passbook
]