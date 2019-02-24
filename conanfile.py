from conans import ConanFile, tools, VisualStudioBuildEnvironment
import os

class QwtConan(ConanFile):
    name = "qwt"
    version = "6.1.4"
    license = "https://qwt.sourceforge.io/qwtlicense.html"
    author = "KudzuRunner"
    url = "https://github.com/kudzurunner/conan-qwt"
    description = "Qwt - Qt Widgets for Technical Applications"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "with_plot": [True, False],
        "with_widgets": [True, False],
        "with_svg": [True, False],
        "with_opengl": [True, False],
        "with_mathml": [True, False],
        "with_designer": [True, False],
        "with_examples": [True, False],
        "with_playground": [True, False],
    }
    default_options = {
        "shared": True,
        "with_plot": True,
        "with_widgets": False,
        "with_svg": True,
        "with_opengl": True,
        "with_mathml": False,
        "with_designer": True,
        "with_examples": False,
        "with_playground": False
    }
    generators = "qmake"
    source_name = "{}-{}".format(name, version)
    requires = (
        "qt/5.12.1@bincrafters/stable"
    )
    exports = (
        "patches/*.patch")

    def ex_dict(self, d, keys):
        return {k:v for k,v in d.items() if k not in keys}

    def disable_conf(self, name, enabled):
        prefix = "#" if enabled == 'False' else ""
        if name == "Opengl":
            name = "OpenGL"
        if name == "Mathml":
            name = "MathML"
        string = "QWT_CONFIG += Qwt" + name
        self.output.info("String: %s, value: %r, prefix: %s" % (string, enabled, prefix))
        tools.replace_in_file("{}/qwtconfig.pri".format(self.source_name), string, prefix+string)

    def build_requirements(self):
        if self.settings.os == "Windows":
            self.build_requires("jom_installer/1.1.2@bincrafters/stable")

    def configure(self):
        if self.settings.build_type == "Debug":
            self.options.with_designer = False
        if self.options.with_designer:
            self.options["qt"].qttools = True
        if self.options.with_svg:
            self.options["qt"].qtsvg = True

    def source(self):
        archive_name = "{}.tar.bz2".format(self.source_name)
        url = "https://downloads.sourceforge.net/{0}/{1}".format(self.name, archive_name)

        tools.download(url, filename=archive_name)
        tools.untargz(filename=archive_name)
        os.remove(archive_name)

        tools.patch(base_path=self.source_name, patch_file="patches/config.patch")
        self.disable_conf("Dll", self.options.shared == True)
        options = self.ex_dict(self.options, {"shared"})
        for key, value in options.items():
            self.disable_conf(str(key)[5:].title(), value)

    def build(self):
        build_type = str(self.settings.build_type).lower()
        qmake = "qmake -r qwt.pro".format(build_type)
        with tools.chdir(self.source_name):
            if self.settings.os == "Windows":
                env_build = VisualStudioBuildEnvironment(self)
                with tools.environment_append(env_build.vars):
                    vcvars = tools.vcvars_command(self.settings)
                    self.run("%s && %s" % (vcvars, qmake))
                    self.run("%s && jom -j%d" % (vcvars, tools.cpu_count()))
            else:
                self.run("%s && make -j%d" % (qmake, tools.cpu_count()))

    def package(self):
        self.copy("*.h", dst="include", src=self.source_name+"/src")
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        suffix = "d" if self.settings.build_type == "Debug" else ""
        self.cpp_info.libs = ["qwt" + suffix]
