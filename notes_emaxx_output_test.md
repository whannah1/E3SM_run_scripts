


```shell
SRC_ROOT=/pscratch/sd/w/whannah/tmp_e3sm_src
TEST_MOD_ROOT=${SRC_ROOT}/components/eamxx/cime_config/testdefs/testmods_dirs/eamxx

# ------------------------------------------------------------------------------
# create instant output testmod
mkdir -p ${TEST_MOD_ROOT}/instant_ouput
cat <<EOF > ${TEST_MOD_ROOT}/instant_ouput/eamxx_output.1hr_instant.yaml
%YAML 1.1
---
filename_prefix: output.scream.2D.1hr
averaging_type: instant
max_snapshots_per_file: 2
fields:
   physics_pg2:
      field_names:
         - surf_sens_flux
output_control:
   frequency: 1
   frequency_units: nhours
restart:
   force_new_file: false
EOF

cat <<EOF > ${TEST_MOD_ROOT}/instant_ouput/shell_commands
file=${TEST_MOD_ROOT}/instant_ouput/eamxx_output.1hr_instant.yaml
cime_root=\$(./xmlquery --value CIMEROOT)
atmchange=\$cime_root/../components/eamxx/scripts/atmchange
# Copy yaml to case dir
cp -v \${file} ./
# Append to output list
\$atmchange -b output_yaml_files="./\$(basename \${file})"
EOF

# ------------------------------------------------------------------------------
# create average output testmod
mkdir -p ${TEST_MOD_ROOT}/average_ouput
cat <<EOF > ${TEST_MOD_ROOT}/average_ouput/eamxx_output.1hr_average.yaml
%YAML 1.1
---
filename_prefix: output.scream.2D.1hr
averaging_type: average
max_snapshots_per_file: 2
fields:
   physics_pg2:
      field_names:
         - surf_sens_flux
output_control:
   frequency: 1
   frequency_units: nhours
restart:
   force_new_file: false
EOF

cat <<EOF > ${TEST_MOD_ROOT}/average_ouput/shell_commands
file=${TEST_MOD_ROOT}/average_ouput/eamxx_output.1hr_average.yaml
cime_root=\$(./xmlquery --value CIMEROOT)
atmchange=\$cime_root/../components/eamxx/scripts/atmchange
# Copy yaml to case dir
cp -v \${file} ./
# Append to output list
\$atmchange -b output_yaml_files="./\$(basename \${file})"
EOF

# ------------------------------------------------------------------------------
# run the tests
${SRC_ROOT}/cime/scripts/create_test --test-root ${SRC_ROOT}/tests --output-root ${SRC_ROOT}/tests --project e3sm --wait -j2 SMS_Lh2.ne4pg2_oQU480.F2010-SCREAMv1.pm-cpu_intel.eamxx-instant_ouput SMS_Lh2.ne4pg2_oQU480.F2010-SCREAMv1.pm-cpu_intel.eamxx-average_ouput

${SRC_ROOT}/cime/scripts/create_test --test-root ${SRC_ROOT}/tests --output-root ${SRC_ROOT}/tests --project e3sm --wait -j2 SMS_Lh2.ne4pg2_oQU480.F2010-SCREAMv1.pm-gpu_gnugpu.eamxx-instant_ouput SMS_Lh2.ne4pg2_oQU480.F2010-SCREAMv1.pm-gpu_gnugpu.eamxx-average_ouput

```


```shell

grep "averaging_type" ${TEST_MOD_ROOT}/instant_ouput/eamxx_output.1hr_instant.yaml
grep "averaging_type" ${TEST_MOD_ROOT}/average_ouput/eamxx_output.1hr_average.yaml

cat ${TEST_MOD_ROOT}/instant_ouput/shell_commands
cat ${TEST_MOD_ROOT}/average_ouput/shell_commands

```

```shell
git reset --hard origin/master
git submodule sync ; git submodule update --init --recursive
git status
```