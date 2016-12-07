try:
    from urllib import urlretrieve
except ImportError:
    from urllib.request import urlretrieve

import os.path
import re
import shutil
from subprocess import check_output

from tito.common import chdir, find_git_root, get_build_commit, get_commit_count, get_latest_commit, munge_specfile
from tito.builder.fetch import SourceStrategy
from tito.builder.fetch import FetchBuilder as TitoFetchBuilder

SOURCE_REGEX = re.compile("^(source[0-9]+:\s*)(.+)$", re.IGNORECASE)

RELEASE_REGEX = re.compile("^(release:\s*)(.+)$", re.IGNORECASE)
VERSION_REGEX = re.compile("^(version:\s*)(.+)$", re.IGNORECASE)


class FetchBuilder(TitoFetchBuilder):
    def __init__(self, tag=None, *args, **kwargs):
        TitoFetchBuilder.__init__(self, tag=tag, *args, **kwargs)
        self.build_tag = tag

        with chdir(find_git_root()):
            self.git_commit_id = get_build_commit(tag=self.build_tag,
                                                  test=self.test)

        if self.test:
            # should get latest commit for given directory *NOT* HEAD
            latest_commit = get_latest_commit(".")
            self.commit_count = get_commit_count(self.build_tag, latest_commit)

        # Used to make sure we only modify the spec file for a test build
        # once. The srpm method may be called multiple times during koji
        # releases to create the proper disttags, but we only want to modify
        # the spec file once.
        self.ran_setup_test_specfile = False


    def _setup_test_specfile(self):
        self.spec_file = os.path.join(self.start_dir,
                                      '%s.spec' % self.project_name)

        if self.test and not self.ran_setup_test_specfile:
            # Copy the spec to the sourcedir to avoid muning the original
            new_spec_file = os.path.join(self.rpmbuild_sourcedir,
                                          '%s.spec' % self.project_name)
            shutil.copyfile(self.spec_file, new_spec_file)
            self.spec_file = new_spec_file

            # If making a test rpm we need to get a little crazy with the spec
            # file we're building off. (note that this is a temp copy of the
            # spec) Swap out the actual release for one that includes the git
            # SHA1 we're building for our test package:
            sha = self.git_commit_id[:7]
            munge_specfile(
                self.spec_file,
                sha,
                self.commit_count,
            )

            self.ran_setup_test_specfile = True        


class DownloadSourceStrategy(SourceStrategy):
    def fetch(self):
        self.spec_file = os.path.join(self.builder.start_dir,
                                      '%s.spec' % self.builder.project_name)
        parsed_spec = check_output('rpmspec -P %s' % self.spec_file,
                                   shell=True).decode()

        sources = []
        for line in parsed_spec.split('\n'):
            m = SOURCE_REGEX.match(line)
            if m:
                sources.append(m.group(2))

            m = RELEASE_REGEX.match(line)
            if m:
                self.release = m.group(2)

            m = VERSION_REGEX.match(line)
            if m:
                self.version = m.group(2)

        for source in sources:
            if source.startswith('http://') or source.startswith('https://'):
                base_name = source.split('/')[-1]
                filename = os.path.join(self.builder.rpmbuild_sourcedir,
                                        base_name)
                urlretrieve(source, filename)
            else:
                base_name = os.path.basename(source)
                filename = os.path.join(self.builder.rpmbuild_sourcedir,
                                        base_name)
                shutil.copyfile(source, filename)

            self.sources.append(filename)
