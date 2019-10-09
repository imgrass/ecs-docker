import sys

class network(object):
    def __init__(self, **kwargs):
        # management network
        self.mn_iface = kwargs.get('mn_iface', None)
        self.mn_ifaddr = kwargs.get('mn_ifaddr', None)
        self.mn_mask = kwargs.get('mn_mask', None)
        self.mn_gtw = kwargs.get('mn_gtw', None)

        # provider network
        self.pn_iface = kwargs.get('pn_iface', None)
        self.pn_ifaddr = kwargs.get('pn_ifaddr', None)
        self.pn_mask = kwargs.get('pn_mask', None)
        self.pn_gtw = kwargs.get('pn_gtw', None)


class controller(network):
    ref_count = 0

    def __init__(self, **kwargs):
        self.host = 'controller_%d' % self.ref_count
        self.ref_count += 1
        network.__init__(self, **kwargs)


class compute(network):
    ref_count = 0

    def __init__(self, **kwargs):
        self.host = 'compute_%d' % self.ref_count
        self.ref_count += 1
        network.__init__(self, **kwargs)


## network configuration
controller_ntw = {
        'mn_iface': 'eth0',
        'mn_ifaddr': '10.0.0.11',
        'mn_mask': 24,
        'mn_gtw': '10.0.0.1',

        'pn_iface': 'eth1',
        'pn_ifaddr': None,
        'pn_mask': 24,
        'pn_gtw': '203.0.113.1',
        }
compute_ntw = {
        'mn_iface': 'eth0',
        'mn_ifaddr': '10.0.0.31',
        'mn_mask': 24,
        'mn_gtw': '10.0.0.1',

        'pn_iface': 'eth1',
        'pn_ifaddr': None,
        'pn_mask': 24,
        'pn_gtw': '203.0.113.1',
        }


class passwords(object):
    ADMIN_PASS = 'rootroot'
    CINDER_DBPASS = 'rootroot'
    CINDER_PASS = 'rootroot'
    DASH_DBPASS = 'rootroot'
    DEMO_PASS = 'rootroot'
    GLANCE_DBPASS = 'rootroot'
    GLANCE_PASS = 'rootroot'
    KEYSTONE_DBPASS = 'rootroot'
    METADATA_SECRET = 'rootroot'
    NEUTRON_DBPASS = 'rootroot'
    NEUTRON_PASS = 'rootroot'
    NOVA_DBPASS = 'rootroot'
    NOVA_PASS = 'rootroot'
    PLACEMENT_PASS = 'rootroot'
    RABBIT_PASS = 'rootroot'



class config(object):
    def __init__(self):
        self.controller_ntw = controller(**controller_ntw)
        self.compute_ntw = compute(**compute_ntw)

        self.passwords = passwords()

        self.docker_img_base = 'ubuntu:16.04.3'


if __name__ == '__main__':
    tmp = config()
    print tmp.controller_ntw.__dict__
    print tmp.compute_ntw.__dict__
    print tmp.passwords.PLACEMENT_PASS
