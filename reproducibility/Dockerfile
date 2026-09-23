# Minimal image for archival ANALYSIS reproduction (no GPU needed).
FROM python:3.13-slim

ENV MPLBACKEND=Agg \
    PYTHONIOENCODING=utf-8 \
    PIP_NO_CACHE_DIR=1

WORKDIR /repro
COPY requirements.txt /repro/requirements.txt

# Analysis-only reproduction needs numpy+scipy+matplotlib+pandas; torch/SB3/gymnasium
# are required only for simulation/retraining and can be commented out for a lean image.
RUN pip install numpy==2.1.1 scipy==1.15.2 matplotlib==3.10.1 pandas==2.2.3 pytest PyYAML

COPY . /repro

# Default: validate artifacts, reproduce analysis, and run the release gates.
CMD ["bash", "-lc", "python scripts/validate_artifacts.py && python scripts/reproduce_analysis.py && python -m pytest tests -q"]
