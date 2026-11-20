if(NOT DEFINED TEST_PROGRAM OR TEST_PROGRAM STREQUAL "")
    message(FATAL_ERROR "TEST_PROGRAM is required")
endif()
if(NOT EXISTS "${TEST_PROGRAM}")
    message(FATAL_ERROR "cross-process test executable does not exist: ${TEST_PROGRAM}")
endif()
if(NOT DEFINED WORK_ROOT OR WORK_ROOT STREQUAL "")
    message(FATAL_ERROR "WORK_ROOT is required")
endif()

string(RANDOM LENGTH 16 ALPHABET 0123456789abcdef run_token)
file(MAKE_DIRECTORY "${WORK_ROOT}")
set(checkpoint "${WORK_ROOT}/cross-process-checkpoint-${run_token}.deetsnap")
set(future_reference "${WORK_ROOT}/cross-process-future-${run_token}.deetsnap")

# execute_process calls are deliberately sequential. The producer has exited
# before the consumer starts, so the test cannot pass through in-memory state.
execute_process(
    COMMAND "${TEST_PROGRAM}" produce "${checkpoint}" "${future_reference}"
    RESULT_VARIABLE producer_result
    OUTPUT_VARIABLE producer_output
    ERROR_VARIABLE producer_error)
if(NOT producer_result EQUAL 0)
    message(FATAL_ERROR
        "producer process failed (${producer_result})\n${producer_output}${producer_error}")
endif()
if(NOT EXISTS "${checkpoint}" OR NOT EXISTS "${future_reference}")
    message(FATAL_ERROR "producer process did not create both snapshots")
endif()

execute_process(
    COMMAND "${TEST_PROGRAM}" consume "${checkpoint}" "${future_reference}"
    RESULT_VARIABLE consumer_result
    OUTPUT_VARIABLE consumer_output
    ERROR_VARIABLE consumer_error)
if(NOT consumer_result EQUAL 0)
    message(FATAL_ERROR
        "consumer process failed (${consumer_result})\n${consumer_output}${consumer_error}")
endif()

message(STATUS "${producer_output}")
message(STATUS "${consumer_output}")
file(REMOVE "${checkpoint}" "${future_reference}")
