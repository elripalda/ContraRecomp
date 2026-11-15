# Contra (USA) on the NESRecomp cycle backend.
#
#   cmake -S . -B build-play -G Ninja -DCMAKE_BUILD_TYPE=Release
#   cmake --build build-play --parallel
#   ./build-play/contrarecomp contra.nes
#
# Your own ROM: contra.nes beside this file, or -DCONTRA_ROM=/path/to/rom.nes.
# Headless (logs, harvesting): add -DNESRECOMP_HEADLESS=ON, separate build dir.
cmake_minimum_required(VERSION 3.20)
project(ContraRecomp C)

# The engine: a nesrecomp submodule here, else the shared fixed fork.
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/nesrecomp/runner/cyc/project.cmake")
    set(_contra_engine "${CMAKE_CURRENT_SOURCE_DIR}/nesrecomp")
else()
    set(_contra_engine "$ENV{HOME}/Projects/nesrecomp")
endif()
set(NESRECOMP_ROOT "${_contra_engine}" CACHE PATH "nesrecomp engine checkout")
if(NOT EXISTS "${NESRECOMP_ROOT}/runner/cyc/project.cmake")
    message(FATAL_ERROR "NESRECOMP_ROOT=${NESRECOMP_ROOT} is not a nesrecomp checkout")
endif()

# The launcher and in-game menu (recomp-ui): a submodule here, else the copy
# in DD2Recomp (pinned at the tested commit there).
if(NOT DEFINED CACHE{NESRECOMP_RECOMP_UI}
   AND NOT EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/recomp-ui/recomp_ui.cmake"
   AND EXISTS "$ENV{HOME}/Projects/DD2Recomp/recomp-ui/recomp_ui.cmake")
    set(NESRECOMP_RECOMP_UI "$ENV{HOME}/Projects/DD2Recomp/recomp-ui" CACHE STRING
        "recomp-ui checkout for the cycle host's launcher and menu")
endif()

set(CONTRA_ROM "${CMAKE_CURRENT_SOURCE_DIR}/contra.nes" CACHE FILEPATH "Contra (USA) ROM")
if(NOT EXISTS "${CONTRA_ROM}")
    message(FATAL_ERROR "No ROM at ${CONTRA_ROM}: put your Contra (USA) dump there as contra.nes, "
                        "or pass -DCONTRA_ROM=/path/to/rom.nes")
endif()
option(NESRECOMP_HEADLESS "Build without SDL window/audio support" OFF)

# Rewind starts off: its snapshot every few frames slows the frame after it,
# which breaks the even 120/180/240 pictures a second (players can turn it
# on in config.ini [Rewind] Enabled = 1).
add_compile_definitions(NESRECOMP_REWIND_DEFAULT=0)

include("${NESRECOMP_ROOT}/runner/cyc/project.cmake")

set(contra_options "")
if(NESRECOMP_HEADLESS)
    list(APPEND contra_options HEADLESS)
endif()

# seeds.txt: ROM code addresses to compile (no game data, safe to commit).
# capture.txt: code the game copies into RAM (holds game bytes, local only).
set(contra_capture "")
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/capture.txt")
    set(contra_capture CAPTURE_FILE "capture.txt")
endif()
nesrecomp_add_cycle_game(contrarecomp
    ROM          "${CONTRA_ROM}"
    GAME_CONFIG  "game.toml"
    SEED_FILE    "seeds.txt"
    ${contra_capture}
    PLAYERS 2
    REGION NTSC
    HOST_EXTRAS  "src/contra_extras.c"
    ${contra_options})

if(UNIX)
    target_link_libraries(contrarecomp PRIVATE m)
endif()
