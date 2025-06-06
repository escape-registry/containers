# Python Data Science Environment

This environment provides a pre-configured Docker container for data science workflows using Python 3.10.

## Usage

To use this environment, ensure you have Docker installed. Then, navigate to the root of this repository and run the following command:

```bash
docker build -t python-datascience:latest -f environments/python-datascience/v1.0.0/Dockerfile .
docker run -it --rm -p 8888:8888 python-datascience:latest
```

This will build the Docker image and start a container with Jupyter Lab running. You can then access Jupyter Lab in your browser at `http://localhost:8888`.

## Included Packages

The following Python packages are pre-installed in this environment:

*   pandas
*   numpy
*   scikit-learn
*   matplotlib
*   jupyterlab


## Dockerfile

The `Dockerfile` for this environment are located at [environments/python-datascience/](environments/python-datascience/). It contains detailed instructions on how the environment is built and configured.  The image is tagged with metadata labels for discoverability and management.

## License

This environment is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.