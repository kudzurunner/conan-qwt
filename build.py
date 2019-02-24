from cpt.packager import ConanMultiPackager


if __name__ == "__main__":
    builder = ConanMultiPackager(username="kudzurunner", build_policy="missing")
    builder.add_common_builds()
    builder.run()