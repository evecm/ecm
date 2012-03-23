# Copyright 1999-2012 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: $

EAPI=3

DESCRIPTION="Eve Corporation Management is a django app for various corporation
wide task in the MMO EVE Online"
HOMEPAGE="http://code.google.com/p/eve-corp-management/"
EHG_REPO_URI="https://code.google.com/p/eve-corp-management/"

PYTHON_DEPEND="2"
SUPPORT_PYTHON_ABIS="1"
RESTRICT_PYTHON_ABIS="3.*"

inherit distutils mercurial


LICENSE="GPL-3"
SLOT="0"
KEYWORDS="~amd64"
IUSE=""

DEPEND="${RDEPEND}
                dev-python/django
                dev-python/imaging
                dev-python/south
                dev-python/distutils"
RDEPEND="
                dev-python/django
                dev-python/imaging
                dev-python/south"

