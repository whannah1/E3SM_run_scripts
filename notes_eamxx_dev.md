
## using CPP macros in EAMxx

These notes came from the implicit momentum flux PR. We didn't end up needing to use any CPP macros,
but I wanted to capture Luca's suggestion for future use 

### components/eamxx/src/mct_coupling/eamxx_cpl_indices.F90

```f90
#ifdef XXX
  integer, parameter, public :: num_scream_exports = 20
#else
  integer, parameter, public :: num_scream_exports = 17
#endif
```

### components/eamxx/cime_config/buildlib_cmake

```python
def buildlib(bldroot, installpath, case):
  (...)
    xxx = case.get_value("ATM_FLUX")
    if xxx:
        cmake_args += " -DEAMXX_IMPLICIT_FLUX=ON"

    print("scream cmake options: '{}'".format(cmake_args))

    return cmake_args
```

### components/eamxx/src/share/core/CMakeLists.txt

```cmake
if (EAMXX_IMPLICIT_FLUX)
  target_compile_definitions(eamxx_core PUBLIC EAMXX_IMPLICIT_FLUX )
endif()
```