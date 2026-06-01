"""Simple greeting module."""


def greet(name: str) -> None:
    """Print a greeting message for the given name.

    Args:
        name: The name to greet.
    """
    message = f"Hello, {name}"
    print(message)


if __name__ == "__main__":
    greet("Claude")