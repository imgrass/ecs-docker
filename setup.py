#!/usr/bin/env python
import os, sys
from commands import getstatusoutput
from time import sleep


def get_docker_image_info(repository, tag):
    status, output = getstatusoutput(
            'docker images | awk \'$1=="%s" && $2=="%s" {print $3}\'' %
            (repository, tag))
    if len(output) is 0 or status is not 0:
        return None

    image_id = output
    print('--> get docker image with <repository:%s> and <tag:%s> is %s' %
          (repository, tag, image_id))
    return image_id


def force_remove_container(repository, tag):
    print('--> force remove container <%s:%s>\n' % (repository, tag))
    status, output = getstatusoutput(
            'docker ps -a | awk \'$2=="%s:%s" {print $1}\'' %
            (repository, tag))
    for container_id in output.split('\n'):
        getstatusoutput('docker rm -f %s' % container_id)


def build_openstack_base_image(repository, tag, path_docker_file):
    image_id = get_docker_image_info(repository, tag)
    if image_id is not None:
        return image_id

    os.remove('Dockerfile')
    os.symlink(path_docker_file, 'Dockerfile')
    cmd = 'docker build -t %s:%s . | tee docker_build.log' % (repository, tag)
    print ('--> cmd is <%s>' % cmd)
    status, output = getstatusoutput(cmd)

    if status is not 0:
        print '----> docker build %s:%s failed\n' % (repository, tag)
        print output
        return None
    return get_docker_image_info(repository, tag)


def setup_container(repository, tag, name=None, hostname=None,
                    path_shared=None):
    # docker_release_container =
    # "docker ps -a | cut -d ' ' -f 1 | xargs docker rm"
    if get_docker_image_info(repository, tag) is None:
        return None

    ## the option [privileged] used to level up the privilege of container,
    ## used for chrony
    docker_run_cmd = 'docker run --privileged -it'

    if name is not None:
        docker_run_cmd += ' --name %s' % name
    if hostname is not None:
        docker_run_cmd += ' --hostname %s' % hostname
    if path_shared is not None:
        docker_run_cmd += ' -v %s' % path_shared

    docker_run_cmd += ' %s:%s /bin/bash' % (repository, tag)
    print '--> run <%s>\n' % docker_run_cmd
    sys.exit(1)


if __name__ == '__main__':
    # setup_container('openstack', 'base-v0', hostname='sola', path_shared='/home/eouylei:/data')
    # setup_container('ubuntu', '16.04.3', hostname='sola', path_shared='/home/eouylei:/data')
    build_openstack_base_image('apt-server', 'openstack_v0',
                               'dockerfiles/dockerfile_apt_server.js1')
