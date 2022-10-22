# Copyright (c) 2022 Canonical Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from semver import VersionInfo

UNKNOWN_VERSION = VersionInfo(0, 0, 0)


def has_superuser_privileges() -> bool:
    """Determines if the current user has superuser privileges.

    This method will return True if the effective UID is 0. This should work
    for standard linux distributions.

    :return: True if the current user has superuser privileges, False otherwise
    :rtype: bool
    """
    return os.geteuid() == 0


def parse_version(version: str) -> VersionInfo:
    """Parse the version string and return a semver.VersionInfo.

    Attempts tot parse the version string and return a semver.VersionInfo.
    However, not all the versions that we will find conform to the semantic
    versioned strings. This method will attempt to provide a few known
    adjustments (such as expanding to MAJOR.MINOR.PATCH for versions that only
    have MAJOR.MINOR).

    In the event that the string cannot be coerced to be a valid semantic
    versioning form, this method will raise a ValueError indicating that it
    cannot parse the version.

    :param version: the version string to prase
    :type version: str
    :return: the semver.VersionInfo containing the versioning information
    :rtype: VersionInfo
    """
    try:
        return VersionInfo.parse(version)
    except ValueError:
        # Microk8s prefixes its version info with a 'v'. Let's strip it and get
        # rid of it.
        if version[0] == "v":
            return VersionInfo.parse(version[1:])

        # Juju uses 3.0 instead of 3.0.0 for major releases, so attempt to
        # convert it into a 3.0.0 (and include any pre-release information).
        if version.count(".") == 1:
            parts = version.split("-")
            new_version = f"{parts[0]}.0-{parts[1]}"
            return VersionInfo.parse(new_version)

        # Not a known condition, let's just re-raise.
        raise