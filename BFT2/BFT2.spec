#
# spec file for package 'BTF2 (version '0.1')
#

# Basic Information
Name: BFT2
Version: 0.1
Release: 1
Summary: Simple test scheduler with UI based on cdialog
Group: BTF2 
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
Requires: python dialog robotframework pyserial pythondialog

%description
%{summary}

%prep
echo "prep"
%setup -q

%build
echo "build"

%install
echo "install"
pwd 
tar -C %{_tmppath}/%{name}-root/robotframework-2.6.3 -zxvf roboframework-2.6.3.tar.gz
cp -a %{_topdir}/BUILD/%{name}-%{version}/opt %{_tmppath}/%{name}-root

%clean
echo "clean"

%post
echo "post"

%postun
# TODO
echo "postrun"
pwd 
cd robotframework-2.6.3
cp ../opt/cDialog.py src/robot/libraries/Dialogs.py
python install.py install

%files
#%defattr(-,root,root,-)
%dir /opt/BFT2/
/opt/BFT2/.dialogrc*
/opt/BFT2/*
#%doc

%changelog
* Fri Feb 3 2012 Anna Sirota <anna.sirota@t-platforms.ru>
nothing'd really changed though
