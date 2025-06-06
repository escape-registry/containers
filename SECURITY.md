# SECURITY.md

# Security Policy

## Reporting Security Issues

If you discover a security vulnerability within this project, please send an email to the project maintainers. You can find the contact information in the `README.md` file. Please do not disclose the vulnerability publicly until it has been addressed.

## Pull Request Security

- Pull requests from forks cannot directly access repository secrets. This ensures that malicious code cannot be executed with elevated privileges.
- All contributions must be reviewed before merging to ensure code quality and security.

## Dockerfile Best Practices

- Use minimal base images to reduce the attack surface.
- Avoid running containers as the root user whenever possible.
- Pin versions of dependencies to avoid introducing vulnerabilities through updates.

## Image Scanning

- TODO: integrate a Docker image vulnerability scanner into the CI/CD pipeline to identify and address vulnerabilities in images.

## Code Review

- All pull requests should undergo a thorough review process.

## Metadata Parsing

- Ensure that the metadata extraction scripts are robust against malformed input and do not execute arbitrary code based on label values.