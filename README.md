# ATM-API
[![CircleCI](https://circleci.com/gh/RyanSept/atm-api/tree/develop.svg?style=svg)](https://circleci.com/gh/RyanSept/atm-api/tree/develop)
[![codecov](https://codecov.io/gh/RyanSept/atm-api/branch/develop/graph/badge.svg)](https://codecov.io/gh/RyanSept/atm-api)

This is a Bank ATM api. It is available at https://atm2.herokuapp.com/

## Built with
Flask-restful, SQLAlchemy

## Installation
Once you've cloned the repo from `git@github.com:RyanSept/atm-api.git`

Change directory into the project `$ cd atm-api`

Install dependencies `$ pip install -r requirements.txt`

Create a [.env](#setting-up-the-configs) file based on the `.env-sample` which is inside the project.

To run the app, navigate to the project folder and run `$ python manage.py runserver`

You can access the app at `http://127.0.0.1:5000`

### Setting up the configs
The application has 3 different configuration modes: `dev`, `staging` and `prod`. The flag `STAGE`, an environment variable,
is used to determine which config class is loaded into the app (see config.py). You also need to set up a .env file
for the apps secret variables.

`$ export STAGE=dev`

`$ cat .env-sample > .env # make necessary edits`
    - [$DATABASE_URI](#database-setup)

`$ source .env`

### Database setup
The application uses a Postgres database. To setup the database run the following commands.

`$ createdb atm_api` (You should have this if you've installed psql, the Postgres client)

You can then fill out the `DATABASE_URI` variable in your .env file with your database uri connection string.

Run `$ python manage.py init_app` to create tables on the database.


### Generating a secure encryption key for the application
To generate an encryption key for the `SECRET_KEY` app cofig run `$ python manage.py generate_secret_key`

# Documentation

### Account login

You can authenticate a user and receive a JSON Web Token using this method. This token expires according to the secret config variable
`JWT_TOKEN_EXPIRY`.

```
*Sample request*
POST /accounts/login
Accept: application/json
{
    "account_number": "1234567890",
    "pin": 2345
}
```

```
*Sample response*
HTTP/1.1 200 OK
Vary: Accept
Content-Type: application/json
{
    "token": "eyJ0eXAiOiJKVasf9y83uhajGIafsiVFjiadh1NiJ9afospujfas.afsiha9e732k3laflmao"
}

```

Request Arguments

    Body:

        account_number <required><string>: User bank account number

        pin <required><int>: Account pin

---

### Account creation

You can create a new account for purposes of testing.

```
*Sample request*
POST /accounts/create
Accept: application/json
{
    "account_number": "1234567890",
    "pin": "2345",
    "first_name": "John",
    "last_name": "Doe",
    "opening_balance": 100000
}
```

```
*Sample response*
HTTP/1.1 201 OK
Vary: Accept
Content-Type: application/json
{
    "message": "Account was created."
}

```

Request Arguments

    Body:

        account_number <required><string>: User bank account number

        pin <required><int>: Account pin

        first_name <required><string>

        last_name <required><string>

        opening_balance <required><int>: Opening balance for account

---

### Account balance

You can retrieve the balance for an account.

```
*Sample request*
GET /accounts/balance
Accept: application/json
```

```
*Sample response*
HTTP/1.1 200 OK
Vary: Accept
Content-Type: application/json
{
    "balance": 100000,
    "account_number": "1234567890"
}
```
---

### Account deposit

Making a deposit.

```
*Sample request*
POST /accounts/balance
Accept: application/json
{
    "deposit_amount": 10000
}
```

```
*Sample response*
HTTP/1.1 201 OK
Vary: Accept
Content-Type: application/json
{
    "message": "Deposited 10000 successfully.",
    "new_balance": 110000
}

```

Request Arguments

    Body:

        deposit_amount <required><int>: Amount to deposit into account

---

### Account withdrawal

Making a withdrawal from an account.

```
*Sample request*
POST /accounts/withdraw
Accept: application/json
{
    "withdrawal_amount": 10000
}
```

```
*Sample response*
HTTP/1.1 201 OK
Vary: Accept
Content-Type: application/json
{
    "message": "Withdrew 10000 successfully.",
    "new_balance": 90000
}

```

Request Arguments

    Body:

        withdrawal_amount <required><int>: Amount to withdraw from account

---

## Deploying and Management
Create an app on heroku `$ heroku apps:create <app_name>` and set secret config variables through the heroku dashboard.

`$ git push heroku <current_branch>:master` to push the app to heroku. (Remember to initialize the db!)


## Unit Tests
To run the application's unit tests, simply run `$ nosetests`

To run a specific test run eg. the register endpoint test run:

`$ nosetests api.v1.tests.test_register:RegisterTestSuite.test_creates_account`

To run a specific test suite eg. the deposit test suite, run:

`$ nosetests api.v1.tests.test_deposit`

To check test coverage `$ nosetests --with-coverage --cover-package=api`
