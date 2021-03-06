DESCRIPTION = "Enigma2 plugin to add and edit keys for (Biss, PowerVU, Irdeto and Tandberg)."
MAINTAINER = "RAED - fairbird"
LICENSE = "GPLv3"
LIC_FILES_CHKSUM = "file://LICENSE;md5=1ebbd3e34237af26da5dc08a4e440464"

SRC_URI = "git://github.com/fairbird/KeyAdder;protocol=https;branch=main"

inherit gitpkgv distutils-openplugins

RDEPENDS_${PN} += "\
	python-six \
	"

S = "${WORKDIR}/git"

SRCREV = "${AUTOREV}"

PV = "1.1+git${SRCPV}"
PKGV = "1.1+git${GITPKGV}"

FILES_${PN} = "${prefix}/"

do_install() {
	install -d ${D}${prefix}
	cp -r ${S}${prefix}/* ${D}${prefix}/
}

INSANE_SKIP_${PN} += "already-stripped"
