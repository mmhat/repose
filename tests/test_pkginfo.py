import pytest
from datetime import datetime
from repose import lib, ffi
from wrappers import Parser, ParserError, Package


REPOSE_PKGINFO = '''# Generated by makepkg 5.0.1
# using fakeroot version 1.21
# Sun Oct 30 16:09:47 UTC 2016
pkgname = repose-git
pkgver = 6.2.10.gbab93f3-1
pkgdesc = A archlinux repo building tool
url = http://github.com/vodik/repose
builddate = 1477843787
packager = Simon Gomizelj <simongmzlj@gmail.com>
size = 63488
arch = x86_64
license = GPL
conflict = repose
provides = repose
depend = pacman
depend = libarchive
depend = gnupg
makedepend = git
makedepend = ragel
'''


class PKGINFOParser(Parser):
    def init_parser(self):
        parser = ffi.new('struct pkginfo_parser*')
        lib.pkginfo_parser_init(parser)
        return parser

    def feed_parser(self, parser, pkg, data):
        return lib.pkginfo_parser_feed(parser, pkg, data, len(data))


@pytest.fixture
def parser():
    return PKGINFOParser()


@pytest.fixture
def pkg():
    return Package()


def test_parse_pkginfo(pkg, parser):
    parser.feed(pkg, REPOSE_PKGINFO)
    assert parser.entry == lib.PKG_MAKEDEPENDS

    assert pkg.base is None
    assert pkg.base64sig is None
    assert pkg.desc == 'A archlinux repo building tool'
    assert pkg.isize == 63488
    assert pkg.url == 'http://github.com/vodik/repose'
    assert pkg.arch == 'x86_64'
    assert pkg.builddate == "Oct 30, 2016, 16:09:47"
    assert pkg.packager == 'Simon Gomizelj <simongmzlj@gmail.com>'
    assert pkg.licenses == ['GPL']


@pytest.mark.parametrize('chunksize', [1, 10, 100])
def test_parse_chunked(pkg, parser, chunksize):
    def chunk(data, size):
        return (data[i:i+size] for i in range(0, len(data), size))

    for chunk in chunk(REPOSE_PKGINFO, chunksize):
        parser.feed(pkg, chunk)

    assert pkg.base is None
    assert pkg.base64sig is None
    assert pkg.desc == 'A archlinux repo building tool'
    assert pkg.isize == 63488
    assert pkg.url == 'http://github.com/vodik/repose'
    assert pkg.arch == 'x86_64'
    assert pkg.builddate == "Oct 30, 2016, 16:09:47"
    assert pkg.packager == 'Simon Gomizelj <simongmzlj@gmail.com>'
    assert pkg.licenses == ['GPL']


def test_pkginfo_with_backup(pkg, parser):
    parser.feed(pkg, '''pkgname = example
backup = etc/example/conf
''')


def test_invalid_pkginfo_entry(pkg, parser):
    with pytest.raises(ParserError):
        parser.feed(pkg, '''pkgname = example
badentry = etc/example/conf
''')
