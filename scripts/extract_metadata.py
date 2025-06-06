import os
import re
import json
import sys
from pathlib import Path

# Adapt this to your project's prefix if different
PROJECT_LABEL_PREFIX = "org.escape-registry.recipe."
OCI_LABEL_PREFIX = "org.opencontainers.image."


def extract_dockerfile_labels(dockerfile_path):
    """
    Extracts LABEL instructions from a Dockerfile.
    Handles multi-line labels and different quote styles.
    """
    metadata = {}
    try:
        with open(dockerfile_path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: Dockerfile not found at {dockerfile_path}", file=sys.stderr)
        return metadata  # Returns an empty dictionary if the file is not found

    # Improved regex to capture key=value pairs in LABEL instructions
    # Handles multi-line labels terminated by \ and spaces around =
    # Handles values in double quotes, single quotes, or without quotes
    label_pattern = re.compile(
        r"^\s*LABEL\s+((?:(?:[^\s=]+)\s*=\s*(?:\"((?:\\\"|[^\"])*)\"|\'((?:\\\'|[^\'])*)\'|(?:[^\\\"\'\s][^\"\'\s]*))(?:\s*\\?\s*))+)",
        re.MULTILINE | re.IGNORECASE,
    )

    # Regex to extract individual key=value pairs from a LABEL line
    kv_pattern = re.compile(r"([^\s=]+)\s*=\s*(?:\"((?:\\\"|[^\"])*)\"|\'((?:\\\'[^\'])*)\'|([^\\\"\'\s][^\"\'\s]*))")

    for match in label_pattern.finditer(content):
        labels_block = match.group(1).replace("\\\n", " ").replace("\\\r\n", " ")  # Concatenate continued lines

        for kv_match in kv_pattern.finditer(labels_block):
            key = kv_match.group(1).strip()
            # Prioritize values in double quotes, then single quotes, then without quotes
            val_double_quoted = kv_match.group(2)
            val_single_quoted = kv_match.group(3)
            val_unquoted = kv_match.group(4)

            if val_double_quoted is not None:
                value = val_double_quoted.replace('\\"', '"')
            elif val_single_quoted is not None:
                value = val_single_quoted.replace("\\'", "'")
            else:
                value = val_unquoted

            metadata[key] = value.strip()

    return metadata


def validate_metadata(metadata, dockerfile_path):
    """
    Validates the extracted metadata against requirements.
    Returns a list of error messages.
    """
    required_labels = [
        f"{OCI_LABEL_PREFIX}title",
        f"{OCI_LABEL_PREFIX}description",
        f"{OCI_LABEL_PREFIX}url",
        f"{PROJECT_LABEL_PREFIX}author",
        f"{PROJECT_LABEL_PREFIX}version",
        f"{PROJECT_LABEL_PREFIX}keywords",
    ]

    errors = []

    for label in required_labels:
        if label not in metadata or not metadata[label]:
            errors.append(f"Required label missing or empty: {label}")

    # Specific format validations
    version_label = f"{PROJECT_LABEL_PREFIX}version"
    if version_label in metadata and metadata[version_label]:
        if not re.fullmatch(r"^\d+\.\d+\.\d+$", metadata[version_label]):
            errors.append(f"The version label '{metadata[version_label]}' does not follow the semantic format X.Y.Z.")
        else:
            # Check if the version in the label matches the parent directory name
            dockerfile_p = Path(dockerfile_path)
            expected_version_dir = dockerfile_p.parent.name
            if metadata[version_label] != expected_version_dir:
                errors.append(
                    f"The version label '{PROJECT_LABEL_PREFIX}version' ({metadata[version_label]}) "
                    f"does not match the version directory '{expected_version_dir}'."
                )

    build_args_label = f"{PROJECT_LABEL_PREFIX}build_arguments"
    if build_args_label in metadata and metadata[build_args_label]:
        try:
            json.loads(metadata[build_args_label])
        except json.JSONDecodeError:
            errors.append(f"The label '{build_args_label}' is not valid JSON.")

    exposed_ports_label = f"{PROJECT_LABEL_PREFIX}exposed_ports"
    if exposed_ports_label in metadata and metadata[exposed_ports_label]:
        ports_str = metadata[exposed_ports_label]
        if ports_str:  # Ensure the string is not empty before splitting
            for port in ports_str.split(","):
                if not port.strip().isdigit():
                    errors.append(f"The label '{exposed_ports_label}' contains non-numeric values or incorrect format: '{port.strip()}'.")
                    break

    # Validation of the OCI image URL
    oci_url_label = f"{OCI_LABEL_PREFIX}url"
    if oci_url_label in metadata and metadata[oci_url_label]:
        # Example: https://github.com/your-org/your-repo/tree/main/environments/recipe-name/version
        # Adjust GITHUB_REPOSITORY and GITHUB_REF_NAME if necessary to match your CI
        # For local execution, these environment variables might not be defined.
        repo_url_base = (
            os.environ.get("GITHUB_SERVER_URL", "https://github.com") + "/" + os.environ.get("GITHUB_REPOSITORY", "your-org/your-repo")
        )

        # Derive recipe_name and version_dir from the Dockerfile path
        p = Path(dockerfile_path)  # environments/<recipe_name>/<version>/Dockerfile
        version_dir = p.parent.name
        recipe_name = p.parent.parent.name

        # The default branch is usually 'main' or 'master'
        # GITHUB_REF_NAME is usually 'refs/heads/main', so we extract 'main'
        # For PRs, this might be different, so we might need more robust logic
        # or ask the contributor to define it correctly. For now, we assume 'main'.
        default_branch = os.environ.get("GITHUB_REF_NAME", "refs/heads/main").split("/")[-1]

        expected_url_path = f"/tree/{default_branch}/environments/{recipe_name}/{version_dir}"
        expected_url = f"{repo_url_base}{expected_url_path}"

        if metadata[oci_url_label] != expected_url:
            # Allow some flexibility if the user has provided a valid full URL
            # but don't be too strict if the environment variables are not available
            if "GITHUB_SERVER_URL" in os.environ and "GITHUB_REPOSITORY" in os.environ:
                errors.append(
                    f"The label '{oci_url_label}' ({metadata[oci_url_label]}) "
                    f"does not match the expected URL ({expected_url}). "
                    f"Make sure it points to the correct version directory in the repository."
                )

    return errors


def get_recipe_name_and_version(dockerfile_path_str):
    """
    Extracts the recipe name and version from the Dockerfile path.
    Assumes path format: environments/<recipe_name>/<version>/Dockerfile
    """
    p = Path(dockerfile_path_str)
    # p.parts for 'environments/recipe-name/version/Dockerfile' might be:
    # ('environments', 'recipe-name', 'version', 'Dockerfile')
    # or on Windows: ('environments', 'recipe-name', 'version', 'Dockerfile')
    # We need to handle potential leading slashes or drive letters if the path is absolute
    # by finding the 'environments' part.

    parts = list(p.parts)
    try:
        environments_index = parts.index("environments")
        # Recipe name is the part after 'environments'
        recipe_name = parts[environments_index + 1]
        # Version is the part after recipe_name
        version = parts[environments_index + 2]
        return recipe_name, version
    except (ValueError, IndexError):
        # Handle cases where the path doesn't match the expected structure
        print(f"Warning: Could not derive recipe name and version from path: {dockerfile_path_str}", file=sys.stderr)
        return "unknown", "unknown"


def main():
    if len(sys.argv) < 2:
        print("Usage: extract_metadata.py <dockerfile_path> [output_json_path]", file=sys.stderr)
        sys.exit(1)

    dockerfile_path = sys.argv[1]
    output_json_path = sys.argv[2] if len(sys.argv) > 2 else None

    # Get the GitHub workspace directory from the environment
    github_workspace = os.environ.get("GITHUB_WORKSPACE")
    if not github_workspace:
        print("Error: GITHUB_WORKSPACE environment variable not found.", file=sys.stderr)
        sys.exit(1)

    # Create an absolute path to the Dockerfile relative to the workspace
    abs_dockerfile_path = os.path.join(github_workspace, dockerfile_path)

    if not os.path.exists(abs_dockerfile_path):
        print(f"Error: Dockerfile not found at {abs_dockerfile_path}", file=sys.stderr)
        sys.exit(1)

    # Extract metadata from the Dockerfile
    metadata = extract_dockerfile_labels(abs_dockerfile_path)

    # Validate the extracted metadata
    errors = validate_metadata(metadata, abs_dockerfile_path)
    if errors:
        print("Metadata validation errors for {}:".format(dockerfile_path), file=sys.stderr)
        for error in errors:
            print("- " + error, file=sys.stderr)
        sys.exit(1)

    # Add recipe name and version to metadata
    recipe_name, recipe_version_from_path = get_recipe_name_and_version(dockerfile_path)
    metadata["_recipe_name"] = recipe_name
    metadata["_recipe_version_from_path"] = recipe_version_from_path

    # Ensure all required properties exist
    if "org.opencontainers.image.title" not in metadata:
        metadata["org.opencontainers.image.title"] = "Untitled"
    if "_recipe_name" not in metadata:
        metadata["_recipe_name"] = "unknown"
    if "org.escape-registry.recipe.version" not in metadata:
        metadata["org.escape-registry.recipe.version"] = "0.0.0"

    # Output the metadata as JSON
    if output_json_path:
        try:
            with open(output_json_path, "w", encoding="utf-8") as outfile:
                json.dump(metadata, outfile, indent=2)
            print("Metadata saved to {}".format(output_json_path))
        except Exception as e:
            print("Error writing to {}: {}".format(output_json_path, str(e)), file=sys.stderr)
            sys.exit(1)
    else:
        json.dump(metadata, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
