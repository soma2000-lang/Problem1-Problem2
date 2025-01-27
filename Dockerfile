
FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED 1



WORKDIR /app


RUN powershell -Command "Invoke-WebRequest -Uri https://install.python-poetry.org -OutFile install-poetry.py" && \
    python install-poetry.py --version 1.7.1 && \
    setx /M PATH "%PATH%;%USERPROFILE%\.local\bin"

# Configure Poetry
RUN poetry config virtualenvs.create false

# Copy project files
COPY pyproject.toml poetry.lock* /app/

# Install dependencies
ARG INSTALL_DEV=false
RUN if "%INSTALL_DEV%"=="true" ( \
        poetry install --no-root \
    ) else ( \
        poetry install --no-root --only main \
    )

# Set Python path
ENV PYTHONPATH=C:\app

# Copy application files
COPY scripts/ /app/scripts/
COPY prestart.sh /app/
COPY tests-start.sh /app/
COPY app /app/app

# Optional: Use PowerShell as default shell
SHELL ["powershell", "-Command"]