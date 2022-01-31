# type: ignore
from versioning.version import Version


def test_versioning():
    v = Version('1.0.0')
    assert v.state == 'final'
    assert v.major == 1
    assert v.minor == 0
    assert v.micro == 0
    v.bump_major()
    assert str(v) == '2.0.0'
    v.bump_minor()
    assert str(v) == '2.1.0'
    v.bump_micro()
    assert str(v) == '2.1.1'


def test_devrelease():
    v = Version('1.0.0', enable_prereleases=False)
    assert v.enable_prereleases is False
    v.start_devrelease()
    assert v == Version('1.1.0.dev0')
    v.bump_release()
    assert str(v) == '1.1.0.dev1'
    v.finish_release()
    assert str(v) == '1.1.0'


def test_devrelease_state():
    v = Version('1.0.0', enable_prereleases=False)
    assert v.enable_prereleases is False
    assert v.state == 'final'
    v.start_devrelease()
    assert v.state == 'development'
    v.finish_release()
    assert v.state == 'final'


def test_prerelease():
    v = Version('2.0.0', enable_devreleases=False)
    assert v.state == 'final'
    v.start_alpha(kind='major')
    assert str(v) == '3.0.0a0'
    assert v.pre == ('a', 0)
    v.bump_release()
    assert str(v) == '3.0.0a1'
    v.start_beta()
    assert str(v) == '3.0.0b0'
    v.bump_release()
    assert str(v) == '3.0.0b1'
    v.start_release()
    assert str(v) == '3.0.0rc0'
    v.bump_release()
    assert str(v) == '3.0.0rc1'


def test_prerelease_states():
    v = Version('1.0.0', enable_devreleases=False)
    assert v.state == 'final'
    v.start_alpha()
    assert v.state == 'alpha'
    v.start_beta()
    assert v.state == 'beta'
    v.start_release()
    assert v.state == 'release'
    v.finish_release()
    assert v.state == 'final'


def test_post():
    v = Version('2.0.0')
    assert v.state == 'final'
    v.start_postrelease()
    assert v.release == (2, 0, 0)
    assert v.base_version == '2.0.0'
    assert v.major == 2
    assert v.minor == 0
    assert v.micro == 0
    assert v.state == 'post'
    v.bump_release()
    assert v.state == 'post'
    v.bump_major()
    assert v.state == 'development'


def test_post_state():
    v = Version('2.0.0')
    assert v.state == 'final'

    v.start_postrelease()
    assert v.state == 'post'


def test_local():
    v = Version('3.0.0+1234567')
    assert v.release == (3, 0, 0)
    assert v.pre is None
    assert v.post is None
    assert v.local == '1234567'
    v.bump_major()
    assert str(v) == '4.0.0'


def test_local_state():
    v = Version('1.0.0')
    assert v.state == 'final'

    v1 = Version(f"{str(v)}+build.0")
    assert v1.local == 'build.0'
    assert v1.state == 'final'

    v.new_local('4321')
    assert v == Version('1.0.0+4321')
    assert v.local == '4321'
    assert v.state == 'final'

    # TODO: assert build is gone after bump


def test_local_removed():
    v = Version('1.0.0+build.0')
    assert v.local == 'build.0'
    v.state == 'final'

    # ensure local version is removed from development
    v.start_devrelease()
    v = Version('1.0.0.dev')
    assert v.state == 'development'
    assert v.local is None

    # ensure local version is removed from final
    v = Version('1.0.0+build.0')
    v.bump_minor()
    assert v.state == 'development'
    assert v.local is None


def test_mixed():
    # TODO: getting warning due to both
    v = Version('5.0.0-rc5+build254')
    assert v.state == 'release'
    assert v.local == 'build254'


def test_epoch():
    v = Version('1!6.0.0')
    assert v.state == 'final'
    assert v.epoch == 1
    v.bump_epoch()
    assert str(v) == '2!6.0.0'
