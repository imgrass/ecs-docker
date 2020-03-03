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

    def create_container(self, **kwargs):
        hostname = kwargs['hostname']
        image    = kwargs['image']
        name     = kwargs['name']

        cap_add  = kwargs.get('cap_add', 'SYS_ADMIN')
        command  = kwargs.get('command', 'systemd')
        env      = kwargs.get('env', None)
        volumes  = kwargs.get('volumes', None)

        try:
            self.dk_client.containers.get(name).remove(force=True)
            print('==> remove existed container %s' % name)
        except docker.errors.NotFound:
            pass

        return self.dk_client.containers.run(
            image, command, cap_add=cap_add, detach=True, environment=env,
            hostname=hostname, name=name, volumes=volumes)


class DeployOpenstack(DeployOpenstackBase, Const):
    def __init__(self):
        print('... Start to deploy Openstack ...')
        super(DeployOpenstack, self).__init__()

        self.hdr_keystone = None

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


if __name__ == '__main__':
    DeployOpenstack().keystone_container()