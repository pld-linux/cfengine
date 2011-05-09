# TODO
# - precise texinfo deps
# - pldize initscript
# - FHS
Summary:	A systems administration tool for networks
Name:		cfengine
Version:	3.0.5p1
Release:	0.1
License:	GPL v3
Group:		Applications/System
Source0:	http://www.cfengine.org/tarballs/%{name}-%{version}.tar.gz
# Source0-md5:	b74af23928253e11dcce3d98510f1066
Source1:	cf-execd
Source2:	cf-serverd
Source3:	cf-monitord
URL:		http://www.cfengine.org/
BuildRequires:	acl-devel
BuildRequires:	bison
BuildRequires:	db-devel
BuildRequires:	flex
BuildRequires:	libselinux-devel
BuildRequires:	m4
BuildRequires:	openssl-devel
BuildRequires:	pcre-devel
BuildRequires:	tetex-dvips
Requires(post,preun):	/sbin/chkconfig
Requires:	rc-scripts
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Cfengine, or the configuration engine is an agent/software robot and a
very high level language for building expert systems to administrate
and configure large computer networks. Cfengine uses the idea of
classes and a primitive form of intelligence to define and automate
the configuration and maintenance of system state, for small to huge
configurations. Cfengine is designed to be a part of a computer immune
system.

%package doc
Summary:	Documentation for cfengine
Group:		Documentation
Requires:	%{name} = %{version}-%{release}

%description doc
This package contains the documentation for cfengine.

%prep
%setup -q

%build
%configure \
	BERKELEY_DB_LIB=-ldb \
	--docdir=%{_docdir}/%{name}-%{version} \
	--enable-selinux
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sbindir},%{_datadir}/%{name}}
%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

# make directory tree for cfengine configs
install -d $RPM_BUILD_ROOT%{_var}/%{name}
for i in ppkeys inputs outputs; do
	mkdir -m 0700 $RPM_BUILD_ROOT%{_var}/%{name}/$i
done

# It's ugly, but thats the way Mark wants to have it. :(
# If we don't create this link, cfexecd will not be able to start
# (hardcoded) /var/sbin/cf-agent in scheduled intervals. Other option
# would be to patch cfengine to use %{_sbindir}/cf-agent
# but upstream won't support this
install -d $RPM_BUILD_ROOT%{_var}/%{name}/bin
ln -sf %{_sbindir}/cf-agent $RPM_BUILD_ROOT%{_var}/%{name}/bin
ln -sf %{_sbindir}/cf-promises $RPM_BUILD_ROOT%{_var}/%{name}/bin

# init scripts
install -d $RPM_BUILD_ROOT/etc/rc.d/init.d
for i in %{SOURCE1} %{SOURCE2} %{SOURCE3}; do
	install -p -m 0755 $i $RPM_BUILD_ROOT/etc/rc.d/init.d
done

rm -f $RPM_BUILD_ROOT%{_infodir}/dir

# All this stuff is pushed into doc/contrib directories
rm -rf $RPM_BUILD_ROOT%{_datadir}/%{name}
rm -f $RPM_BUILD_ROOT%{_sbindir}/cfdoc

%clean
rm -rf $RPM_BUILD_ROOT

%post
[ ! -x /usr/sbin/fix-info-dir ] || /usr/sbin/fix-info-dir -c %{_infodir} >/dev/null 2>&1

# cfagent won't run nicely, unless your host has keys.
if [ ! -d /mnt/sysimage -a ! -f %{_var}/%{name}/ppkeys/localhost.priv ]; then
	%{_sbindir}/cf-key >/dev/null || :
fi

# add init files to chkconfig
/sbin/chkconfig --add cf-monitord
/sbin/chkconfig --add cf-execd
/sbin/chkconfig --add cf-serverd
%service cf-monitord restart
%service cf-execd restart
%service cf-serverd restart

%preun
if [ "$1" = "0" ]; then
	%service cf-monitord stop
	%service cf-execd stop
	%service cf-serverd stop
	/sbin/chkconfig --del cf-monitord
	/sbin/chkconfig --del cf-execd
	/sbin/chkconfig --del cf-serverd
fi

%postun
[ ! -x /usr/sbin/fix-info-dir ] || /usr/sbin/fix-info-dir -c %{_infodir} >/dev/null 2>&1

%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog README TODO
%attr(755,root,root) %{_sbindir}/*
%{_libdir}/libpromises*
%{_mandir}/man8/*
%attr(754,root,root) /etc/rc.d/init.d/cf-monitord
%attr(754,root,root) /etc/rc.d/init.d/cf-execd
%attr(754,root,root) /etc/rc.d/init.d/cf-serverd
%{_var}/%{name}

%files doc
%defattr(644,root,root,755)
%doc inputs
%doc docs/*html
%doc docs/*pdf
