import atexit
import ssl
from pyVim import connect
from pyVmomi import vim, vmodl # pylint: disable=E0401

from src.classes.vcenter import VCenter
from src.helper.filter_helper import collect_properties

def get_vm(host: VCenter, vm_id: str):
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

        # get vm
        vms = collect_properties(service_instance, service_instance.content.rootFolder, vim.VirtualMachine,
                                 ['summary'])

        vm = next(filter(lambda vm: vm['summary'].vm._moId
                         == vm_id, vms.values()))
        vm = vm['obj']

        return 0
    except vmodl.MethodFault as error:
        print("Caught vmodl fault : " + error.msg)
        return -1
        