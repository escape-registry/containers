## Description

Please include a summary of the changes and the issue being resolved. Please also include relevant motivation and context. List any dependencies that are required for this change.

Fixes # (issue)

## Type of change

Please delete options that are not relevant.

- [ ] Bug fix (non-disruptive change that fixes an issue)
- [ ] New feature/recipe (non-disruptive change that adds functionality)
- [ ] Breaking change (fix or feature that would cause a change in behavior of an existing functionality)
- [ ] Documentation update
- [ ] Maintenance/Refactoring

## How has this been tested?

Please describe the tests that you ran to verify your changes. Provide instructions so we can reproduce. Please also list any relevant details for your test configuration.

- [ ] Test A
- [ ] Test B

**Test configuration**:
* Docker version:
* Operating system:
* Other notes:

## Contributor checklist:

Before submitting, please check the following points.
Thank you for your contribution!

- [ ] I have read and understand the [Contribution Guidelines](LINK_TO_CONTRIBUTING_GUIDELINES.md) (Create this file if necessary).
- [ ] My code follows the style standards of this project.
- [ ] I have performed a self-assessment of my own code.
- [ ] I have commented on my code, especially in hard-to-understand areas.
- [ ] I have made corresponding changes to the documentation (if applicable).
- [ ] My changes do not generate any new warnings.
- [ ] I have added tests that prove that my fix is effective or that my feature works (if applicable).
- [ ] New and existing unit tests pass locally with my changes (if applicable).
- [ ] All required metadata (`LABEL`) is included and correct in my `Dockerfile`(s).
  - [ ] `org.opencontainers.image.title`
  - [ ] `org.opencontainers.image.description`
  - [ ] `org.opencontainers.image.url` (points to the recipe directory in this repository)
  - [ ] `org.yourproject.recipe.author`
  - [ ] `org.yourproject.recipe.version` (semantic version of the recipe, e.g., 1.0.0)
  - [ ] `org.yourproject.recipe.keywords`
- [ ] The `Dockerfile` is placed in the correct directory structure: `environments/<recipe-name>/<recipe-version>/Dockerfile`.
- [ ] A `README.md` (optional but recommended) has been added or updated for the recipe in `environments/<recipe-name>/README.md`.

## For maintainers (after merging):

- [ ] Verify that the image was built correctly and pushed to the registry.
- [ ] Verify that the GitHub Pages data has been updated.