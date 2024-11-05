# Prerequisites

```
dnf install -y php-pgsql
```

# Postrequsites

Apply ingestor fix
```
cd /tmp
curl -O https://patch-diff.githubusercontent.com/raw/ubccr/xdmod/pull/1942.patch
cd /usr/share/xdmod
patch -p1 < /tmp/1942.patch
```
