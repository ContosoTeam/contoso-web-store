FROM python:3.9-slim

# VULNERABILITY: Running as root
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# VULNERABILITY: Exposing env vars in Dockerfile
ENV DATABASE_URL=postgresql://admin_user:P@ssw0rd!2024_prod@contoso-prod-db.postgres.database.azure.com:5432/contoso_store
ENV STRIPE_SECRET_KEY=stripe_live_key_rk7Xp2nQ9wLmT4vB8cYhJ1dF6gA3sK0eU5iO7zN
ENV FLASK_ENV=development
ENV DEBUG=True

EXPOSE 5000

CMD ["python", "app.py"]
