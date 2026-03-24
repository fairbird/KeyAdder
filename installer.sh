#!/bin/bash

######### Only These two lines to edit with new version ######
version='9.5'
description='What is NEW:\n- Fixes.\n\n*************************\n:ما هو الجديد\n- إصلاحات'

# Configure where we can find things here #
TMPDIR='/tmp'
PLUGINDIR='/usr/lib/enigma2/python/Plugins/Extensions'

# Remove Old Version #
rm -rf $PLUGINDIR/AddKey
rm -rf $PLUGINDIR/KeyAdder
rm -rf $PLUGINDIR/Biscotto
rm -rf $TMPDIR/*main*

#########################
if [ -f /etc/opkg/opkg.conf ]; then
    STATUS='/var/lib/opkg/status'
    OSTYPE='Opensource'
    OPKG='opkg update'
    OPKGINSTAL='opkg install'
elif [ -f /etc/apt/apt.conf ]; then
    STATUS='/var/lib/dpkg/status'
    OSTYPE='DreamOS'
    OPKG='apt-get update'
    OPKGINSTAL='apt-get install'
fi

#########################
install() {
    if grep -qs "Package: $1" $STATUS; then
        echo
    else
        $OPKG >/dev/null 2>&1
        echo "   >>>>   Need to install $1   <<<<"
        echo
        if [ $OSTYPE = "Opensource" ]; then
            $OPKGINSTAL "$1"
            clear
        elif [ $OSTYPE = "DreamOS" ]; then
            $OPKGINSTAL "$1" -y
            clear
        fi
    fi
}

#########################
if [ -f /usr/bin/python3 ] ; then
    echo ":You have Python3 image ..."
    Packagesix=python3-six
    Packageprocps=procps
else
    echo ":You have Python2 image ..."
    Packagesix=python-six
    Packageprocps=procps
fi

install $Packagesix $Packageprocps

#########################
cd /tmp
set -e
echo "Downloading And Insallling KeyAdder plugin Please Wait ......"
echo
wget https://github.com/fairbird/KeyAdder/archive/refs/heads/main.tar.gz
tar -xzf main.tar.gz
cp -r KeyAdder-main/usr /
rm -rf *ArabicSavior* > /dev/null 2>&1
rm -rf *main* > /dev/null 2>&1
set +e
cd ..
sync
#########################

### Check if plugin installed correctly
if [ ! -d '/usr/lib/enigma2/python/Plugins/Extensions/KeyAdder' ]; then
	echo "Some thing wrong .. Plugin not installed"
	exit 1
fi

sync
echo "#########################################################"
echo "#         KeyAdder INSTALLED SUCCESSFULLY               #"
echo "#                 RAED (fiarbird)                       #"              
echo "#                     support                           #"
echo "#   https://www.tunisia-sat.com/forums/threads/3955125/ #"
echo "#########################################################"
echo "#           your Device will RESTART Now                #"
echo "#########################################################"
sleep 3
killall enigma2
exit 0
