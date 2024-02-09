from rest_framework import views
from rest_framework import status
from .models import Expense, Passbook
from rest_framework.response import Response
from .serializers import ExpenseSerializer,PassbookSerializer
from .utility import (manage_equal_expense,
                      manage_exact_expense,
                      manage_percentage_expense,
                      generate_balances)


class AddExpense(views.APIView):

    """
    A view to handle adding and listing expenses.

    Methods: GET and POST

    Returns:
    - If successful, returns the appropriate response based on the expense type.
    - If unsuccessful due to missing or invalid data, returns an error response with appropriate messages.
    """

    def get(self, request, *args, **kwargs):
        """
        Retrieves a list of all expenses.
        """
        queryset = Expense.objects.all()
        serializer = ExpenseSerializer(queryset, many= True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """
        Adds a new expense.

        Request Body Format:
        {
            "payer": int,
            "amount": float,
            "expense_type": string,
            "expense_name": string,
            "note": string,
            "participant_detail": list
        }

        Returns:
        - Success response if the expense is added successfully.
        - Error response if there are missing or invalid parameters.
        """
        request_data = request.data
        try:
            participant_detail = request_data.pop('participant_detail')
        except:
            return Response({'Error':"Participant_detail key is required"},status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ExpenseSerializer(data = request_data)
        serializer.is_valid()
        expense_detail = serializer.validated_data
        expense_type = expense_detail.get("expense_type")
        total_amount = expense_detail['amount']
        payer = expense_detail['payer']
        
        if len(participant_detail) > 1000:
            return Response({"Error":"Too many participants. Maximum allowed is 1000."},status=status.HTTP_400_BAD_REQUEST)
        
        if total_amount > 10000000:
            return Response({"Error":"Expense amount exceeds the maximum limit of 10,000,000."},status=status.HTTP_400_BAD_REQUEST)
        
        if expense_type == "equal":
            response =  manage_equal_expense(total_amount,payer,participant_detail)

        elif expense_type == "exact":
            response = manage_exact_expense(total_amount,payer,participant_detail)
             
        elif expense_type == "percent":
            response = manage_percentage_expense(total_amount,payer,participant_detail)
        else:
            return Response({"Error":"Invalid expense_type"},status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save()
        return response

class RetreiveExpense(views.APIView):
    """
    A view to retrieve expenses associated with a particular user

    Methods: GET
    """
    def get(self, request, *args, **kwargs):
        """
        Retrieves the list of expenses for a particular user.
        """
        user = kwargs['user']
        queryset = Expense.objects.filter(payer=user)
        serializer_data = ExpenseSerializer(queryset,many = True).data
        return Response(serializer_data)

class ListPassbook(views.APIView):
    """
    A view to list passbook entries.

    Methods: GET
    """
    def get(self, request, *args, **kwargs):
        """
        If 'simplify' query parameter is set to True, simplified passbook entries are returned else detailed passbook entries are returned.
        """
        simplify = request.query_params.get('simplify',False)
        result_dict = generate_balances(simplify)
        return Response(result_dict,status=status.HTTP_200_OK)

class UserPassbook(views.APIView):
    """
    A view to retrieve passbook entries for a specific user.

    Methods: GET
    """
    def get(self, request, *args, **kwargs):
        """
        Retrieves passbook entries for a specific user.
        """
        user = kwargs['user']
        user_data = PassbookSerializer(Passbook.objects.filter(user=user), many=True)
        owes_to_data = PassbookSerializer(Passbook.objects.filter(owes_to = user),many = True)
        response_data = user_data.data + owes_to_data.data 
        return Response(response_data,status=status.HTTP_200_OK)