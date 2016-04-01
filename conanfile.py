from conans import ConanFile
import os, shutil
from conans.tools import download, unzip, replace_in_file
from conans import CMake, ConfigureEnvironment


class ZlibNgConan(ConanFile):
    name = "giflib"
    version = "5.1.3"
    ZIP_FOLDER_NAME = "giflib-%s" % version 
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = "shared=False", "fPIC=True"
    url="http://github.com/lasote/conan-giflib"
    license="https://sourceforge.net/p/giflib/code/ci/master/tree/COPYING"
    exports = ["FindGIF.cmake", "CMakeLists.txt", "getopt.c", "getopt.h", "stdbool.h", "unistd.h.in", "giflib-%s-windows.zip" % version]
    # The exported files I took them from https://github.com/bjornblissing/osg-3rdparty-cmake/tree/master/giflib
    
    def config(self):
        try: # Try catch can be removed when conan 0.8 is released
            del self.settings.compiler.libcxx 
        except: 
            pass
        
        if self.settings.os == "Windows":
            try:
                self.options.remove("shared")
                self.options.remove("fPIC")
            except: 
                pass
            self.ZIP_FOLDER_NAME = "giflib-%s-windows" % self.version


    def source(self):
        if self.settings.os == "Windows":
            zip_name = "giflib-%s-windows.zip" % self.version
        else: 
            zip_name = "%s.tar.gz" % self.ZIP_FOLDER_NAME
            download("http://downloads.sourceforge.net/project/giflib/%s" % zip_name, zip_name)
        unzip(zip_name)
        self.output.info("Unzipped!")
        if self.settings.os != "Windows":
            self.run("chmod +x ./%s/autogen.sh" % self.ZIP_FOLDER_NAME)
        else:
            for filename in ["CMakeLists.txt", "getopt.c", "getopt.h", "stdbool.h", "unistd.h.in"]:
                shutil.copy(filename, os.path.join(self.ZIP_FOLDER_NAME, filename))
            

    def build(self):
        if self.settings.os == "Linux" or self.settings.os == "Macos":
            env = ConfigureEnvironment(self.deps_cpp_info, self.settings)
            if self.options.fPIC:
                env_line = env.command_line.replace('CFLAGS="', 'CFLAGS="-fPIC ')
            else:
                env_line = env.command_line
            
            self.run("cd %s && %s ./autogen.sh" % (self.ZIP_FOLDER_NAME, env_line))
            self.run("chmod +x ./%s/configure" % self.ZIP_FOLDER_NAME)
            if self.settings.os == "Macos":
                old_str = '-install_name \$rpath/\$soname'
                new_str = '-install_name \$soname'
                replace_in_file("./%s/configure" % self.ZIP_FOLDER_NAME, old_str, new_str)

            
            self.run("cd %s && %s ./configure" % (self.ZIP_FOLDER_NAME, env_line))
            self.run("cd %s && %s make" % (self.ZIP_FOLDER_NAME, env_line))
        else:
            cmake = CMake(self.settings)
            self.run("cd %s && mkdir _build" % self.ZIP_FOLDER_NAME)
            cd_build = "cd %s/_build" % self.ZIP_FOLDER_NAME
            self.output.warn('%s && cmake .. %s' % (cd_build, cmake.command_line))
            self.run('%s && cmake .. %s' % (cd_build, cmake.command_line))
            self.output.warn("%s && cmake --build . %s" % (cd_build, cmake.build_config))
            self.run("%s && cmake --build . %s" % (cd_build, cmake.build_config))
 
    def package(self):
        # Copy FindGIF.cmake to package
        self.copy("FindGIF.cmake", ".", ".")
        
        # Copying zlib.h, zutil.h, zconf.h
        self.copy("*.h", "include", "%s" % (self.ZIP_FOLDER_NAME), keep_path=False)
        self.copy("*.h", "include", "%s" % ("_build"), keep_path=False)

        if not self.settings.os == "Windows" and self.options.shared:
            if self.settings.os == "Macos":
                self.copy(pattern="*.dylib", dst="lib", keep_path=False)
                self.copy(pattern="*getarg*.a", dst="lib", src=self.ZIP_FOLDER_NAME, keep_path=False)
            else:
                self.copy(pattern="*.so*", dst="lib", src=self.ZIP_FOLDER_NAME, keep_path=False)
                self.copy(pattern="*getarg*.a*", dst="lib", src=self.ZIP_FOLDER_NAME, keep_path=False)
        else:
            self.copy(pattern="*.a", dst="lib", src="%s/_build" % self.ZIP_FOLDER_NAME, keep_path=False)
            self.copy(pattern="*.a", dst="lib", src=self.ZIP_FOLDER_NAME, keep_path=False)
            self.copy(pattern="*.lib", dst="lib", src=self.ZIP_FOLDER_NAME, keep_path=False)

    def package_info(self):
        if self.settings.os == "Windows":
            if self.settings.build_type == "Debug":
                self.cpp_info.libs = ['libgifd', 'getargd']
            else:
                self.cpp_info.libs = ['libgif', 'getarg']
        else:
            self.cpp_info.libs = ['gif', 'getarg']
