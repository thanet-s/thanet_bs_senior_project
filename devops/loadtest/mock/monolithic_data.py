import random
import uuid
import os
import mock_utils

user_to_mock = 1000

# SQL statements to create the tables in the "monolithic" database
create_sql = """
DROP DATABASE IF EXISTS monolithic;
CREATE DATABASE monolithic;
SET DATABASE = monolithic;

CREATE TABLE users (
  id UUID NOT NULL,
  email VARCHAR(255) NULL,
  fullname VARCHAR(255) NULL,
  phone_no VARCHAR(10) NULL,
  birthday DATE NULL,
  password VARCHAR(255) NULL,
  created_at TIMESTAMP NULL DEFAULT now():::TIMESTAMP,
  CONSTRAINT users_pkey PRIMARY KEY (id ASC),
  UNIQUE INDEX ix_users_email (email ASC),
  UNIQUE INDEX ix_users_id (id ASC)
);

CREATE TABLE accounts (
  id UUID NOT NULL,
  user_id UUID NULL,
  account_number VARCHAR(255) NULL,
  account_balance FLOAT8 NULL,
  created_at TIMESTAMP NULL DEFAULT now():::TIMESTAMP,
  CONSTRAINT accounts_pkey PRIMARY KEY (id ASC),
  CONSTRAINT accounts_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  UNIQUE INDEX ix_accounts_id (id ASC),
  UNIQUE INDEX ix_accounts_account_number (account_number ASC)
);

CREATE TABLE transactions (
  id UUID NOT NULL,
  account_number VARCHAR(255) NULL,
  amount FLOAT8 NULL,
  transaction_type VARCHAR(255) NULL,
  created_at TIMESTAMP NULL DEFAULT now():::TIMESTAMP,
  CONSTRAINT transactions_pkey PRIMARY KEY (id ASC),
  CONSTRAINT transactions_account_number_fkey FOREIGN KEY (account_number) REFERENCES accounts(account_number) ON DELETE CASCADE,
  UNIQUE INDEX ix_transactions_id (id ASC)
);

CREATE TABLE transfers (
  id UUID NOT NULL,
  destination_account_number VARCHAR(255) NULL,
  CONSTRAINT transfers_pkey PRIMARY KEY (id ASC),
  CONSTRAINT transfers_id_fkey FOREIGN KEY (id) REFERENCES transactions(id) ON DELETE CASCADE,
  CONSTRAINT transfers_destination_account_number_fkey FOREIGN KEY (destination_account_number) REFERENCES accounts(account_number) ON DELETE CASCADE
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
sql = []
for user in users:
    account_number = mock_utils.rand_account_no()
    while account_number in accounts:
        account_number = mock_utils.rand_account_no()
    accounts.append(account_number)
    sql.append(
        mock_utils.user_sql(
            user[0], user[1], user[2], user[3], user[4], user[5], user[6]
        )
    )
    sql.append(
        mock_utils.account_sql(
            uuid.uuid4(),
            user[0],
            account_number,
            0,
            user[6]
        )
    )
    # init deposit
    sql.append(
        mock_utils.deposit_sql(
            uuid.uuid4(),
            account_number,
            random.randint(
                100000,
                1000000
            ),
            user[6]
        )
    )
    # rand deposit
    for i in range(random.randint(1, 5)):
        sql.append(
            mock_utils.deposit_sql(
                uuid.uuid4(),
                account_number,
                random.randint(
                    100,
                    1000000
                ),
                mock_utils.rand_transaction_create()
            )
        )
    # rand withdraw
    for i in range(random.randint(1, 5)):
        sql.append(
            mock_utils.withdraw_sql(
                uuid.uuid4(),
                account_number,
                random.randint(
                    100,
                    1000
                ),
                mock_utils.rand_transaction_create()
            )
        )

# Generate random transfers for each account
for account in accounts:
    for i in range(random.randint(2, 10)):
        destination_account_number = account
        while destination_account_number == account:
            destination_account_number = random.choice(accounts)
        sql.append(
            mock_utils.transfer_sql(
                uuid.uuid4(),
                account,
                random.randint(
                    100,
                    10000
                ),
                destination_account_number,
                mock_utils.rand_transaction_create()
            )
        )

# Combine the SQL statements to create the tables and insert the mock data
final_sql = create_sql + "\n".join(sql)

file_path = "preload/mock_monolithic_data.sql"
directory = os.path.dirname(file_path)

if not os.path.exists(directory):
    os.makedirs(directory)

# Write the SQL statements to a file
with open(file_path, "w") as f:
    f.write(final_sql)
