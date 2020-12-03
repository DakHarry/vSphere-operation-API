vSphere operation API
=========================
> A simple POC to manage vSphere resources by FastAPI

This project demos how to upload a script file into the specific VM created by vShpere. Then execute the program and get/send the result to the computer. 

# Getting Started
To get started, you will need Python, pip, uvicorn and [pyvmomi](https://github.com/vmware/pyvmomi)

## Installation
You can install requirements with pip
```
$ pip install -r requirements.txt
```

## Run server
```
uvicorn app.main:app --reload
```

### Endpoint

> POST /vm/upload-file
> upload file to the specific VM.
```
body parameters
{
    "host": {
        "host": "vCenter Host",  
        "username": "xxx@vsphere.local",
        "userpassword": "vCenter password"
    },
    "params": {
        "vm_name": "VM name",
        "vm_user": "VM computer username",
        "vm_pwd": "VM computer password",
        "path_inside_vm": "C:\\Users\\Administrator\\Desktop\\hello.bat", // path you want to store inside the VM
        "path_from_local": "/Users/harry_jhan/Desktop/sample/hello.bat" // file path from your computer
    }
}
```

> POST /vm/run-program
> Run a script inside the VM, then download the result as `out.txt` on your machine.

```
body parameters

{
    "host": {
        "host": "vCenter Host",  
        "username": "xxx@vsphere.local",
        "userpassword": "vCenter password"
    },
    "params": {
        "vm_name": "VM name",
        "vm_user": "VM computer username",
        "vm_pwd": "VM computer password",
        "path_to_program": "C:\\Users\\Administrator\\Desktop\\hello.bat" // script you want to run
    }
}
```


### Folder structure
```
/src
  /classes - data structure
  /helper - shared function
    filter_helper.py - filter the objects return from vSphere
  /models - main logic of the api
  /router
```