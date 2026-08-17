cmake_minimum_required(VERSION 3.20)
project(DisaggSIMDProcessor LANGUAGES CXX)


# Set Standard
set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED On)
set(warnings "-Wall -Wextra -pedantic -Wcast-align -Wcast-qual -Wctor-dtor-privacy -Wdisabled-optimization -Wformat=2 -Winit-self -Wlogical-op -Wmissing-include-dirs -Wnoexcept -Wold-style-cast -Woverloaded-virtual -Wredundant-decls -Wshadow -Wsign-promo -Wstrict-null-sentinel -Wstrict-overflow=5 -Wundef -Wno-unused -Wno-variadic-macros -Wno-parentheses -fdiagnostics-show-option")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${warnings}")
set(OPTIMIZE_OPTIONS -O3 -g)
set(CMAKE_VERBOSE_MAKEFILE On)

add_compile_options("${OPTIMIZE_OPTIONS}")

find_library(PTHREAD_LIB pthread REQUIRED)
find_library(NUMA_LIB numa REQUIRED)

# Optimizer Append
include(FetchContent)
include(CTest)

set(OPTIMIZER_DIR "${CMAKE_CURRENT_SOURCE_DIR}/ws25-optimizer-cpp/cpp")

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
option(BUILD_SHARED_LIBS "Build shared libraries" ON)

