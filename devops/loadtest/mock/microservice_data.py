import random
import uuid
import os
import mock_utils

user_to_mock = 1000

# SQL statements to create the tables in the "user" database
create_user_db_sql = """
DROP DATABASE IF EXISTS userdb;
CREATE DATABASE userdb;
SET DATABASE = userdb;

CREATE TABLE users (
  id UUID NOT NULL,
  email VARCHAR(255) NULL,
  fullname VARCHAR(255) NULL,
  phone_no VARCHAR(10) NULL,
  birthday DATE NULL,
  password VARCHAR(255) NULL,
  created_at TIMESTAMP NULL DEFAULT now():::TIMESTAMP,
  CONSTRAINT users_pkey PRIMARY KEY (id ASC),
  UNIQUE INDEX ix_users_id (id ASC),
  UNIQUE INDEX ix_users_email (email ASC)
);

"""

# SQL statements to create the tables in the "account" database
create_account_db_sql = """
DROP DATABASE IF EXISTS account;
CREATE DATABASE account;
SET DATABASE = account;

CREATE TABLE accounts (
  id UUID NOT NULL,
  user_id UUID NULL,
  account_number VARCHAR(255) NULL,
  account_balance FLOAT8 NULL,
  created_at TIMESTAMP NULL DEFAULT now():::TIMESTAMP,
  CONSTRAINT accounts_pkey PRIMARY KEY (id ASC),
  UNIQUE INDEX ix_accounts_id (id ASC),
  UNIQUE INDEX ix_accounts_account_number (account_number ASC)
);

"""

# SQL statements to create the tables in the "transaction" database
create_transaction_db_sql = """
DROP DATABASE IF EXISTS transaction;
CREATE DATABASE transaction;
SET DATABASE = transaction;

CREATE TABLE transactions (
  id UUID NOT NULL,
  account_number VARCHAR(255) NULL,
  amount FLOAT8 NULL,
  transaction_type VARCHAR(255) NULL,
  created_at TIMESTAMP NULL DEFAULT now():::TIMESTAMP,
  CONSTRAINT transactions_pkey PRIMARY KEY (id ASC),
  UNIQUE INDEX ix_transactions_id (id ASC)
);

CREATE TABLE transfers (
  id UUID NOT NULL,
  destination_account_number VARCHAR(255) NULL,
  CONSTRAINT transfers_pkey PRIMARY KEY (id ASC),
  CONSTRAINT transfers_id_fkey FOREIGN KEY (id) REFERENCES transactions(id) ON DELETE CASCADE
);

"""

password = mock_utils.get_password_hash("test")

# Generate 1000 users
users = []
phones = []
for i in range(1, user_to_mock+1):
    email = f"{i}@ubu.ac.th"
    fullname = f"User {i}"
    phone_no = mock_utils.rand_phone_no()
    while phone_no in phones:
        phone_no = mock_utils.rand_phone_no()
    phones.append(phone_no)
    birthday = mock_utils.rand_birthday()
    users.append(
        (
            uuid.uuid4(),
            email,
            fullname,
            phone_no,
            birthday,
            password,
            mock_utils.rand_user_account_create()
        )
    )

# Generate SQL statements to insert the users and their accounts
accounts = []
user_sql = []
account_sql = []
transaction_sql = []
for user in users:
    account_number = mock_utils.rand_account_no()
    while account_number in accounts:
        account_number = mock_utils.rand_account_no()
    accounts.append(account_number)
    user_sql.append(
        mock_utils.user_sql(
            user[0], user[1], user[2], user[3], user[4], user[5], user[6]
        )
    )
    account_sql.append(
        mock_utils.account_sql(
            uuid.uuid4(),
            user[0],
            account_number,
            0,
            user[6]
        )
    )
    # init deposit
    init_deposit_uuid = uuid.uuid4()
    init_deposit_amount = random.randint(100000,1000000)
    account_sql.append(
        mock_utils.increase_account_balance(
            account_number,
            init_deposit_amount
        )
    )
    transaction_sql.append(
        mock_utils.insert_transaction(
            'deposit',
            init_deposit_uuid,
            account_number,
            init_deposit_amount,
            user[6]
        )
    )
    # rand deposit
    for i in range(random.randint(1, 5)):
        rand_deposit_uuid = uuid.uuid4()
        rand_deposit_amount = random.randint(100,1000000)
        account_sql.append(
            mock_utils.increase_account_balance(
                account_number,
                rand_deposit_amount
            )
        )
        transaction_sql.append(
            mock_utils.insert_transaction(
                'deposit',
                rand_deposit_uuid,
                account_number,
                rand_deposit_amount,
                mock_utils.rand_transaction_create()
            )
        )
    # rand withdraw
    for i in range(random.randint(1, 5)):
        rand_withdraw_uuid = uuid.uuid4()
        rand_withdraw_amount = random.randint(100,1000)
        account_sql.append(
            mock_utils.decrease_account_balance(
                account_number,
                rand_withdraw_amount
            )
        )
        transaction_sql.append(
            mock_utils.insert_transaction(
                'withdraw',
                rand_withdraw_uuid,
                account_number,
                rand_withdraw_amount,
                mock_utils.rand_transaction_create()
            )
        )

# Generate random transfers for each account
for account in accounts:
    for i in range(random.randint(2, 10)):
        destination_account_number = account
        while destination_account_number == account:
            destination_account_number = random.choice(accounts)
        rand_transfer_uuid = uuid.uuid4()
        rand_transfer_amount = random.randint(100,10000)
        account_sql.append(
            mock_utils.decrease_account_balance(
                account,
                rand_transfer_amount
            )
        )
        account_sql.append(
            mock_utils.increase_account_balance(
                destination_account_number,
                rand_transfer_amount
            )
        )
        transaction_sql.append(
            mock_utils.insert_transaction(
                'transfer',
                rand_transfer_uuid,
                account,
                rand_transfer_amount,
                mock_utils.rand_transaction_create()
            )
        )
        transaction_sql.append(
            mock_utils.insert_transfer(
                rand_transfer_uuid,
                destination_account_number
            )
        )

# Combine the SQL statements to create the tables and insert the mock data
final_user_sql = create_user_db_sql + "\n".join(user_sql)
final_account_sql = create_account_db_sql + "\n".join(account_sql)
final_transaction_sql = create_transaction_db_sql + "\n".join(transaction_sql)

user_file_path = "preload/mock_microservice_user_data.sql"
account_file_path = "preload/mock_microservice_account_data.sql"
transaction_file_path = "preload/mock_microservice_transaction_data.sql"
directory = os.path.dirname(user_file_path)

if not os.path.exists(directory):
    os.makedirs(directory)

# Write the SQL statements to a file
with open(user_file_path, "w") as f:
    f.write(final_user_sql)
with open(account_file_path, "w") as f:
    f.write(final_account_sql)
with open(transaction_file_path, "w") as f:
    f.write(final_transaction_sql)