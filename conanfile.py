from conans import ConanFile
import os, shutil
from conans.tools import download, unzip, replace_in_file, environment_append, chdir
from conans import CMake, AutoToolsBuildEnvironment


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
    exports = ["FindGIF.cmake", "CMakeLists.txt", "getopt.c", "getopt.h", "unistd.h.in"]
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
            # self.ZIP_FOLDER_NAME = "giflib-%s-windows" % self.version

    def source(self):
        zip_name = "%s.tar.gz" % self.ZIP_FOLDER_NAME
        download("http://downloads.sourceforge.net/project/giflib/%s" % zip_name, zip_name)
        unzip(zip_name)
        self.output.info("Unzipped!")
        if self.settings.os != "Windows":
            self.run("chmod +x ./%s/autogen.sh" % self.ZIP_FOLDER_NAME)
        else:
            for filename in ["CMakeLists.txt", "getopt.c", "getopt.h", "unistd.h.in"]:
                shutil.copy(filename, os.path.join(self.ZIP_FOLDER_NAME, filename))

    def build(self):
        if self.settings.os == "Linux" or self.settings.os == "Macos":
            env = AutoToolsBuildEnvironment(self)
            env.fpic = self.options.fPIC
            with environment_append(env.vars):
                with chdir(self.ZIP_FOLDER_NAME):
                    self.run("./autogen.sh")
                    self.run("chmod +x configure")
                    if self.settings.os == "Macos":
                        old_str = '-install_name \$rpath/\$soname'
                        new_str = '-install_name \$soname'
                        replace_in_file("./configure", old_str, new_str)

                    self.run("./configure")
                    self.run("make")
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

        # Copy pc file
        self.copy("*.pc", dst="", keep_path=False)
        
        # Copying zlib.h, zutil.h, zconf.h
        self.copy("*.h", "include", "%s" % self.ZIP_FOLDER_NAME, keep_path=False)
        self.copy("*.h", "include", "%s" % "_build", keep_path=False)

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
