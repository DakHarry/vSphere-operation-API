from fastapi import APIRouter
from src.router import vm

router = APIRouter()
router.include_router(vm.router, prefix="/vm")