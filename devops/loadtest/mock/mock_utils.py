import random
import string
from passlib.context import CryptContext


def user_sql(id, email, fullname, phone_no, birthday, password, created_at) -> str:
    return f"INSERT INTO users (id, email, fullname, phone_no, birthday, password, created_at) VALUES ('{id}', '{email}', '{fullname}', '{phone_no}', '{birthday}', '{password}', '{created_at}');"


def account_sql(id, user_id, account_number, account_balance, created_at) -> str:
    return f"INSERT INTO accounts (id, user_id, account_number, account_balance, created_at) VALUES ('{id}', '{user_id}', '{account_number}', {account_balance}, '{created_at}');"


def increase_account_balance(account_number, amount) -> str:
    return f"""UPDATE accounts SET account_balance = account_balance + {amount} WHERE account_number = '{account_number}';"""


def decrease_account_balance(account_number, amount) -> str:
    return f"""UPDATE accounts SET account_balance = account_balance - {amount} WHERE account_number = '{account_number}';"""


def insert_transaction(tx_type, id, account_number, amount, created_at) -> str:
    return f"""INSERT INTO transactions (id, account_number, amount, transaction_type, created_at) VALUES ('{id}', '{account_number}', {amount}, '{tx_type}', '{created_at}');"""


def insert_transfer(id, destination_account_number) -> str:
    return f"""INSERT INTO transfers (id, destination_account_number) VALUES ('{id}', '{destination_account_number}');"""


def deposit_sql(id, account_number, amount, created_at) -> str:
    return increase_account_balance(account_number, amount) + "\n" \
        + insert_transaction('deposit', id, account_number, amount, created_at)


def withdraw_sql(id, account_number, amount, created_at) -> str:
    return decrease_account_balance(account_number, amount) + "\n" \
        + insert_transaction('withdraw', id, account_number, amount, created_at)


def transfer_sql(id, account_number, amount, destination_account_number, created_at) -> str:
    return decrease_account_balance(account_number, amount) + "\n" \
        + increase_account_balance(destination_account_number, amount) + "\n" \
        + insert_transaction('transfer', id, account_number, amount, created_at) + "\n" \
        + insert_transfer(id, destination_account_number)


def get_password_hash(password) -> str:
    return CryptContext(schemes=["bcrypt"], deprecated="auto").hash(password)


def rand_phone_no() -> str:
    return random.choice(['06', '08', '09']) + ''.join(random.choices(string.digits, k=8))


def rand_account_no() -> str:
    return ''.join(random.choices(string.digits, k=10))


def rand_date_in_range(start_year: int, end_year: int) -> str:
    year = random.randint(start_year, end_year)
    month = random.randint(1, 12)

    if month == 2:
        if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
            day = random.randint(1, 29)
        else:
            day = random.randint(1, 28)
    elif month in [4, 6, 9, 11]:
        day = random.randint(1, 30)
    else:
        day = random.randint(1, 31)

    return f"{year:04d}-{month:02d}-{day:02d}"


def rand_birthday() -> str:
    return rand_date_in_range(1960, 2014)


def rand_user_account_create() -> str:
    date = rand_date_in_range(2021, 2021)
    time = f"{random.randint(0, 23):02d}:{random.randint(0, 59):02d}:{random.randint(0, 59):02d}"
    return f"{date} {time}"


def rand_transaction_create() -> str:
    date = rand_date_in_range(2022, 2022)
    time = f"{random.randint(0, 23):02d}:{random.randint(0, 59):02d}:{random.randint(0, 59):02d}"
    return f"{date} {time}"
