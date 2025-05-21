

# TEST=SMS_Ln4_P168x1.ne4pg2_ne4pg2.F-MMF1.summit_gnu
# TEST=SMS_Ln4_P168x1.ne4pg2_ne4pg2.F-MMF1.summit_gnu.eam-genmmf
# TEST=SMS_Ln4_P168x1.ne4pg2_ne4pg2.FC5AV1C-L.summit_gnu
ID=00
cime/scripts/create_test $TEST --test-id=$ID -r ./ --no-setup
TEST_NAME=${TEST}.${ID}
cd ${TEST_NAME}
./xmlchange REST_OPTION=nsteps
./xmlchange RESUBMIT=1
./case.setup && ./case.build && ./case.submit




# Test the effect of not setting REST_OPTION=never
TEST=ERS_Ln4_P168x1.ne4pg2_ne4pg2.FC5AV1C-L.summit_gnu
ID=01
cime/scripts/create_test $TEST --test-id=$ID -r ./ --no-setup
TEST_NAME=${TEST}.${ID}
cd ${TEST_NAME}
./case.setup && ./case.build && ./case.submit