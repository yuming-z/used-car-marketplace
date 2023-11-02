# Used Car Marketplace Web Application

## Prerequisites

- [Python](https://www.python.org/downloads/) 3.8 or higher
- [PostgreSQL](https://www.postgresql.org/download/) 13.4 or higher

## Dependencies

- [Django](https://pypi.org/project/Django/) 4.2.5
- [django-environ](https://pypi.org/project/django-environ/) 0.11.2
- [psycopg](https://pypi.org/project/psycopg/) 3.1.12
- [six](https://pypi.org/project/six/) 1.16.0
- [crispy-bootstrap4](https://pypi.org/project/crispy-bootstrap4/) 2023.1

## How to run the application

### Step 1: Environment Setup

Create a new environment file `.env` in the root directory of the project and copy the contents from ['.env.example'](.env.example).

Then, fill in the environment variables in the `.env` file.

The program can be executed in either of the environments:

1. In the local environment.
2. In containers.

#### Local environment

> **Note:** You need to create your own database in PostgreSQL before running the program in the local environment.

It is strongly recommended to use **virtual environment** to run the program in the local environment.

To create a virtual environment, run the following command:

MacOS/Linux:

```bash
python3 -m venv venv
```

Windows:

```powershell
py -m venv venv
```

To activate the virtual environment, run the following command:

MacOS/Linux:

```bash
source venv/bin/activate
```

Windows:

```powershell
.\venv\Scripts\activate
```

To deactivate the virtual environment, run the following command:

```bash
deactivate # the same for both MacOS/Linux and Windows
```

#### Containers

To run the program in containers, you need to install [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/).

Run the following command to set up the environment:

```bash
docker-compose up --build --no-deps --force-recreate
```

### Step 2: Install Dependencies

To install dependencies, run the following command:

```bash
pip install -r requirements.txt
```

> **Note:** If you are using containers, you do not need to install dependencies as the dependencies are already installed during [set-up process](#containers).

### Step 3: Run the Application

#### Local environment

To run the application, run the following command:

```bash
python manage.py makemigrations marketplace_app
python manage.py migrate
python manage.py runserver
```

#### Containers

When you run the containers, the application will be automatically started.

To apply database migrations, run the following command to access the command line interface:

```bash
docker-compose exec web bash
```

Then run the following command to apply database migrations:

```bash
python manage.py makemigrations marketplace_app
python manage.py migrate
```

## Load initial dummy data

To load the initial dummy data, run the following command at the command line interface:

```bash
python manage.py loaddata car_brand
python manage.py loaddata car_model
python manage.py loaddata fuel_type
python manage.py loaddata transmission
python manage.py loaddata car
```