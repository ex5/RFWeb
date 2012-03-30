#
# spec file for package 'dscheduler (version '0.1')
#

# Basic Information
Name: dscheduler
Version: 0.1
Release: 1
Summary: Simple test scheduler with UI based on cdialog
Group: dscheduler 
License: LGPL
BuildArch: noarch
#URL:

# Packager Information
#Packager:

# Build Information
BuildRoot: %{_topdir}/BUILD/%{name}-%{version}

# Source Information
Source: %{name}-%{version}.tar.gz

# Dependency Information
#BuildRequires:
Requires: python dialog 

%description
%{summary}

%prep
echo "prep"
%setup -q

%build
echo "build"

%install
echo "install"
cp -a %{_topdir}/BUILD/%{name}-%{version}/usr %{_tmppath}/%{name}-root

%clean
echo "clean"

%post
echo "post"

%postun
echo "postrun"

%files
#%defattr(-,root,root,-)
%dir /usr/share/dscheduler/
/usr/share/dscheduler/.dialogrc*
/usr/share/dscheduler/*
#%doc

%changelog
* Fri Feb 3 2012 Anna Sirota <anna.sirota@t-platforms.ru>
nothing'd really changed though
