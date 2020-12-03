import atexit
import ssl
import re
import time
import requests
from pyVim import connect
from pyVmomi import vim, vmodl


from src.classes.vcenter import VCenter
from src.classes.execute_params import ExecuteParams
from src.helper.filter_helper import collect_properties


def execute_program(host: VCenter, params: ExecuteParams):

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
       
        try:
            pm = content.guestOperationsManager.processManager

            ps = vim.vm.guest.ProcessManager.ProgramSpec(
                programPath=params.path_to_program,
                arguments=r" >> C:\Users\Administrator\Desktop\out.txt"
            )
            res = pm.StartProgramInGuest(vm, creds, ps)


            if res > 0:
                print("Program submitted, PID is %d" % res)
                pid_exitcode = pm.ListProcessesInGuest(vm, creds,
                                                       [res]).pop().exitCode
                # If its not a numeric result code, it says None on submit
                while (re.match('[^0-9]+', str(pid_exitcode))):
                    print("Program running, PID is %d" % res)
                    time.sleep(5)
                    pid_exitcode = pm.ListProcessesInGuest(vm, creds,
                                                           [res]).pop().\
                        exitCode
                    if (pid_exitcode == 0):
                        print("Program %d completed with success" % res)
                        break
                    # Look for non-zero code to fail
                    elif (re.match('[1-9]+', str(pid_exitcode))):
                        print("ERROR: Program %d completed with Failute" % res)
                        # print("  tip: Try running this on guest %r to debug" \
                        #     % summary.guest.ipAddress)
                        print("ERROR: More info on process")
                        print(pm.ListProcessesInGuest(vm, creds, [res]))
                        break
                

                # download
                dest=r"/Users/harry_jhan/Desktop/sample/out.txt" #My local pc

                src=r"C:\Users\Administrator\Desktop\out.txt" #Server's directory
                fti = content.guestOperationsManager.fileManager.InitiateFileTransferFromGuest(vm, creds, src)

                resp=requests.get(fti.url, verify=False)

                #Writes into file
                with open(dest, 'wb') as f:
                        f.write(resp.content)
        except IOError as e:
            print(e)
    except vmodl.MethodFault as error:
        print("Caught vmodl fault : " + error.msg)
        return -1

    return 0
    