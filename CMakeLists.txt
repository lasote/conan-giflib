PROJECT(giflib)
cmake_minimum_required(VERSION 2.8)
include(../conanbuildinfo.cmake)
CONAN_BASIC_SETUP()


SET(GIFLIB_SOURCE_DIR ".")
SET(TARGET_LIB libgif)

SET(GIFLIB_PUBLIC_HEADERS
	${GIFLIB_SOURCE_DIR}/lib/gif_lib.h
)
SET(GIFLIB_PRIVATE_HEADERS
	${GIFLIB_SOURCE_DIR}/lib/gif_lib_private.h
	${GIFLIB_SOURCE_DIR}/lib/gif_hash.h
)


file(GLOB GIFLIB_SRCS lib/*.c)

IF(MSVC)
	# Create file to avoid include file name collision on other platforms
	CONFIGURE_FILE(unistd.h.in unistd.h @ONLY)	

	# Add unistd.h, getopt.h, getopt.c and stdbool.h for windows build
	# getopt from: http://gist.github.com/ashelly/7776712
	# unistd.h from: http://stackoverflow.com/questions/341817/is-there-a-replacement-for-unistd-h-for-windows-visual-c
	# stdbool.h is just a simple redefinition of bool as int
	#SET(GIFLIB_PUBLIC_HEADERS
	#	${GIFLIB_PUBLIC_HEADERS}
	#	stdbool.h
	#)

	SET(GIFLIB_PRIVATE_HEADERS
		${GIFLIB_PRIVATE_HEADERS}
		getopt.h
		unistd.h
	)

	SET(GIFLIB_SRCS
		${GIFLIB_SRCS}
		getopt.c
	)
ENDIF(MSVC)


# Dependent include files
INCLUDE_DIRECTORIES(${GIFLIB_SOURCE_DIR} ${CMAKE_CURRENT_SOURCE_DIR} ${CMAKE_CURRENT_BINARY_DIR})

IF(MSVC)
	SET(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} /wd4018 /wd4028 /wd4244 /wd4996")
	ADD_DEFINITIONS(-D_CRT_SECURE_NO_WARNINGS -D_LIB)
	SET(CMAKE_DEBUG_POSTFIX "d")
ENDIF(MSVC)

IF(MINGW)
	ADD_DEFINITIONS(-D_CRT_SECURE_NO_WARNINGS -D_LIB)
ENDIF(MINGW)
MESSAGE(ERROR ${GIFLIB_SRCS})
ADD_LIBRARY(${TARGET_LIB} STATIC ${GIFLIB_SRCS} ${GIFLIB_PRIVATE_HEADERS} ${GIFLIB_PUBLIC_HEADERS})
ADD_LIBRARY(getarg STATIC util/getarg.c)

IF(MINGW)
	SET_TARGET_PROPERTIES(${TARGET_LIB} PROPERTIES OUTPUT_NAME gif)
ENDIF()

