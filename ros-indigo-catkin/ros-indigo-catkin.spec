#
# spec file for package catkin
#
# Copyright (c) 2010 SUSE LINUX Products GmbH, Nuernberg, Germany.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#

# norootforbuild

Name:           ros-indigo-catkin
Version:        0.6.18
Release:        0%{?dist}
Summary:        Low-level build system macros and infrastructure for ROS

License:        BSD
URL:            http://www.ros.org/wiki/catkin
Source0:        https://github.com/ros-gbp/catkin-release/archive/upstream/%{version}.zip

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  gtest-devel
BuildRequires:  python-argparse
BuildRequires:  python-catkin_pkg
BuildRequires:  python-empy
BuildRequires:  python-nose

Requires:       cmake
Requires:       gcc-c++
Requires:       gtest-devel
Requires:       python-argparse
Requires:       python-catkin_pkg
Requires:       python-empy
Requires:       python-nose

BuildArch:      noarch

%description
Low-level build system macros and infrastructure for ROS.

%package devel
Summary:        Development package for catkin
Group:          Development/Libraries/C and C++

%description devel
Development package for catkin.

%prep
%setup -q -n catkin-release-upstream-%{version}
#%patch0 -p1

mkdir ../catkin
mv * ../catkin

mkdir -p src/catkin
mv ../catkin src

%build
./src/catkin/bin/catkin_make -DSETUPTOOLS_DEB_LAYOUT="OFF" \
                             -DCATKIN_PACKAGE_LIB_DESTINATION=%{_libdir} \
                             -DCMAKE_INSTALL_PREFIX=%{_prefix}

%install
./src/catkin/bin/catkin_make install -DCMAKE_INSTALL_PREFIX=%{_prefix} DESTDIR=%{buildroot}

root=%{buildroot}/%{_prefix}
rm ${root}/.catkin
rm ${root}/.rosinstall
rm ${root}/env.sh
rm ${root}/_setup_util.py
rm ${root}/setup.*
mv ${root}/lib/pkgconfig ${root}/share/lib

%files
%defattr(-,root,root,-)
%{_bindir}/*
%{_datadir}/*
%{python_sitelib}/*

%changelog
* Tue Dec 07 2016 Scott Dial <scott.dial@scientiallc.com> 0.6.18-0
- New package built with tito
