##############################################################################
## marco
repo_dir=$openstack_repo_dir
repo=$openstack_repo
err_log="$HOME/update_local_apt_repo_err.log"

packages=$*
existed_packages_str=""
install_failed_packages=""
install_existed_packages=""


##############################################################################
## function

function init_err_log() {
    [ -f $err_log ] || touch $err_log
    printf "

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
start date: %s
script wants to apt download debs as followed:
<%s>

start download... ... ...

" "$(date)" "$packages" | tee -a $err_log
}


function finish_err_log() {
    printf "

finish ... ... ...
finish date: %s
--> all the packages are:
    <$packages>
--> already existed packages are:
    <$install_existed_packages>
--> failed packages are:
    <$install_failed_packages>

vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

" "$(date)" | tee -a $err_log
}


function show_err_and_exit() {
    echo "Error: $1" | tee -a $err_log
    exit 1
}

function generate_existed_package_array() {
    echo "----->  scanning existed packages ... ... ..." | tee -a $err_log
    cd $repo_dir/$repo
    existed_packages_str=$(gunzip -9c Packages.gz | egrep "^Package:" | \
                           cut -d ' ' -f 2)
}

function assert_package_not_existed() {
    local package="$1"
    local result=""

    result=$(echo "$existed_packages_str" | \
        while read item;
        do
            if [ "$item" = "$package" ]; then
                echo "existed"
                return 0
            fi
        done
    )
    [ "$result" = "existed" ] && return 1 || return 0
}


##############################################################################
## main

init_err_log

[ -z "$repo_dir" -o -z "$repo" ] && \
    show_err_and_exit "The envir argv is not exist!"
[ -d $repo_dir ] || \
    show_err_and_exit "the dir of repo <$repo_dir> is not exist!"
[ -d $repo_dir/$repo ] || \
    show_err_and_exit "repo <$repo_dir: $repo> is not exist!"

generate_existed_package_array

cd $repo_dir/$repo
for package in $@;
    do
        printf "\n--> start to download apt debs <$package>\n" | \
            tee -a $err_log

        assert_package_not_existed "$package"
        if [ $? != 0 ]; then
            printf "the package <$package> is existed, jump it\n" | \
                tee -a $err_log
            install_existed_packages="$install_existed_packages $package"
            continue;
        fi
        printf "    download package <$package>\n" | tee -a $err_log

        apt-cache depends "$package" -i --recurse | \
            awk '/^[a-z]/ {print $0}' | \
            xargs apt-get --allow-unauthenticated download

        if [ $? != 0 ]; then
            echo "**** Exception: apt download <$package> failed" | \
                tee -a $err_log;
            install_failed_packages="$install_failed_packages $package"
        fi
    done

printf "\n***********\n" | tee -a $err_log

cd ..
dpkg-scanpackages $repo /dev/null | \
    gzip -9c > \
    $repo/Packages.gz 2>&1 | tee -a $err_log

finish_err_log
