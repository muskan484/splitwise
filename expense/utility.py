from user.models import User
from .models import Passbook
from rest_framework import status
from collections import defaultdict
from expense.tasks import send_email_task
from .serializers import PassbookSerializer
from rest_framework.response import Response


def manage_equal_expense(total_amount, payer, participant_detail):
    """
    Manages equal expenses among participants.
    
    Parameters:
    - total_amount (float): The total amount of the expense.
    - payer (str): The user who paid the expense.
    - participant_detail (list): List of dictionaries containing participant details. 
                                 Eg: [{"id":1},{"id":3}...]

    Returns: Response indicating the status of the expense creation.

    Notes:
    - For equal expense type, each participant owes the same amount.
    - Passbook entries are created for each participant.
    - Emails are sent to notify participants about their share of the expense.

    """
    if any("amount" in participant for participant in participant_detail) or any("percentage" in participant for participant in participant_detail):
        return Response({"Error":"Amount or percentage is not required for equal type of split"},status=status.HTTP_400_BAD_REQUEST)

    each_person_owes = round(total_amount/len(participant_detail),2)
    for index, participant in enumerate(participant_detail):
        passbook = Passbook()
        passbook.owes_to = payer
        passbook.user = User.objects.get(pk = participant['id'])

        if each_person_owes * len(participant_detail) == total_amount:
            passbook.amount = each_person_owes
        else:
            if index == 0:
                remaining_amount = total_amount - each_person_owes * len(participant_detail)
                passbook.amount = each_person_owes+remaining_amount
            else:
                passbook.amount = each_person_owes
        passbook.save()
        email_data = {
            'user_name': passbook.user.name,
            'user_email': passbook.user.email,
            'owes_to_name': passbook.owes_to.name,
            'amount': passbook.amount
        }
        send_email_task.delay(email_data)

    return Response({"Message":"Expense Created"},status=status.HTTP_201_CREATED)


def manage_exact_expense(total_amount, payer, participant_detail):
    """
    Manages exact expenses among participants.

    Parameters:
    - total_amount (float): The total amount of the expense.
    - payer (str): The user who paid the expense.
    - participant_detail (list): List of dictionaries containing participant details, including their specific amounts.
                                 Eg: [{"id":1,"amount":1000} , {"id":3, "amount":3000}]

    Returns: Response indicating the status of the expense creation.

    Notes:
    - For exact expense type, each participant owes a specific amount.
    - Passbook entries are created for each participant.
    - Emails are sent to notify participants about their share of the expense.

    """
    try:
        participant_total_amount = sum(round(item['amount'],2) for item in participant_detail)
    except:
        return Response({"Error":"Each participant's amount is required for exact type of split"},status=status.HTTP_400_BAD_REQUEST)
    
    if participant_total_amount != total_amount:
        return Response({"Error":"The calculated total amount of participants does not match the provided total amount"},status=status.HTTP_400_BAD_REQUEST)

    for participant in participant_detail:
        passbook = Passbook()
        passbook.owes_to = payer
        passbook.user = User.objects.get(pk = participant['id'])
        passbook.amount = round(participant['amount'],2)
        passbook.save()
        email_data = {
            'user_name': passbook.user.name,
            'user_email': passbook.user.email,
            'owes_to_name': passbook.owes_to.name,
            'amount': passbook.amount
        }
        send_email_task.delay(email_data)
    return Response({"Message":"Expense Created"},status=status.HTTP_201_CREATED)


def manage_percentage_expense(total_amount, payer, participant_detail):
    """
    Manages expenses split by percentage among participants.

    Parameters:
    - total_amount (float): The total amount of the expense.
    - payer (str): The user who paid the expense.
    - participant_detail (list): List of dictionaries containing participant details, including their percentages.
                                 Eg: [{"id":1,"percentage":40},{"id":3,"percentage":60}]

    Returns: Response indicating the status of the expense creation.

    Notes:
    - For percentage expense type, each participant's share is determined by their specified percentage.
    - Passbook entries are created for each participant.
    - Emails are sent to notify participants about their share of the expense.
    """
    try:
        participant_total_percentage = sum(round(float(item['percentage']),2) for item in participant_detail)
    except:
        return Response({"Error":"Each participant's percentage is required for percent type of split"},status=status.HTTP_400_BAD_REQUEST)
    
    if participant_total_percentage != 100:
        return Response({"Error":"The sum of participant's percentage is not equal to 100."},status=status.HTTP_400_BAD_REQUEST)

    for participant in participant_detail:
        passbook = Passbook()
        passbook.owes_to = payer
        passbook.user = User.objects.get(pk = participant['id'])
        passbook.amount = round(float(total_amount/100) * float(participant['percentage']),2)
        passbook.save()
        email_data = {
            'user_name': passbook.user.name,
            'user_email': passbook.user.email,
            'owes_to_name': passbook.owes_to.name,
            'amount': passbook.amount
        }
        send_email_task.delay(email_data)
    return Response({"Message":"Expense Created"},status=status.HTTP_201_CREATED)


def generate_balances(simplify):
    """
    Generates balances for users based on passbook entries.

    Parameters:
    - simplify (bool): A boolean flag indicating whether to simplify the balances or not.

    Returns:
    - If simplify is True, returns a dictionary containing simplified balances between users.
    - If simplify is False, returns serialized data of all passbook entries.

    Notes:
    - If simplify is True, balances between users are simplified, where each user only owes or is owed by another user.
    - If simplify is False, detailed passbook entries are returned.
    """
    if simplify:
        user_passbooks = Passbook.objects.values('user__userId', 'owes_to__userId', 'amount').order_by('user__userId')

        required_dict = defaultdict(dict)

        for data in user_passbooks:
            current_key, other_key, amount = data['user__userId'], data['owes_to__userId'], data['amount']

            required_dict[other_key][current_key] = required_dict[other_key].get(current_key, 0) + amount

        for current_key, current_value in required_dict.items():
            for other_key, other_value in required_dict.items():
                if current_key != other_key:
                    if current_key in other_value and other_key in current_value:
                        max_value = max(other_value[current_key], current_value[other_key])

                        other_value[current_key] = max_value - other_value[current_key]
                        current_value[other_key] = max_value - current_value[other_key]

                        if other_value[current_key] == 0.0:
                            del required_dict[other_key][current_key]
                        if current_value[other_key] == 0.0:
                            del required_dict[current_key][other_key]

        final_dict = {key: value for key, value in required_dict.items() if bool(value)}
        
        new_dict = {}
        for key,value in final_dict.items():
            if key in value:
                del value[key]
                new_dict[key]=value

        return {key:value for key, value in new_dict.items() if new_dict[key]}
    else:
        return PassbookSerializer(Passbook.objects.select_related('user'), many=True).data