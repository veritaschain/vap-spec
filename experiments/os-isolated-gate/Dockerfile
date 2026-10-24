FROM python:3.12-slim@sha256:a0f57064cbdcd6285fa45f51237ab0b35ea8ebaed06a1f5973e89e19dfb86704
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app/experiments/os-isolated-gate
WORKDIR /app/experiments/os-isolated-gate
COPY experiments/declared-scope-verifier/requirements.txt /app/experiments/declared-scope-verifier/requirements.txt
RUN python -m pip install --no-cache-dir -r /app/experiments/declared-scope-verifier/requirements.txt
COPY experiments/declared-scope-verifier/scope_verifier /app/experiments/declared-scope-verifier/scope_verifier
COPY experiments/pre-record-gate/record_gate /app/experiments/pre-record-gate/record_gate
COPY experiments/os-isolated-gate/isolation_lab /app/experiments/os-isolated-gate/isolation_lab
ENTRYPOINT ["python", "-m", "isolation_lab"]
