"""
 /api/vm
"""
from fastapi import APIRouter
from pydantic import BaseModel

from src.models.upload_file_to_vm import upload_file
from src.models.execute_program_in_vm import execute_program

"""
 vCenter login info
"""
class VCenter(BaseModel):
    host: str
    username: str
    userpassword: str

"""
 Upload file parameters
"""
class UploadFileParams(BaseModel):
    vm_name: str
    vm_user: str
    vm_pwd: str
    path_inside_vm: str
    path_from_local: str

"""
 Run script parameters
"""
class RunScriptParams(BaseModel):
    vm_name: str
    vm_user: str
    vm_pwd: str
    path_to_program: str

router = APIRouter()

@router.post("/upload-file")
async def upload_file_in_vm(host: VCenter, params: UploadFileParams):
    return upload_file(host, params)

@router.post("/run-program")
async def run_program(host: VCenter, params: RunScriptParams):
    return execute_program(host, params)
