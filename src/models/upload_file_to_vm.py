import atexit
import requests
import re
import ssl

from pyVim import connect
from pyVmomi import vim, vmodl
from src.classes.vcenter import VCenter
from src.classes.upload_params import UploadParams
from src.helper.filter_helper import collect_properties


def upload_file(host: VCenter, params: UploadParams):
    try:
        context = None
        if hasattr(ssl, '_create_unverified_context'):
            context = ssl._create_unverified_context()
            print(context)
        service_instance = connect.SmartConnect(host=host.host,
                                                user=host.username,
                                                pwd=host.userpassword,
                                                port=int(443),
                                                sslContext=context)

        if not service_instance:
            return "Could not connect to the specified host using specified username and password"

        atexit.register(connect.Disconnect, service_instance)
        content = service_instance.RetrieveContent()

        vms = collect_properties(service_instance, service_instance.content.rootFolder, vim.VirtualMachine,
                                 ['name'])

        vm = next(filter(lambda vm: vm['name']
                         == params.vm_name, vms.values()))
        vm = vm['obj']

        tools_status = vm.guest.toolsStatus
        if (tools_status == 'toolsNotInstalled' or
                tools_status == 'toolsNotRunning'):
            raise SystemExit(
                "VMwareTools is either not running or not installed. "
                "Rerun the script after verifying that VMWareTools "
                "is running")
        creds = vim.vm.guest.NamePasswordAuthentication(
            username=params.vm_user, password=params.vm_pwd)
        with open(params.path_from_local, 'rb') as myfile:
            fileinmemory = myfile.read()

        try:
            file_attribute = vim.vm.guest.FileManager.FileAttributes()
            url = content.guestOperationsManager.fileManager. \
                InitiateFileTransferToGuest(vm, creds, params.path_inside_vm,
                                            file_attribute,
                                            len(fileinmemory), True)
            # When : host argument becomes https://*:443/guestFile?
            # Ref: https://github.com/vmware/pyvmomi/blob/master/docs/ \
            #            vim/vm/guest/FileManager.rst
            # Script fails in that case, saying URL has an invalid label.
            # By having hostname in place will take take care of this.
            url = re.sub(r"^https://\*:", "https://"+str(host.host)+":", url)
            resp = requests.put(url, data=fileinmemory, verify=False)
            if not resp.status_code == 200:
                print("Error while uploading file")
                return "Error while uploading file"
            else:
                print("Successfully uploaded file")
                return "Successfully uploaded file"
        except IOError as e:
            print(e)
    except vmodl.MethodFault as error:
        print("Caught vmodl fault : " + error.msg)
        return -1
    return 0
