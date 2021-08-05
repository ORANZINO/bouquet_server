# ------------------------------------------------------------------------------
# Base image
# ------------------------------------------------------------------------------
FROM python:3.8-slim AS base

# ------------------------------------------------------------------------------
# Install dependencies
# ------------------------------------------------------------------------------
FROM base AS deps
COPY requirements.txt ./
RUN apt update > /dev/null && \ 
        apt install -y build-essential && \
        pip install --disable-pip-version-check -r requirements.txt && \
	pip install --disable-pip-version-check torch torchvision torchaudio -f https://download.pytorch.org/whl/lts/1.8/torch_lts.html

# ------------------------------------------------------------------------------
# Final image
# ------------------------------------------------------------------------------
FROM deps
WORKDIR /usr/src/app
COPY . /usr/src/app

EXPOSE 80

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]

