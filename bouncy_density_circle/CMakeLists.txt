cmake_minimum_required(VERSION 3.25)
project(BouncyDensityCircle LANGUAGES C CXX CUDA)

# ---- Build options ----
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CUDA_STANDARD 17)
set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type")

# Ball count / resolution defaults
set(BALL_COUNT "(1u<<24)" CACHE STRING "Number of balls (C macro)")
set(RENDER_W   "1280"     CACHE STRING "Render width")
set(RENDER_H   "720"      CACHE STRING "Render height")

# ---- Find dependencies ----
find_package(OpenGL REQUIRED)
find_package(glfw3 REQUIRED)
find_package(GLEW REQUIRED)

# ---- Source ----
set(SRC bouncy_density_circle.cu)
add_executable(bouncy_density_circle ${SRC})

# ---- CUDA compiler settings ----
target_compile_options(bouncy_density_circle PRIVATE
  $<$<COMPILE_LANGUAGE:CUDA>:
    -O3
    -use_fast_math
    --expt-relaxed-constexpr
    --extended-lambda
    -lineinfo
  >
)

# Set GPU arch — change for your GPU if needed
set_property(TARGET bouncy_density_circle PROPERTY CUDA_ARCHITECTURES 86)

# ---- Definitions ----
target_compile_definitions(bouncy_density_circle PRIVATE
  BALL_COUNT=${BALL_COUNT}
  RENDER_W=${RENDER_W}
  RENDER_H=${RENDER_H}
)

# ---- Link libraries ----
target_link_libraries(bouncy_density_circle PRIVATE
  OpenGL::GL
  GLEW::GLEW
  glfw
)

# On Windows, we need to link extra system libs
if (WIN32)
  target_link_libraries(bouncy_density_circle PRIVATE
    opengl32
    gdi32
    user32
  )
endif()

# ---- Output directory ----
set_target_properties(bouncy_density_circle PROPERTIES
  RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
)

message(STATUS "Configured with BALL_COUNT=${BALL_COUNT}, resolution=${RENDER_W}x${RENDER_H}")
