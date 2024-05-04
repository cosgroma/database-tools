__version__ = "0.0.0"

from dotenv import load_dotenv

from .core import compute

load_dotenv()  # take environment variables

__all__ = [
    "compute",
]
