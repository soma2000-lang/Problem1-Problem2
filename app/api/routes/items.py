import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select
