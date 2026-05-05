FROM python:3.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install dependencies using uv
COPY apps/atoms/drone_management/pyproject.toml ./
RUN uv pip install --system .

# Copy app code
COPY apps/atoms/drone_management/ .
COPY apps/shared/ /app/shared/

CMD ["python", "main.py"]
