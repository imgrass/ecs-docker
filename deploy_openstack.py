#!/usr/bin/env python
import docker


class Const(object):
    dir_workspace = '/home/eouylei/imgrass/project/ecs-docker/workspace'
    dir_src = '/home/eouylei/imgrass/source-code/ecs-mos'


class DeployOpenstackBase(object):
    '''
    Provide the base implementation for all Openstack mouldes.
    '''

    dk_client = docker.from_env()

    def create_network(self, **kwargs):
        name    = kwargs['name']
        subnet  = kwargs['subnet']
        gateway = kwargs['gateway']

        driver  = kwargs.get('driver', 'bridge')

        print('+ Create network %s with <subnet:%s> <gateway:%s>' %
              (name, subnet, gateway))
        try:
            network = self.dk_client.networks.get(name)
            ipam_config = network.attrs.get('IPAM').get('Config')
            for ipam in ipam_config:
                if ipam.get('Subnet') == subnet and \
                   ipam.get('Gateway') == gateway:
                    print('  Network already existed')
                    return
            network.remove()
            print('  ==> remove existed network %s' % name)
        except docker.errors.NotFound:
            pass

        ipam_pool = docker.types.IPAMPool(subnet=subnet, gateway=gateway)
        ipam_config = docker.types.IPAMConfig(pool_configs=[ipam_pool])
        return self.dk_client.networks.create(name, driver=driver,
                                              ipam=ipam_config)

    def create_container(self, **kwargs):
        hostname = kwargs['hostname']
        image    = kwargs['image']
        name     = kwargs['name']

        cap_add  = kwargs.get('cap_add', 'SYS_ADMIN')
        command  = kwargs.get('command', 'systemd')
        env      = kwargs.get('env', None)
        volumes  = kwargs.get('volumes', None)

        print('+ Create container %s with <image:%s> <command:%s>' %
              (name, image, command))
        try:
            self.dk_client.containers.get(name).remove(force=True)
            print('==> remove existed container %s' % name)
        except docker.errors.NotFound:
            pass

        return self.dk_client.containers.run(
            image, command, cap_add=cap_add, detach=True, environment=env,
            hostname=hostname, name=name, volumes=volumes)

    def exec_run(self, container, command, workdir=None):
        exit, output = container.exec_run(command, workdir=workdir)
        print('..run <%s> in container %s with exit code %d' %
              (command, container.name, exit))
        if exit is 0:
            print('<DEBUG>: output is\n%s' % output)
        else:
            print('<FAILED>: output is\n%s' % output)

        return exit


class DeployOpenstack(DeployOpenstackBase, Const):
    def __init__(self):
        print('... Start to deploy Openstack ...')
        super(DeployOpenstack, self).__init__()

        self.hdr_keystone = None

    def init_network(self):
        ## docker network
        stk_mgmt = {
            'name'      : 'stk_mgmt',
            'driver'    : 'bridge',
            'subnet'    : '10.1.0.0/24',
            'gateway'   : '10.1.0.254',
        }

        stk_prv = {
            'name'      : 'stk_prv',
            'driver'    : 'bridge',
            'subnet'    : '203.1.113.0/24',
            'gateway'   : '203.1.113.254',
        }

        self.create_network(**stk_mgmt)
        self.create_network(**stk_prv)

    def keystone_container(self):
        env_pythonpath = 'PYTHONPATH=$PYTHONPATH:/opt/keystone/'\
                         ':/usr/local/lib/python2.7/dist-packages'

        volumes = {
            '%s/keystone/dist-packages' % self.dir_workspace: {
                'bind': '/usr/local/lib/python2.7/dist-packages',
                'mode': 'rw',
            },
            '%s/keystone/requirement' % self.dir_workspace: {
                'bind': '/opt/keystone',
                'mode': 'rw',
            },
            self.dir_src: {
                'bind': '/data',
                'mode': 'rw',
            },
        }

        config = {
            'hostname'  : 'keystone',
            'image'     : 'stk:latest',
            'name'      : 'keystone',

            'env'       : [env_pythonpath],
            'volumes'   : volumes,
        }
        #print('<DEBUG>: print config: \n%s' % str(config))
        self.hdr_keystone = self.create_container(**config)

        print('... Successfully create container keystone with <id:%s>' %
              self.hdr_keystone.id)

    def keystone_config(self):
        hdr_keystone = self.hdr_keystone or\
                       self.dk_client.containers.get('keystone')
        print('<DEBUG> hdr_keystone is %s' % hdr_keystone)

        self.exec_run(hdr_keystone, 'python setup.py install',
                      workdir='/data/openstack/keystone')


if __name__ == '__main__':
    DeployOpenstack().init_network()
