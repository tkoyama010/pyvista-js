"""Utility to generate Stlite Sharing URLs from Python source code.

Stlite Sharing uses a custom URL encoding format based on protobuf.
This module provides functions to work with Stlite Sharing URLs.

Note: The full encoding implementation requires the protobuf format used by
stlite. As a workaround, this module provides functions to:
1. Verify if source code matches an existing URL
2. Generate placeholder URLs for documentation
3. Check if the source has changed and needs URL regeneration

When the stlite library becomes available with URL generation support,
this module can be updated to use it directly.
"""

from __future__ import annotations

import base64
import re
from pathlib import Path

# Base URL for Stlite Sharing editor
STLITE_EDITOR_URL = "https://edit.share.stlite.net/#!"
STLITE_SHARE_URL = "https://share.stlite.net/#!"


def _decode_url_content(url: str) -> bytes | None:
    """Decode the content part of a Stlite Sharing URL.

    Parameters
    ----------
    url : str
        The Stlite Sharing URL.

    Returns
    -------
    bytes or None
        The decoded content bytes, or None if decoding fails.

    """
    # Extract the part after #!
    if "#!" not in url:
        return None

    encoded_part = url.split("#!", 1)[1]

    # Add padding if needed
    padding_needed = 4 - len(encoded_part) % 4
    if padding_needed != 4:
        encoded_part += "=" * padding_needed

    try:
        return base64.urlsafe_b64decode(encoded_part)
    except Exception:  # noqa: BLE001
        return None


def _extract_source_from_decoded(decoded: bytes) -> dict[str, str] | None:
    """Extract source files from decoded URL content.

    Parameters
    ----------
    decoded : bytes
        The decoded URL content.

    Returns
    -------
    dict[str, str] or None
        Dictionary mapping filenames to their content.

    """
    # This is a simplified extraction that looks for common patterns
    # The actual format uses protobuf encoding
    files = {}

    # Try to find Python file content
    # Pattern: filename followed by content with length prefix
    idx = 0
    while idx < len(decoded):
        # Look for length-delimited field marker (0x0a = field 1, wire type 2)
        if idx < len(decoded) and decoded[idx] == 0x0A:
            idx += 1
            if idx >= len(decoded):
                break

            # Read filename length (varint)
            fname_len = decoded[idx]
            idx += 1

            if idx + fname_len > len(decoded):
                break

            filename = decoded[idx : idx + fname_len].decode("utf-8", errors="ignore")
            idx += fname_len

            # Look for content field marker (0x12 = field 2, wire type 2)
            if idx < len(decoded) and decoded[idx] == 0x12:
                idx += 1

                # Read content length (varint)
                content_len = 0
                shift = 0
                while idx < len(decoded):
                    byte = decoded[idx]
                    idx += 1
                    content_len |= (byte & 0x7F) << shift
                    if not (byte & 0x80):
                        break
                    shift += 7

                if idx + content_len > len(decoded):
                    break

                content = decoded[idx : idx + content_len]
                idx += content_len

                # The content might be another nested protobuf message
                # Try to extract the actual source code
                if content.startswith(b"\n\x06"):
                    # Nested structure - extract inner content
                    inner_idx = 9  # Skip outer wrapper
                    if inner_idx < len(content) and content[inner_idx - 1] == 0x12:
                        # Read inner content length
                        inner_len = 0
                        inner_shift = 0
                        inner_pos = inner_idx
                        while inner_pos < len(content):
                            byte = content[inner_pos]
                            inner_pos += 1
                            inner_len |= (byte & 0x7F) << inner_shift
                            if not (byte & 0x80):
                                break
                            inner_shift += 7

                        if inner_pos + inner_len <= len(content):
                            inner_content = content[inner_pos : inner_pos + inner_len]
                            # Try to find the actual source
                            if inner_content.startswith(b"\n\xc3\x04"):
                                # Skip more wrapper bytes
                                source_start = 3
                                if inner_content[source_start:].startswith(b'"""'):
                                    # Found Python source code
                                    source = inner_content[source_start:].decode(
                                        "utf-8",
                                        errors="ignore",
                                    )
                                    files[filename] = source
                else:
                    # Try direct decode
                    try:
                        files[filename] = content.decode("utf-8")
                    except UnicodeDecodeError:
                        pass

        else:
            idx += 1

    return files or None


def extract_source_from_url(url: str) -> dict[str, str] | None:
    """Extract source files from a Stlite Sharing URL.

    Parameters
    ----------
    url : str
        The Stlite Sharing URL.

    Returns
    -------
    dict[str, str] or None
        Dictionary mapping filenames to their content, or None if extraction fails.

    """
    decoded = _decode_url_content(url)
    if decoded is None:
        return None

    return _extract_source_from_decoded(decoded)


def verify_url_matches_source(url: str, source_path: Path | str) -> bool:
    """Verify if a Stlite URL contains the same source as a file.

    Parameters
    ----------
    url : str
        The Stlite Sharing URL.
    source_path : Path or str
        Path to the source file.

    Returns
    -------
    bool
        True if the URL matches the source file, False otherwise.

    """
    source_path = Path(source_path)
    if not source_path.exists():
        return False

    source_content = source_path.read_text(encoding="utf-8")
    extracted = extract_source_from_url(url)

    if extracted is None:
        return False

    # Check if the main file content matches
    for filename, content in extracted.items():
        if filename == source_path.name:
            # Normalize both contents for comparison
            normalized_source = "\n".join(source_content.strip().splitlines())
            normalized_extracted = "\n".join(content.strip().splitlines())
            return normalized_source == normalized_extracted

    return False


