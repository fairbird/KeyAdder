#!/bin/sh
##setup command=wget -q "--no-check-certificate" https://raw.githubusercontent.com/fairbird/KeyAdder/main/installer.sh -O - | /bin/sh

######### Only These two lines to edit with new version ######
version=5.8
description=What is NEW:\n[[Move plugin to my source github]\nما هو الجديد:\n[github نقل البلجن الى سورساتي على]
##############################################################

# Python version
PYTHON_VERSION=$(python -c"import platform; print(platform.python_version())")

# remove old version
rm -rf /usr/lib/enigma2/python/Plugins/Extensions/AddKey
rm -rf /usr/lib/enigma2/python/Plugins/Extensions/KeyAdder
rm -rf /usr/lib/enigma2/python/Plugins/Extensions/Biscotto

# Download and install plugin

if [ -f /var/lib/dpkg/status ]; then
   STATUS=/var/lib/dpkg/status
   OSTYPE=DreamOs
else
   STATUS=/var/lib/opkg/status
   OSTYPE=Dream
fi

if python --version 2>&1 | grep -q '^Python 3\.'; then
	echo "You have Python3 image"
	PYTHON=PY3
	Packagesix=python3-six
else
	echo "You have Python2 image"
	PYTHON=PY2
	Packagesix=python-six
fi

if grep -qs "Package: $Packagesix" cat $STATUS ; then
	echo ""
else
	echo "Need to install $Packagesix"
	echo ""
	if [ $OSTYPE = "DreamOs" ]; then
		apt-get update && apt-get install python-six -y
	elif [ $PYTHON = "PY3" ]; then
		opkg update && opkg install python3-six
	elif [ $PYTHON = "PY2" ]; then
		opkg update && opkg install python-six
	fi
fi
echo ""

cd /tmp 
wget -q "--no-check-certificate" https://github.com/fairbird/KeyAdder/archive/refs/heads/main.tar.gz
tar -xf main.tar.gz
cp -rf KeyAdder-main/usr /
rm -rf KeyAdder-main*
cd ..

sync
echo "#########################################################"
echo "#          KeyAdder INSTALLED SUCCESSFULLY              #"
echo "#                 Raed  &  mfaraj57                     #"              
echo "#                     support                           #"
echo "#   https://www.tunisia-sat.com/forums/threads/3955125/ #"
echo "#########################################################"
echo "#           your Device will RESTART Now                #"
echo "#########################################################"
sleep 3
killall enigma2
exit 0
