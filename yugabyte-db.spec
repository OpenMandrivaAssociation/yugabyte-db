Name: yugabyte-db
Version: 2.17.2.0
Release: 1
Source0: https://github.com/yugabyte/yugabyte-db/archive/refs/tags/v%{version}.tar.gz
Source1: https://github.com/yugabyte/yugabyte-bash-common/archive/refs/heads/master.tar.gz#/yugabyte-bash-common.tar.gz
Source2: https://github.com/yugabyte/yugabyte-db-thirdparty/archive/refs/heads/master.tar.gz#/yugabyte-db-thirdparty.tar.gz
Patch0: fix-worst-build-system-offenses.patch
Summary: Distributed SQL database
URL: https://github.com/yugabyte/yugabyte-db
License: Apache-2.0
Group: Servers
BuildRequires: cmake ninja
BuildRequires: pkgconfig(libssl)
BuildRequires: pkgconfig(libglog)
BuildRequires: %mklibname cds-s -d -s

%description
High-performance, cloud-native, distributed SQL database that aims to support
all PostgreSQL features. It is best suited for cloud-native OLTP (i.e.,
real-time, business-critical) applications that need absolute data correctness
and require at least one of the following: scalability, high tolerance to
failures, or globally-distributed deployments.

%prep
%setup -q -a 1 -a 2
export YB_DEBUG_BUILD_ROOT_BASENAME_PARSING=1
mkdir build
mv yugabyte-bash-common-master build/yugabyte-bash-common
mv yugabyte-db-thirdparty-master thirdparty
%autopatch -p1

# The idiotic build system requires compiler names to end in
# "/compiler-wrappers/cc" or "/compiler-wrappers/c++". So let's
# give it what it wants without doing anything super dumb...
mkdir compiler-wrappers
ln -s %{__cc} compiler-wrappers/cc
ln -s %{__cxx} compiler-wrappers/c++

# We don't want any thirdparty mess. That's what system libs are there for...
# Let's just hack around the *****ing stupid build system.
export NO_REBUILD_THIRDPARTY=1
mkdir -p thirdparty/installed/uninstrumented/libcxx/include/c++/v1 \
	thirdparty/installed/uninstrumented/libcxx/lib

export CMAKE_BUILD_DIR=release-clang16-full-lto-x86_64-ninja

%cmake \
	-DCMAKE_C_COMPILER=$(pwd)/../compiler-wrappers/cc \
	-DCMAKE_CXX_COMPILER=$(pwd)/../compiler-wrappers/c++ \
	-DGLOG_SHARED_LIB=%{_libdir}/libglog.so \
	-DGLOG_INCLUDE_DIR=%{_includedir}/glog \
	-DCDS_SHARED_LIB=%{_libdir}/libcds.so \
	-DCDS_STATIC_LIB=%{_libdir}/libcds-s.a \
	-DCDS_INCLUDE_DIR=%{_includedir}/cds \
	-DREBUILD_THIRDPARTY:BOOL=OFF \
	-G Ninja

%build
%ninja_build -C release-clang16-full-lto-x86_64-ninja

%install
%ninja_install -C release-clang16-full-lto-x86_64-ninja

%files
# Leaving the "/" in here is _BAD_, but will generally work [packaging all
# files] for testing.
# Please replace it with an actual file list to prevent your package from
# owning all system directories.
/
