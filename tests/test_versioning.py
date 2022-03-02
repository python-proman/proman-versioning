# type: ignore
"""Test versioning capability."""

from versioning.version import Version


def test_versioning():
    """Test capability to bump versions."""
    v = Version('1.0.0', autostart_default_release=False)
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
    """Test development releases."""
    v = Version('1.0.0', enable_prereleases=False)
    assert v.default_release_type == 'dev'
    assert v.enable_prereleases is False
    v.start_release(segment='minor')
    assert v == Version('1.1.0.dev0')
    v.bump_release()
    assert str(v) == '1.1.0.dev1'
    v.start_release()
    assert str(v) == '1.1.0'


def test_devrelease_state():
    """Test development release state."""
    v = Version('1.0.0', enable_prereleases=False)
    assert v.default_release_type == 'dev'
    assert v.enable_prereleases is False
    assert v.state == 'final'
    v.start_release()
    assert v.state == 'dev'
    v.start_release()
    assert v.state == 'final'


def test_prerelease():
    """Test pre-releases."""
    v = Version('2.0.0', enable_devreleases=False)
    assert v.default_release_type == 'alpha'
    assert v.state == 'final'
    v.start_release(segment='major')
    assert str(v) == '3.0.0a0'
    assert v.pre == ('a', 0)
    v.bump_release()
    assert str(v) == '3.0.0a1'
    v.start_release()
    assert str(v) == '3.0.0b0'
    v.bump_release()
    assert str(v) == '3.0.0b1'
    v.start_release()
    assert str(v) == '3.0.0rc0'
    v.bump_release()
    assert str(v) == '3.0.0rc1'


def test_prerelease_states():
    """Test pre-release states."""
    v = Version('1.0.0', enable_devreleases=False)
    assert v.default_release_type == 'alpha'
    assert v.state == 'final'
    v.start_release()
    assert v.state == 'alpha'
    v.start_release()
    assert v.state == 'beta'
    v.start_release()
    assert v.state == 'candidate'
    v.start_release()
    assert v.state == 'final'


def test_post():
    """Test post-release version bump."""
    v = Version('2.0.0', autostart_default_release=True)
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
    assert v.state == 'dev'


def test_post_state():
    """Test post-release state."""
    v = Version('2.0.0')
    assert v.state == 'final'

    v.start_postrelease()
    assert v.state == 'post'


def test_local():
    """Test local version update."""
    v = Version('3.0.0+1234567', autostart_default_release=False)
    assert v.release == (3, 0, 0)
    assert v.pre is None
    assert v.post is None
    assert v.local == '1234567'
    v.bump_major()
    assert str(v) == '4.0.0'


def test_local_state():
    """Test local version state."""
    v = Version('1.0.0')
    assert v.state == 'final'

    v1 = Version(f"{str(v)}+build.0")
    assert v1.local == 'build.0'
    assert v1.state == 'final'

    v._new_local('4321')
    assert v == Version('1.0.0+4321')
    assert v.local == '4321'
    assert v.state == 'final'

    # TODO: assert build is gone after bump


def test_local_removed():
    """Test removal of local version."""
    v = Version('1.0.0+build.0')
    assert v.local == 'build.0'
    v.state == 'final'

    # ensure local version is removed from development
    v.start_release()
    v = Version('1.0.0.dev')
    assert v.state == 'dev'
    assert v.local is None

    # ensure local version is removed from final
    v = Version('1.0.0+build.0', autostart_default_release=True)
    v.bump_minor()
    assert v.state == 'dev'
    assert v.local is None


def test_mixed():
    """Test mixed versions."""
    # TODO: getting warning due to both
    v = Version('5.0.0-rc5+build254')
    assert v.state == 'candidate'
    assert v.local == 'build254'


def test_epoch():
    """Test epoch version bump."""
    v = Version('1!6.0.0')
    assert v.state == 'final'
    assert v.epoch == 1
    v.bump_epoch()
    assert str(v) == '2!6.0.0'
