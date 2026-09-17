FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN useradd --create-home --uid 10001 opspulse
WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY opspulse ./opspulse
RUN pip install --no-cache-dir .

USER opspulse
ENTRYPOINT ["opspulse"]
CMD ["--help"]

