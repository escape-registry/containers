# ESCAPE Docker Container Recipies

Welcome to the ESCAPE catalogue of Docker Container Recipes! This project aims to provide a centralized collection of Docker container recipes. This repository is designed to facilitate community contributions, automate the building and pushing of Docker images, and provide a web-based interface for browsing available environments.

## Project Goals

- **Recipe Hosting:** Store Dockerfile-based recipes in a structured manner.
- **Community Contributions:** Allow users to propose new recipes or updates via Pull Requests.
- **Automated CI/CD:** Automatically build and push Docker images to a container registry upon merging Pull Requests or pushing to the main branch.
- **Web Interface:** Provide a user-friendly interface for browsing available environments and their descriptions.

## Core Functionalities

- Each recipe is stored in its own directory under `environments/`.
- Dockerfiles contain embedded metadata using `LABEL` instructions.
- A CI/CD pipeline is implemented using GitHub Actions for automated builds and pushes.
- A GitHub Pages site displays a list of available environments, derived from Dockerfile metadata.


## Contribution Guidelines

1. **Fork the Repository:** Create a personal copy of the repository.
2. **Create a New Branch:** Develop your changes in a new branch.
3. **Add Your Recipe:** Create a new directory under `environments/` with a Dockerfile and optional README.md.
4. **Submit a Pull Request:** Open a PR targeting the main branch with a clear description of your changes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

## Security

For information on security practices and how to contribute securely, please refer to the SECURITY.md file.

Thank you for your interest in contributing to the Docker Recipes Repository! We look forward to your contributions.