# Prerequisites

```
dnf install -y php-pgsql
yum install --enablerepo "powertools" python3-matplotlib python3-pandas
```

# Postrequsites

Apply ingestor fix
```
cd /tmp
curl -O https://patch-diff.githubusercontent.com/raw/ubccr/xdmod/pull/1942.patch
cd /usr/share/xdmod
patch -p1 < /tmp/1942.patch
```

Apply Program type fix

```
cd /etc/xdmod
curl -L https://patch-diff.githubusercontent.com/raw/ubccr/xdmod/pull/1943.patch | sudo  patch -p2
```

Apply side-by-side chart fix
```
cd /tmp
curl -O https://patch-diff.githubusercontent.com/raw/ubccr/xdmod/pull/1883.patch
cd /usr/share/xdmod
patch -p1 < /tmp/1883.patch

Apply cloud bodge
```
https://raw.githubusercontent.com/ubccr/xdmod/9939f7431d804d72dcc4333eb2e620c099cd671f/configuration/etl/etl_action_defs.d/cloud_openstack/staging_raw_instance_type.json
```

# Design Ideas

Groupy Requested Resource?
Group by Awarded Resource?


Could do a group by resource action?
