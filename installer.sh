#!/bin/bash
# ###########################################
# SCRIPT : DOWNLOAD AND INSTALL KeyAdder
# ###########################################
#
# Command: wget https://raw.githubusercontent.com/fairbird/KeyAdder/main/installer.sh -qO - | /bin/sh
#
# ###########################################

######### Only These two lines to edit with new version ######
version='9.5'
description='What is NEW:\n- Fixes.\n\n*************************\n:ما هو الجديد\n- إصلاحات'
##############################################################

###########################################
# Configure where we can find things here #
TMPDIR='/tmp'
PLUGINDIR='/usr/lib/enigma2/python/Plugins/Extensions'

#######################
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
cd $TMPDIR
echo "Downloading And Insallling KeyAdder plugin Please Wait ......"
echo
wget https://github.com/fairbird/KeyAdder/archive/refs/heads/main.tar.gz -qP $TMPDIR
tar -xzf main.tar.gz
cp -r KeyAdder-main/usr /
rm -rf *main*
cd ..
#########################

sleep 2
clear
echo "#########################################################"
echo "#          KeyAdder INSTALLED SUCCESSFULLY              #"
echo "#                 Raed  &  mfaraj57                     #"
echo "#                     support                           #"
echo "#   https://www.tunisia-sat.com/forums/threads/3955125/ #"
echo "#########################################################"
echo "#           your Device will RESTART Now                #"
echo "#########################################################"

killall enigma2

exit 0
