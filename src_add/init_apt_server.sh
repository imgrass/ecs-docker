function apache_service() {
    ## action is ['start', 'status']
    local action="$1"

    service apache2 $action > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        apache_runtime_status=1
        apache_runtime_info='Exception: apache2 running failed, pls check it'
    else
        apache_runtime_status=0
        apache_runtime_info='Successfully!, apache2 is running ... ...'
    fi
}


function cmd_init_os_env() {
    apache_listen_port=$(cat /etc/apache2/ports.conf | awk '/^Listen/ {print $2}')
    apache_service start

    hostname=$HOSTNAME
    ip_addr=$(
        ip a show dev eth0 | \
            awk '/inet / {match($0, /[.\/0-9]+/); \
                          print substr($0, RSTART, RLENGTH)}')

    echo "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    echo "=======   APT SERVER    ========"
    echo "++++++++++++++++++++++++++++++++"
    echo "hostname: $hostname"
    echo "ip: $ip_addr"
    echo ""
    echo "service apache2 listens port <$apache_listen_port> and now"
    echo "$apache_runtime_info"
    echo ""

    export openstack_repo_dir="/var/www/html/debs"
    export openstack_repo="openstack"
}


# req_deb_list=/root/requested_debs_list.txt
function cmd_update_apt() {
    req_deb_list="$1"
    echo "--> start update apt service with list <$req_deb_list> ... ... ..."
    apache_service status
    if [ $apache_runtime_status -ne 0 ]; then
        echo $apache_runtime_info
        return 1
    fi

    local debs=$(
        awk ' \
            BEGIN {debs=""}; \
            {if($0 ~ /^\*/){ \
                match($0, /[^*]+/); \
                debs=debs" "substr($0, RSTART, RLENGTH);}}; \
            END {print debs}' $req_deb_list)

    if [ "$debs" = "" ]; then
        echo ">_<! debs is None, pls check the file<$req_deb_list> you imported"
        return 0
    fi
    update_local_apt_repo.sh $debs
}


function usage() {
    echo -e "\nUsage: $(basename $0) [options] \n"
    echo -e " -i, --init_os_env     Initialization when container starts,
                                    including starting apache2 and set env args"
    echo -e " -u, --update_apt      Updating local apt server"
}


function opt_parse() {
    OPTPARSER=$(getopt --options "iu:" \
                       --longoptions "init_os_env,update_apt:" \
                       --name "$(basename $0)" \
                       -- "$@")
    if [ $? -ne 0 ]; then
        echo "Error during parsing option/parameter"
        usage
        exit 1
    fi

    set -- ${OPTPARSER}
    while [ $# -gt 0 ]; do
        case "$1" in
            -i|--init_os_env)
                cmd_init_os_env
                ## this is used to maintain the interaction state of the container
                ## shift 2 is used to rm '--' in "$@"
                ## echo "\$@ is <$@>"
                shift 2
                exec "${@//\'/}"
                exit 0
                ;;
            -u|--update_apt)
                cmd_update_apt ${2//\'/}
                exit $?
                ;;
            --)
                shift
                break
                ;;
            *)
                usage
                exit 1
                ;;
        esac
    done
}

opt_parse $@