FetchContent_Declare(hyrise_sqlparser GIT_REPOSITORY https://github.com/hyrise/sql-parser.git GIT_TAG main)
FetchContent_Populate(hyrise_sqlparser)
set(SQLPARSER_INCLUDE_DIR "${hyrise_sqlparser_SOURCE_DIR}/src")
file(GLOB_RECURSE SQLPARSER_SRC "${SQLPARSER_INCLUDE_DIR}/*.cpp")

add_library(sql-parser STATIC
    ${SQLPARSER_SRC}
)

target_include_directories(sql-parser PUBLIC
    "${SQLPARSER_INCLUDE_DIR}"
)

# old
# add_library(sql-parser STATIC ${SQLPARSER_SRC} code/include/optimizer/Logger.hpp)

find_program(GRAPHVIZ_DOT NAMES dot)
if(NOT GRAPHVIZ_DOT)
  message(WARNING "Graphviz (dot) not found. Please install it.")
endif()

FetchContent_Declare(abseil GIT_REPOSITORY https://github.com/abseil/abseil-cpp.git GIT_TAG 20240722.0)
set(ABSL_PROPAGATE_CXX_STD ON)
FetchContent_MakeAvailable(abseil)

file(GLOB_RECURSE OPTIMIZER_SRC
    CONFIGURE_DEPENDS
    "${OPTIMIZER_DIR}/code/src/*.[cC][cC]*"
    "${OPTIMIZER_DIR}/code/src/*.[cC][pP][pP]"
)

file(GLOB_RECURSE OPTIMIZER_HEADERS
    CONFIGURE_DEPENDS
    "${OPTIMIZER_DIR}/code/include/*.[hH]*"
)


# add_executable(optimizer-server "${CMAKE_CURRENT_SOURCE_DIR}/code/examples/tcp_server_example.cpp" ${PROJECT_SRC} ${PROJECT_HEADERS} code/include/optimizer/Logger.hpp)
# add_executable(optimizer-unit "${OPTIMIZER_DIR}/code/examples/OptimizerUnit.cpp" ${PROJECT_SRC} ${PROJECT_HEADERS} code/include/optimizer/QueryManager.hpp code/src/optimizer/QueryManager.cpp code/include/optimizer/Logger.hpp)

FetchContent_Declare(
    nlohmann_json
    GIT_REPOSITORY https://github.com/nlohmann/json.git
    GIT_TAG v3.11.3
)

FetchContent_MakeAvailable(nlohmann_json)

# ── Protobuf ────────────────────────────────────────────────
find_package(Protobuf 3.0 REQUIRED)

# Where your .proto files live
set(PROTO_SRC_DIR ${CMAKE_CURRENT_SOURCE_DIR}/proto)

# Where generated .pb.h / .pb.cc will be placed
set(PROTO_GEN_DIR ${CMAKE_BINARY_DIR}/proto)

file(MAKE_DIRECTORY ${PROTO_GEN_DIR})

# Collect all .proto files
file(GLOB PROTO_FILES "${PROTO_SRC_DIR}/*.proto")

# Generate C++ sources from each .proto
set(PROTO_GENERATED_SRCS "")
set(PROTO_GENERATED_HDRS "")

foreach(PROTO_FILE ${PROTO_FILES})
    get_filename_component(PROTO_NAME ${PROTO_FILE} NAME_WE)

    list(APPEND PROTO_GENERATED_SRCS
        "${PROTO_GEN_DIR}/${PROTO_NAME}.pb.cc"
    )

    list(APPEND PROTO_GENERATED_HDRS
        "${PROTO_GEN_DIR}/${PROTO_NAME}.pb.h"
    )
endforeach()

add_custom_command(
    OUTPUT ${PROTO_GENERATED_SRCS} ${PROTO_GENERATED_HDRS}
    COMMAND ${Protobuf_PROTOC_EXECUTABLE}
        --cpp_out=${PROTO_GEN_DIR}
        -I${PROTO_SRC_DIR}
        ${PROTO_FILES}
    DEPENDS ${PROTO_FILES}
    COMMENT "Generating protobuf C++ sources"
)

# Library target so the generated code is compiled once and linkable
add_library(proto_lib STATIC
    ${PROTO_GENERATED_SRCS}
    ${PROTO_GENERATED_HDRS}
)

target_include_directories(proto_lib PUBLIC
    ${PROTO_GEN_DIR}
)

target_link_libraries(proto_lib PUBLIC
    protobuf::libprotobuf
)
# ────────────────────────────────────────────────────────────

add_executable(optimizer-unit
    "${OPTIMIZER_DIR}/code/examples/OptimizerUnit.cpp"
    ${OPTIMIZER_SRC}
    "${OPTIMIZER_DIR}/code/src/optimizer/QueryManager.cpp"
    ${OPTIMIZER_HEADERS}
)


# add_executable(optimizer-compute-unit "${CMAKE_CURRENT_SOURCE_DIR}/code/examples/ComputeUnit.cpp" ${PROJECT_SRC} ${PROJECT_HEADERS} code/include/optimizer/Logger.hpp)

# find_package(Protobuf 3.0 REQUIRED)

# if(TARGET protobuf::libprotobuf)
#     set(PROTOBUF_LIB protobuf::libprotobuf)
# elseif(TARGET protobuf::libprotobuf-lite)
#     set(PROTOBUF_LIB protobuf::libprotobuf-lite)
# elseif(Protobuf_LIBRARIES)
#     set(PROTOBUF_LIB ${Protobuf_LIBRARIES})
# else()
#     message(FATAL_ERROR "Could not find Protobuf library.")
# endif()

# set(ALL_TARGETS optimizer-server optimizer-unit optimizer-compute-unit)
target_include_directories(optimizer-unit PUBLIC
    ${OPTIMIZER_DIR}/code/include
    ${PROTO_GEN_DIR}
)

target_link_libraries(optimizer-unit PRIVATE
    proto_lib
    ${PROTOBUF_LIB}
    absl::log
    absl::log_internal_check_op
    sql-parser
    nlohmann_json::nlohmann_json
)



if(MSVC)
    target_compile_options(optimizer-unit PRIVATE /W4 /permissive-)
else()
    target_compile_options(optimizer-unit PRIVATE -Wall -Wextra -Wpedantic)
endif()


target_include_directories(sql-parser PUBLIC ${SQLPARSER_INCLUDE_DIR})

if (BUILD_TESTING)
  FetchContent_Declare(googletest GIT_REPOSITORY https://github.com/google/googletest.git GIT_TAG v1.17.0)
  FetchContent_MakeAvailable(googletest)
  enable_testing()

#   add_executable(optimizer-tests
#           ${OPTIMIZER_DIR}/code/tests/test_sql_parser.cpp
#           ${OPTIMIZER_DIR}/code/tests/test_sql_to_logical_plan_translator.cpp
#           ${OPTIMIZER_DIR}/code/tests/test_json_to_logical_plan_translator.cpp
#           ${OPTIMIZER_DIR}/code/tests/test_physical_optimizer.cpp
#           ${PROJECT_SRC}
#           ${PROJECT_HEADERS}
#           code/include/optimizer/Logger.hpp
#   )

add_executable(optimizer-tests
    "${OPTIMIZER_DIR}/code/tests/test_sql_parser.cpp"
    "${OPTIMIZER_DIR}/code/tests/test_sql_to_logical_plan_translator.cpp"
    "${OPTIMIZER_DIR}/code/tests/test_json_to_logical_plan_translator.cpp"
    "${OPTIMIZER_DIR}/code/tests/test_physical_optimizer.cpp"
    ${OPTIMIZER_SRC}
    ${OPTIMIZER_HEADERS}
)

target_include_directories(optimizer-tests PUBLIC
          ${OPTIMIZER_DIR}/code/include
          ${PROTO_GEN_DIR}
)

target_compile_definitions(optimizer-tests PRIVATE
          OPTIMIZER_REPO_ROOT="${OPTIMIZER_DIR}/.."
  )

target_link_libraries(optimizer-tests PRIVATE
          proto_lib
          ${PROTOBUF_LIB}
          absl::log
          absl::log_internal_check_op
          sql-parser
          GTest::gtest_main
          nlohmann_json::nlohmann_json
)

include(GoogleTest)
  gtest_discover_tests(optimizer-tests)
endif()



set(EXT_DIR ${CMAKE_CURRENT_SOURCE_DIR}/ext)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

add_subdirectory("ext/SIMDOperators")

# Default log level, overridable via -DLOG_LEVEL=LOG_DEBUG1
set(LOG_LEVEL "LOG_INFO" CACHE STRING "Default log level")

# ── computeUnit ─────────────────────────────────────────────
set(CU_SRC_DIR ${CMAKE_CURRENT_SOURCE_DIR}/computeUnit/src)
set(CU_INC_DIR ${CMAKE_CURRENT_SOURCE_DIR}/computeUnit/include)

file(GLOB_RECURSE CU_SOURCES ${CU_SRC_DIR}/*.cpp)
file(GLOB_RECURSE CU_HEADERS ${CU_INC_DIR}/*.hpp)

add_executable(computeUnit computeUnit/ComputeUnit.cpp ${CU_SOURCES} ${CU_HEADERS})
target_include_directories(computeUnit PRIVATE ${CU_INC_DIR} ${EXT_DIR} ${SIMDOPS_TSL_ROOT} ${SIMDOPS_INCLUDE})
target_link_libraries(computeUnit ${PTHREAD_LIB} ${NUMA_LIB} "tsl" proto_lib)
target_compile_definitions(computeUnit PRIVATE DEFAULT_LOG_LEVEL="${LOG_LEVEL}")

# ── grouper ─────────────────────────────────────────────────
set(GR_SRC_DIR ${CMAKE_CURRENT_SOURCE_DIR}/grouper/src)
set(GR_INC_DIR ${CMAKE_CURRENT_SOURCE_DIR}/grouper/include)

file(GLOB_RECURSE GR_SOURCES ${GR_SRC_DIR}/*.cpp)
file(GLOB_RECURSE GR_HEADERS ${GR_INC_DIR}/*.hpp)

add_executable(grouper grouper/Grouper.cpp ${GR_SOURCES} ${GR_HEADERS})
target_include_directories(grouper PRIVATE ${GR_INC_DIR} ${EXT_DIR})
target_link_libraries(grouper ${PTHREAD_LIB} ${NUMA_LIB} proto_lib)
option(GROUPER_VERBOSE "Enable verbose output for grouper" OFF)
if(GROUPER_VERBOSE)
    target_compile_definitions(grouper PRIVATE VERBOSE_OUTPUT)
endif()
option(GROUPER_PROFILING "Enable CSV timing for DagCollection::analyze" OFF)
if(GROUPER_PROFILING)
    target_compile_definitions(grouper PRIVATE PROFILING_ENABLED)
endif()

# ── pg potential bench ────────────────────────────────────────
add_executable(pg_potential_bench "pg_potential_experiment/pg_potential_bench.cpp")

target_compile_options(pg_potential_bench PRIVATE -O3 -march=native -mavx512f)
target_link_libraries(pg_potential_bench ${PTHREAD_LIB} ${NUMA_LIB})
