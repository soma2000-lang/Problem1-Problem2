# FastAPI Project - Development
So since both the problem statements 1 and 2  with visual inspection , thats why all the code for the visual inspection so all those code has been written in the this repository , I have  writtten docstrings so which class model or function deals with problem statement 1 or problem statement 2


## Requirements

* [Docker](https://www.docker.com/).
* [Poetry](https://python-poetry.org/) for Python package and environment management.



The tech stack used
## Technology Stack and Features

- 
    - 🧰 [SQLModel](https://sqlmodel.tiangolo.com) for the Python SQL database interactions (ORM).
    - 🔍 [Pydantic](https://docs.pydantic.dev), used by FastAPI, for the data validation and settings management.
    - 💾 [PostgreSQL](https://www.postgresql.org) as the SQL database.
     🐋 [Docker](https://www.docker.com) for development and production.
    - 🔒 Secure password hashing by default.
    - 🔑 JWT (JSON Web Token) authentication.
    - 📫 Email based password recovery.

Performm all the features as aked in the problem statement.



The folder structure looks like this-
T![alt text](image.png)


## Project Structure 📁
```
PROBLEM3/
PROBLEM3/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── __init__.py 
│   │       ├── items.py ## all the api end points have been done here
│   │       └── utils.py
                 main.py # where the routing has been finallly done
│   ├── __init__.py
│   ├── deps.py # Database Session Management,OAuth2 Setup,Current User Authentication,Superuser Check, superuser privileges
│   ├── main.py
│   └── core/
│       ├── config.py #CORS (Cross-Origin Resource Sharing) Configuration,Handles CORS origins ,Validates URLs for CORS
│       ├── db.py # initializes the DB
│       └── security.py # getting the password hash,veryfying the password and getting the algorithm via"HS256" algo
├── tests/
│   ├── api/
│   ├── crud/
│   ├── scripts/    #trying to write the tests of all the features that have been implemented
│   ├── utils/
│   ├── __init__.py
│   └── conftest.py
├── __init__.py
├── backend_pre_start.py # initializing  the DB with logging
├── crud.py - ## all the functions for achieving the crud features has been written here
├── health.py # t0 check the health of the DB
├── initial_data.py # creating initial data
├── main.py # starting point of the app
├── models.py ##  all the pydantic Base models have been implemented here
├── tests_pre_start.py # starting of the tests
├── utils.py
├── scripts/
├── .dockerignore # files to be ignored by Docker
├── .gitignore # the files to be ignored by git
├── Dockerfile # for containerisation
├── image.png
├── prestart.sh
├── pyproject.toml #python dependencies
├── README.md
├── README.MD
└── tests-start.sh



* Now we can open wer browser and interact with these URLs:

Frontend, built with Docker, with routes handled based on the path: http://localhost:5173

Backend, JSON based web API based on OpenAPI: http://localhost:8000

Automatic interactive documentation with Swagger UI (from the OpenAPI backend): http://localhost:8000/docs

Adminer, database web administration: http://localhost:8080





And then we can run the local development server for the backend:

```bash

fastapi dev app/main.py
```



## The .env file

The `.env` file is the one that contains all wer configurations, generated keys and passwords, etc.

Depending on wer workflow, we could want to exclude it from Git, for example if wer project is public. In that case, we would have to make sure to set up a way for wer CI tools to obtain it while building or deploying wer project.

One way to do it could be to add each environment variable to wer CI/CD system, and updating the `docker-compose.yml` file to read that specific env var instead of reading the `.env` file.

## Pre-commits and code linting

we are using a tool called [pre-commit](https://pre-commit.com/) for code linting and formatting.

When we install it, it runs right before making a commit in git. This way it ensures that the code is consistent and formatted even before it is committed.

we can find a file `.pre-commit-config.yaml` with configurations at the root of the project.

#### Install pre-commit to run automatically

`pre-commit` is already part of the dependencies of the project, but we could also install it globally if we prefer to, following [the official pre-commit docs](https://pre-commit.com/).

After having the `pre-commit` tool installed and available, we need to "install" it in the local repository, so that it runs automatically before each commit.

Using `uv`, we could do it with:

```bash
❯ uv run pre-commit install
pre-commit installed at .git/hooks/pre-commit
```

Now whenever we try to commit, e.g. with:

```bash
git commit
```

...pre-commit will run and check and format the code we are about to commit, and will ask we to add that code (stage it) with git again before committing.

Then we can `git add` the modified/fixed files again and now we can commit.

#### Running pre-commit hooks manually

we can also run `pre-commit` manually on all the files, we can do it using `uv` with:

```bash
❯ uv run pre-commit run --all-files
check for added large files..............................................Passed
check toml...............................................................Passed
check yaml...............................................................Passed
ruff.....................................................................Passed
ruff-format..............................................................Passed
eslint...................................................................Passed
prettier.................................................................Passed

## Pre-commits and code linting

### Development URLs

Development URLs, for local development.

Backend: http://localhost:8000

Automatic Interactive Docs (Swagger UI): http://localhost:8000/docs

# Extra Features implemented

1. For linting ruff has been used
2. Necessary test unit tests have been added -(more to be added and improved)
3. A Sentry SDK is used to automatically capture and report errors, exceptions, and other events happening within an application
4. Efficient use of middleware
5. In case of uploaded image size is more than efficient handling of that case using io
7. Usage of Starlette (Asynchronous Server Gateway Interface) 
8. Efficient security measures



### Scope of Improvement 
The tests writing are still under progress and have not been fully implemened for all the features due to time constaints
