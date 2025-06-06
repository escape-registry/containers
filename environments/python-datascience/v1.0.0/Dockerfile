# syntax=docker/dockerfile:1.4
FROM python:3.10-slim-buster

# Required Metadata Labels
LABEL org.opencontainers.image.title="Python 3.10 Data Science Environment"
LABEL org.opencontainers.image.description="A Docker environment pre-configured with Python 3.10, Jupyter Lab, Pandas, NumPy, Scikit-learn, and Matplotlib for data science workflows."
LABEL org.opencontainers.image.url="https://github.com/escape-registry/containers/tree/main/environments/python-datascience"
LABEL org.escape-registry.recipe.author="Thomas Vuillaume (vuillaut)"
LABEL org.escape-registry.recipe.version="1.0.0"
LABEL org.escape-registry.recipe.keywords="python,datascience,jupyter,pandas,numpy,scikit-learn"

# Optional Metadata Labels
LABEL org.opencontainers.image.source="https://github.com/escape-registry/containers"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.escape-registry.recipe.build_arguments='{"JUPYTER_LAB_VERSION": "4.1"}'
LABEL org.escape-registry.recipe.exposed_ports="8888"
LABEL org.escape-registry.recipe.documentation="https://github.com/escape-registry/containers/blob/main/environments/python-datascience/README.md"

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt \
    && pip install jupyterlab=="${JUPYTER_LAB_VERSION}"

    
# Expose the default Jupyter Lab port
EXPOSE 8888

CMD ["jupyter", "lab", "--port=8888", "--no-browser", "--ip=0.0.0.0", "--allow-root"]