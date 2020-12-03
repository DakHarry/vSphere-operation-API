from pyVmomi import vim, vmodl
# ALLOWED: from pyVmomi import vim
from pyVmomi import vim

"""
fetch data from server instance
"""
def collect_properties(si, root, vim_type, props):
    objects = {}
    # Start with all the VMs from container, which is easier to write than
    # PropertyCollector to retrieve them.
    view_mgr = si.content.viewManager
    container = view_mgr.CreateContainerView(si.content.rootFolder,
                                             [vim_type], True)
    try:
        filter_spec = get_filter_spec(container, vim_type, props)
        options = vmodl.query.PropertyCollector.RetrieveOptions()
        pc = si.content.propertyCollector
        result = pc.RetrievePropertiesEx([filter_spec], options)
        process_result(result, objects)
        while result.token is not None:
            result = pc.ContinueRetrievePropertiesEx(result.token)
            process_result(result, objects)
    finally:
        container.Destroy()
    return objects

def get_filter_spec(containerView, objType, path):
    traverse_spec = vmodl.query.PropertyCollector.TraversalSpec()
    traverse_spec.name = 'traverse'
    traverse_spec.path = 'view'
    traverse_spec.skip = False
    traverse_spec.type = vim.view.ContainerView

    obj_spec = vmodl.query.PropertyCollector.ObjectSpec()
    obj_spec.obj = containerView
    obj_spec.skip = True
    obj_spec.selectSet.append(traverse_spec)

    prop_spec = vmodl.query.PropertyCollector.PropertySpec()
    prop_spec.type = objType
    prop_spec.pathSet = path

    return vmodl.query.PropertyCollector.FilterSpec(propSet=[prop_spec],
                                                    objectSet=[obj_spec])

def process_result(result, objects):
    for o in result.objects:
        if o.obj not in objects:
            objects[o.obj] = {}
            objects[o.obj]['obj'] = o.obj
        for p in o.propSet:
            objects[o.obj][p.name] = p.val
