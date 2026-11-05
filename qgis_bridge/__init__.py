def classFactory(iface):
    from .bridge_plugin import FTTHAutomationBridge
    return FTTHAutomationBridge(iface)
