#!/bin/bash
# Bootstrap script that either sets up a fresh XDMoD test instance or upgrades
# an existing one.  This code is only designed to work inside the XDMoD test
# docker instances. However, since it is designed to test a real install, the
# set of commands that are run would work on a real production system.

BASEDIR=/root/xdmod-nairr/tests/ci
REF_SOURCE=`realpath $BASEDIR/../artifacts/nairr`
XDMOD_SRC_DIR=`realpath ${XDMOD_SRC_DIR:-$BASEDIR/../../xdmod}`
REPODIR=`realpath $XDMOD_SRC_DIR`
REF_DIR=/var/tmp/nairr

function copy_template_httpd_conf {
    cp /usr/share/xdmod/templates/apache.conf /etc/httpd/conf.d/xdmod.conf
}

function move_info_etc_xdmod {

    rm /etc/xdmod/organization.json
    rm /etc/xdmod/resource_specs.json
    rm /etc/xdmod/resources.json
    rm /etc/xdmod/resource_types.json
    rm /etc/xdmod/hierarchy.json
    # Copy the reference data into the /etc/xdmod directory. This is where the      
    cp $REF_SOURCE/organization.json /etc/xdmod/
    cp $REF_SOURCE/resource_specs.json /etc/xdmod/
    cp $REF_SOURCE/resources.json /etc/xdmod/
    cp $REF_SOURCE/resource_types.json /etc/xdmod/
    cp $REF_SOURCE/hierarchy.json /etc/xdmod/
}

function set_resource_spec_end_times {
    # Adding end time for each resource in resourcespecs.json. This is to get consistant results for
    # the raw data regression tests. The jq command does not do well with overwriting the existing file
    # so writing to a temp file and then renaming seems to be the best way to go.
    cat /etc/xdmod/resource_specs.json | jq '[.[] | .["end_date"] += "2020-01-01"]' > /etc/xdmod/resource_specs2.json
    jq . /etc/xdmod/resource_specs2.json > /etc/xdmod/resource_specs.json
    rm -f /etc/xdmod/resource_specs2.json
}

if [ -z $XDMOD_REALMS ]; then
    export XDMOD_REALMS=jobs,storage,cloud,resourcespecifications
fi

cp -r $REF_SOURCE /var/tmp/

set -e
set -o pipefail

PYTHON_SCIPY=python3-scipy
if [ `rpm -E %{rhel}` = 7 ]; then
    PYTHON_SCIPY=python36-scipy
fi

# Install python dependencies for the image hash comparison algorithm
yum install -y python3 python3-six python3-numpy python3-pillow ${PYTHON_SCIPY}
pip3 install imagehash==4.2.1
cp $XDMOD_SRC_DIR/tests/ci/scripts/imagehash /root/bin

# nairr dependencies
dnf install -y php-pgsql
yum install -y --enablerepo "powertools" python3-matplotlib python3-pandas ${PYTHON_SCIPY}

# ensure php error logging is set to E_ALL (recommended setting for development)
sed -i 's/^error_reporting = .*/error_reporting = E_ALL/' /etc/php.ini

# ensure php command-line errors are logged to a file
sed -i 's/^;error_log = php_errors.log/error_log = \/var\/log\/php_errors.log/' /etc/php.ini


