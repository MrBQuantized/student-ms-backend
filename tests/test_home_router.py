from pathlib import Path

import pytest
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from routers.pages import home_router


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
