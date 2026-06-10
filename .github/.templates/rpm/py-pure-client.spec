%global pypi_name ${NAME}
%global sdist_name ${SDIST_NAME}
%global module_name ${MODULE_NAME}

Name:           python3-%{module_name}
Version:        ${VERSION}
Release:        ${BUILD_NUM}%{?dist}
Summary:        ${SUMMARY}

License:        BSD-2-Clause
URL:            ${HOMEPAGE}
Source0:        %{sdist_name}-%{version}.tar.gz

BuildArch:      noarch

%global __brp_python_bytecompile %nil

BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros

Provides:       python3-%{pypi_name} = %{version}-%{release}

%global _description %{expand:
${SUMMARY}}

%description %_description

%prep
%autosetup -n %{sdist_name}-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
find %{buildroot} -type d -name __pycache__ -exec rm -rf {} +

%check
%{python3} -c "import %{module_name}"

%files
%license LICENSE.txt
%doc README.md
%{python3_sitelib}/%{module_name}/
%{python3_sitelib}/%{sdist_name}-*.dist-info/

%changelog
* ${BUILD_DATE} ${MAINTAINER} - ${VERSION}-${BUILD_NUM}
- Release ${VERSION}
