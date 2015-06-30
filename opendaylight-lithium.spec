%define __jar_repack 0

Name: opendaylight-lithium
Summary: OpenDaylight SDN Controller
Version: 0
Release: 1
Source0: https://nexus.opendaylight.org/content/repositories/public/org/opendaylight/integration/distribution-karaf/0.3.0-Lithium/distribution-karaf-0.3.0-Lithium.tar.gz
Source1: opendaylight-lithium.service
Patch0: 0001-opendaylight-lithium-remove-credentials.patch
Group: Applications/Communications
License: EPL-1.0
URL: http://www.opendaylight.org
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Requires: java-devel >= 1.7.0
Requires(pre): shadow-utils, glibc-common
Requires(postun): shadow-utils
BuildRequires: systemd
Conflicts: opendaylight-helium

# this is used to identify if we need to remove the odl user/group when
# removing
Provides: opendaylight

%pre
%global odl_user odl
%global odl_home /opt/opendaylight

# Create odl user/group
getent passwd %{odl_user} > /dev/null \
    || useradd --system --home-dir %{odl_home} %{odl_user}
getent group %{odl_user} > /dev/null \
    || groupadd --system %{odl_user}

# disable debug packages and the stripping of the binaries
%global _enable_debug_package 0
%global debug_package %{nil}
%global __os_install_post /usr/lib/rpm/brp-compress %{nil}

%description
OpenDaylight is an open platform for network programmability to enable SDN and create a solid foundation for NFV for networks at any size and scale.

%prep
ROOT_DIR=$(dirname $(tar -tf %{SOURCE0} | head -n 1))
%autosetup -N -c -n %{name}
mv ${ROOT_DIR}/* .
rm -rf ${ROOT_DIR}
%autopatch -p0

%build

%install
install -d %{buildroot}/%{odl_home}
cp -R %{_builddir}/%{name} %{buildroot}/%{odl_home}
install -D %{SOURCE1} %{buildroot}/%{_unitdir}/%{name}.service

%clean
rm -rf %
 
%post
%systemd_post %{name}.service

%postun
%systemd_postun_with_restart %{name}.service

# remove installed files
rm -rf %{odl_home}/%{name}

# remove odl user/group if no other opendaylight package is installed
rpmquery --query --whatprovides opendaylight > /dev/null \
    || { userdel %{odl_user} && groupdel %{odl_user}; }

%files
# ODL uses systemd to run as user:group odl:odl
%attr(0775,odl,odl) %{odl_home}/%{name}
%attr(0644,-,-) %{_unitdir}/%{name}.service

%changelog
* Tue Jun 30 2015 David Jorm - 0-1
- Initial creation
