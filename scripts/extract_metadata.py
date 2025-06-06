import sys
import os
import re
import json
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

    if errors:
        error_message = f"Metadata validation errors for {dockerfile_path}:\n" + "\n".join(f"- {e}" for e in errors)
        raise ValueError(error_message)

    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_metadata.py <path_to_dockerfile> [output_path_for_json]", file=sys.stderr)
        sys.exit(1)

    dockerfile_path_arg = sys.argv[1]

    try:
        print(f"Processing Dockerfile: {dockerfile_path_arg}", file=sys.stderr)
        extracted_data = extract_dockerfile_labels(dockerfile_path_arg)
        if not extracted_data:
            print(f"No LABEL metadata found in {dockerfile_path_arg}", file=sys.stderr)
            # Decide whether to exit with an error if no labels are found,
            # or if it's acceptable and validation will fail anyway.
            # For now, we let validation handle this.

        validate_metadata(extracted_data, dockerfile_path_arg)

        # Add additional information to the JSON if needed
        p = Path(dockerfile_path_arg)
        extracted_data["_metadata_source_path"] = str(p.relative_to(Path.cwd()))  # Relative path
        extracted_data["_recipe_name"] = p.parent.parent.name
        extracted_data["_recipe_version_from_path"] = p.parent.name

        if len(sys.argv) > 2:
            output_path = sys.argv[2]
            with open(output_path, "w", encoding="utf-8") as out_f:
                json.dump(extracted_data, out_f, indent=2, ensure_ascii=False)
            print(f"Extracted metadata and saved to {output_path}", file=sys.stderr)
        else:
            print(json.dumps(extracted_data, indent=2, ensure_ascii=False))

    except ValueError as ve:  # Specific validation errors
        print(f"{ve}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error processing Dockerfile {dockerfile_path_arg}: {e}", file=sys.stderr)
        sys.exit(2)  # Different exit code for general errors
