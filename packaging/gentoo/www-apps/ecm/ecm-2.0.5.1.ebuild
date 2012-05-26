# Copyright 1999-2012 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: $

EAPI=3

DESCRIPTION="ECM is a management and decision-making helper-application for the game EVE Online."
HOMEPAGE="http://eve-corp-management.org/"
SRC_URI="http://releases.eve-corp-management.org/src/${P}.tar.gz"


PYTHON_DEPEND="2:2.5"
SUPPORT_PYTHON_ABIS="1"
RESTRICT_PYTHON_ABIS="3.*"

inherit distutils


LICENSE="GPL-3"
SLOT="0"
KEYWORDS="~amd64"
IUSE=""

DEPEND="		${RDEPEND}
                dev-python/distutils"
                
RDEPEND="       dev-python/django
                dev-python/imaging
                dev-python/south
                dev-python/django-simple-captcha
                dev-python/django-compressor"

