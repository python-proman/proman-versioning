# type: ignore
from proman_releases.version import PythonVersion


def test_versioning():
    v = PythonVersion('1.0.0')
    assert v.get_state() == 'final'
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
    v = PythonVersion('1.0.0', enable_devreleases=True)
    v.start_devrelease()
    assert str(v) == '1.1.0.dev0'
    v.finish_release()
    assert str(v) == '1.1.0'


def test_devrelease_state():
    v = PythonVersion('1.0.0', enable_devreleases=True)
    assert v.get_state() == 'final'
    v.start_devrelease()
    assert v.get_state() == 'development'
    v.finish_release()
    assert v.get_state() == 'final'


def test_prerelease():
    v = PythonVersion('2.0.0', enable_prereleases=True)
    assert v.get_state() == 'final'
    v.start_prerelease()
    assert str(v) == '3.0.0a0'
    assert v.pre == ('a', 0)
    v.bump_prerelease()
    assert str(v) == '3.0.0a1'
    v.start_prerelease()
    assert str(v) == '3.0.0b0'
    v.bump_prerelease()
    assert str(v) == '3.0.0b1'
    v.start_prerelease()
    assert str(v) == '3.0.0rc0'
    v.bump_prerelease()
    assert str(v) == '3.0.0rc1'


def test_prerelease_states():
    v = PythonVersion('1.0.0', enable_prereleases=True)
    assert v.get_state() == 'final'
    v.start_prerelease()
    assert v.get_state() == 'prerelease'
    v.start_prerelease()
    assert v.get_state() == 'prerelease'
    v.start_prerelease()
    assert v.get_state() == 'prerelease'
    v.finish_release()
    assert v.get_state() == 'final'


def test_post():
    v = PythonVersion('2.0.0', enable_postreleases=True)
    assert v.get_state() == 'final'
    v.start_postrelease()
    assert v.release == (2, 0, 0)
    assert v.base_version == '2.0.0'
    assert v.major == 2
    assert v.minor == 0
    assert v.micro == 0
    assert v.get_state() == 'post'
    v.bump_postrelease()
    assert v.get_state() == 'post'
    v.bump_major()
    assert v.get_state() == 'final'


def test_post_state():
    v = PythonVersion('2.0.0', enable_postreleases=True)
    assert v.get_state() == 'final'

    v.start_postrelease()
    assert v.get_state() == 'post'


def test_local():
    v = PythonVersion('3.0.0+dev4.post3')
    assert v.release == (3, 0, 0)
    assert v.pre is None
    assert v.post is None
    assert v.local == 'dev4.post3'
    v.bump_major()
    assert str(v) == '4.0.0'


def test_local_state():
    v = PythonVersion('1.0.0')
    assert v.get_state() == 'final'

    v.start_local()
    assert v.local == 'build.0'
    v.get_state() == 'final'

    v.bump_local()
    assert v.local == 'build.1'


def test_mixed():
    # TODO: getting warning due to both
    v = PythonVersion('5.0.0-rc5+build254')
    assert v.get_state() == 'prerelease'
    assert v.local == 'build254'


def test_epoch():
    v = PythonVersion('1!6.0.0')
    assert v.get_state() == 'final'
    assert v.epoch == 1
    v.bump_epoch()
    assert str(v) == '2!6.0.0'
