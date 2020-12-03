"""
Upload file parameters
"""
class UploadParams:
    def __init__(self, vm_name, vm_user, vm_pwd, path_inside_vm, path_from_local):
        self.vm_name = vm_name
        self.vm_user = vm_user
        self.vm_pwd = vm_pwd
        self.path_inside_vm = path_inside_vm
        self.path_from_local = path_from_local
