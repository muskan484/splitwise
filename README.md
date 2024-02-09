Splitwise is a RESTful API built using Django Rest Framework. It utilizes SQLite as database for storing data. The project employs Celery in conjunction with Redis as a message broker to handle tasks such as sending emails to users.

## Installation

1. Clone the repository:

git clone "URL",

2. Commands to run the project
    - python3 -m venv <ENV_NAME>
    - source <ENV_NAME>/bin/activate
    - pip3 install -r requirements.txt
    - Migrations for database 
        python3 manage.py makemigrations
        python3 manage.py migrate  
    - Start the development server:
        python3 manage.py runserver
    - Run redis-server
        redis-server
    - Run celery worker
        celery -A password_manager worker --loglevel=info
    - Run celery beat
        celery -A password_manager beat --loglevel=info

## Models


### User Model

- userId: CharField, unique identifier for the user.
- name: CharField, stores the name of the user.
- email: EmailField, unique email address of the user.
- mobile_number: CharField, stores the mobile number of the user.

### Expense Model

- payer: ForeignKey to User model, represents the user who paid the expense.
- amount: DecimalField, stores the amount of the expense, with validators for minimum and maximum values.
- expense_type: CharField with choices, indicates the type of expense (equal, exact, percent).
- expense_name: CharField, optional field to specify the name of the expense.
- note: TextField, optional field to add notes related to the expense.
- created_at: DateTimeField, automatically records the creation date and time.
- updated_at: DateTimeField, automatically records the last update date and time.

### Passbook Model

- user: ForeignKey to User model, represents the user for whom the passbook entry is recorded.
- owes_to: ForeignKey to User model, represents the user who is owed the amount.
- amount: DecimalField, stores the amount owed by the user to the owes_to user.

## API endpoints

1. /api/user  

    This endpoint is used to create new user and list all users

    Methods: GET and POST

    Request Body : 
    ```
    {
        'username' : '',
        'email_id' : '',
        'password' : '',
        'mobile_number' : ''
    }
    ```

2. /api/expense

    This endpoint is used to create new expense and listing all the expenses

    Methods: GET and POST

    Request Body:
    * for adding equal type of expense
        ```
        {
            "payer": '',
            "amount": '',
            "expense_type": '',
            "expense_name": '',
            "note": '',
            "participant_detail": [{"id":""},{"id":""}...]
        }
        ```

    * for adding exact type of expense
        ```
        {
            "payer": '',
            "amount": '',
            "expense_type": '',
            "expense_name": '',
            "note": '',
            "participant_detail": [{"id":"","amount":""},{"id":"","amount":""}...]
        }
        ```
    * for adding percentage type of expense
    ```
    {
        "payer": '',
        "amount": '',
        "expense_type": '',
        "expense_name": '',
        "note": '',
        "participant_detail": [{"id":"","percentage":""},{"id":"","percentage":""}...]
    }
    ```
    
3. /api/expense/user_id
    This endpoint is used to retrieve expenses associated with a particular user
    Methods: GET

4. /api/passbook
    This endpoint is used to list all passbook entries
    pass query parameter:
    simplify=True : To view the simplified view of expenses
    simplify=False(Default) : To list all passbook entries

5. /api/passbook/user_id
    This endpoint is used to retrieve passbook entries for a specific user
    Methods: GET


## Email Notifications

- Mail is sent to each user involved in expense regarding this new expense creation
- A weekly mail is sent to each user regarding the summary of amounts owed to other user