if [ "$XDMOD_TEST_MODE" = "fresh_install" ];
then
    rpm -qa | grep ^xdmod | xargs yum -y remove || true
    rm -rf /etc/xdmod

    rm -rf /var/lib/mysql
    mkdir -p /var/lib/mysql
    mkdir -p /var/log/mariadb
    mkdir -p /var/run/mariadb
    chown -R mysql:mysql /var/lib/mysql
    chown -R mysql:mysql /var/log/mariadb
    chown -R mysql:mysql /var/run/mariadb

    dnf install -y ~/rpmbuild/RPMS/*/xdmod-11.5*.rpm
    dnf install -y ~/rpmbuild/RPMS/*/xdmod-cloudbank-11.5*.rpm
    rpm -Uvh --replacefiles ~/rpmbuild/RPMS/*/xdmod-nairr-11.5*.rpm
    mysql_install_db --user mysql

    if [ -f /etc/my.cnf.d/mariadb-server.cnf ]; then
        >/etc/my.cnf.d/mariadb-server.cnf
        echo "# this is read by the standalone daemon and embedded servers
              [server]
              sql_mode=
              # this is only for the mysqld standalone daemon
              # Settings user and group are ignored when systemd is used.
              # If you need to run mysqld under a different user or group,
              # customize your systemd unit file for mysqld/mariadb according to the
              # instructions in http://fedoraproject.org/wiki/Systemd
              [mysqld]
              datadir=/var/lib/mysql
              socket=/var/lib/mysql/mysql.sock
              log-error=/var/log/mariadb/mariadb.log
              pid-file=/run/mariadb/mariadb.pid" > /etc/my.cnf.d/mariadb-server.cnf
    fi
    move_info_etc_xdmod
    copy_template_httpd_conf

    # Download patch directly to /tmp (no cd)
    curl -o /tmp/1942.patch https://patch-diff.githubusercontent.com/raw/ubccr/xdmod/pull/1942.patch

# Apply the patch in /usr/share/xdmod without changing directory
    patch -d /usr/share/xdmod -p1 < /tmp/1942.patch
    ~/bin/services start
    mysql -e "CREATE USER 'root'@'gateway' IDENTIFIED BY '';
    GRANT ALL PRIVILEGES ON *.* TO 'root'@'gateway' WITH GRANT OPTION;
    FLUSH PRIVILEGES;"

    # TODO: Replace diff files with hard fixes
    # Modify integration sso tests to work with cloud realm
    if [ "$XDMOD_REALMS" = "cloud" ]; then
        if ! patch --dry-run -Rfsup1 --directory=$REPODIR < $XDMOD_SRC_DIR/tests/ci/diff/SSOLoginTest.php.diff >/dev/null; then
            # -- Fix users searched in SSO test
            patch -up1 --directory=$REPODIR <  $XDMOD_SRC_DIR/tests/ci/diff/SSOLoginTest.php.diff
        fi
    else
        if patch --dry-run -Rfsup1 --directory=$REPODIR <  $XDMOD_SRC_DIR/tests/ci/diff/SSOLoginTest.php.diff >/dev/null; then
            # -- Reverse previous patch
            patch -R -up1 --directory=$REPODIR <  $XDMOD_SRC_DIR/tests/ci/diff/SSOLoginTest.php.diff
        fi
    fi

    expect  $XDMOD_SRC_DIR/tests/ci/scripts/xdmod-setup-start.tcl | col -b

    mysql -e "CREATE DATABASE modw_resourceactions";
    mysql -e "GRANT ALL PRIVILEGES ON *.* TO 'root'@'gateway' WITH GRANT OPTION;
    GRANT ALL PRIVILEGES ON *.* TO 'xdmod'@'gateway' WITH GRANT OPTION;
    FLUSH PRIVILEGES;"

    sudo /usr/share/xdmod/tools/etl/etl_overseer.php -a xdmod.hpcdb-ingest-common.unknown_organization 
    xdmod-import-csv -t hierarchy -i $REF_DIR/hierarchy.csv
    xdmod-import-csv -t group-to-hierarchy -i $REF_DIR/group-to-hierarchy.csv

    if [[ "$XDMOD_REALMS" == *"jobs"* ]];
    then
        xdmod-shredder -r NVIDIA-DGX-Cloud -f slurmjson -d $REF_DIR/data/dgx/postprocessed/ -q 
    fi

    if [[ "$XDMOD_REALMS" == *"cloud"* ]];
    then
        last_modified_start_date=$(date +'%F %T')
        xdmod-shredder -r Indiana-Jetstream2-GPU -f openstack -d $REF_DIR/data/jetstream/nairr-jetstream2
        xdmod-shredder -r Indiana-Jetstream2-GPU -f openstack -d $REF_DIR/data/jetstream/nairr-jetstream2-lm/  
        xdmod-shredder -r Indiana-Jetstream2-GPU -f openstack -d $REF_DIR/data/jetstream/nairr-jetstream2-gpu/
    fi
    

    sudo /usr/share/xdmod/tools/etl/etl_overseer.php -p nairr.resource-actions-bootstrap
    sudo /usr/share/xdmod/tools/etl/etl_overseer.php -p nairr.resource-actions -m 2000-01-01
    xdmod-build-filter-lists --realm ResourceActions --quiet

    xdmod-ingestor
    xdmod-import-csv -t names -i $REF_DIR/names.csv
    xdmod-ingestor --start-date "2016-12-01" --end-date "2025-06-01" --last-modified-start-date "2017-01-01 00:00:00"
    php $XDMOD_SRC_DIR/tests/ci/scripts/create_xdmod_users.php

fi