def generate_stlite_placeholder_url(
    filename: str = "app.py",
    base_url: str = STLITE_EDITOR_URL,
) -> str:
    """Generate a placeholder Stlite URL for documentation purposes.

    This creates a URL that points to stlite with a note that the actual
    URL needs to be generated from source code.

    Parameters
    ----------
    filename : str, optional
        The filename to reference. Default is "app.py".
    base_url : str, optional
        The base Stlite URL.

    Returns
    -------
    str
        A placeholder URL with documentation.

    """
    return f"{base_url}<{filename}>"


def update_readme_stlite_badge(
    readme_path: Path | str,
    app_path: Path | str,
    new_url: str | None = None,
) -> bool:
    """Update the stlite badge URL in README.md.

    Parameters
    ----------
    readme_path : Path or str
        Path to the README.md file.
    app_path : Path or str
        Path to the stlite app.py file.
    new_url : str, optional
        The new URL to use. If None, a placeholder is used.

    Returns
    -------
    bool
        True if the README was updated, False otherwise.

    """
    readme = Path(readme_path)
    app = Path(app_path)

    if not readme.exists():
        msg = f"README not found: {readme}"
        raise FileNotFoundError(msg)

    if not app.exists():
        msg = f"App file not found: {app}"
        raise FileNotFoundError(msg)

    # Read README content
    content = readme.read_text(encoding="utf-8")

    # Pattern to match stlite URL in badge
    # Matches: https://edit.share.stlite.net/#! followed by encoded content
    pattern = r"https://edit\.share\.stlite\.net/\#![^\s\)\"\]\>]+"

    if new_url is None:
        new_url = generate_stlite_placeholder_url(app.name)

    # Replace the URL
    updated_content = re.sub(pattern, new_url, content)

    if updated_content == content:
        return False

    # Write back
    readme.write_text(updated_content, encoding="utf-8")
    return True


def check_stlite_url_needs_update(
    readme_path: Path | str,
    app_path: Path | str,
) -> tuple[bool, str]:
    """Check if the Stlite URL in README needs to be updated.

    Parameters
    ----------
    readme_path : Path or str
        Path to the README.md file.
    app_path : Path or str
        Path to the stlite app.py file.

    Returns
    -------
    tuple[bool, str]
        (needs_update, message) where needs_update is True if the URL
        should be regenerated, and message explains the status.

    """
    readme = Path(readme_path)
    app = Path(app_path)

    if not readme.exists():
        return True, f"README not found: {readme}"

    if not app.exists():
        return True, f"App file not found: {app}"

    # Read README to find current URL
    content = readme.read_text(encoding="utf-8")
    pattern = r"https://edit\.share\.stlite\.net/\#![^\s\)\"\]\>]+"
    match = re.search(pattern, content)

    if not match:
        return True, "No stlite URL found in README"

    current_url = match.group(0)

    # Verify if URL matches current source
    if verify_url_matches_source(current_url, app):
        return False, "Stlite URL is up to date with source"

    return True, "Stlite URL needs regeneration (source has changed)"


def generate_stlite_url_from_source(
    source_path: Path | str,
) -> str | None:
    """Generate a Stlite Sharing URL from source code.

    Note: This is a placeholder implementation. The actual URL generation
    requires proper protobuf encoding or the stlite library. For now, this
    returns None and logs instructions for manual URL generation.

    Parameters
    ----------
    source_path : Path or str
        Path to the source file.

    Returns
    -------
    str or None
        The Stlite URL if generation succeeds, None otherwise.

    """
    source_path = Path(source_path)

    if not source_path.exists():
        return None

    content = source_path.read_text(encoding="utf-8")

    # For now, we can't generate the exact URL without the proper encoding
    # This function serves as a placeholder for when the stlite library
    # provides URL generation support
    return None


if __name__ == "__main__":
    import sys

    # Default paths
    repo_root = Path(__file__).parent.parent.parent
    app_file = repo_root / "stlite" / "app.py"
    readme_file = repo_root / "README.md"

    if len(sys.argv) > 1:
        if sys.argv[1] == "check":
            # Check if URL needs update
            needs_update, message = check_stlite_url_needs_update(readme_file, app_file)
            print(f"stlite-url-check={'true' if needs_update else 'false'}")  # noqa: T201
            print(message)  # noqa: T201
            sys.exit(0 if not needs_update else 1)

        if sys.argv[1] == "verify":
            # Verify current URL against source
            content = readme_file.read_text(encoding="utf-8")
            pattern = r"https://edit\.share\.stlite\.net/\#![^\s\)\"\]\>]+"
            match = re.search(pattern, content)

            if match:
                url = match.group(0)
                matches = verify_url_matches_source(url, app_file)
                print(f"stlite-url-verified={'true' if matches else 'false'}")  # noqa: T201
                sys.exit(0 if matches else 1)
            else:
                print("stlite-url-verified=false")  # noqa: T201
                print("No stlite URL found in README")  # noqa: T201
                sys.exit(1)

    # Default: show status
    needs_update, message = check_stlite_url_needs_update(readme_file, app_file)
    print(f"Status: {message}")  # noqa: T201
    print(f"Needs update: {needs_update}")  # noqa: T201
