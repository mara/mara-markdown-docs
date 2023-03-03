def MARA_NAVIGATION_ENTRIES():
    from . import docs
    return {'Documentation': docs.documentation_navigation_entry()}

def MARA_FLASK_BLUEPRINTS():
    from . import docs
    return [docs.docs]

def MARA_CONFIG_MODULES():
    from . import config
    return [config]

def MARA_ACL_RESOURCES():
    from . import docs
    return {'Documentation': docs.documentation_acl_resource}
