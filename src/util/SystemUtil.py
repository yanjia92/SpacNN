import platform


def on_windows_platform():
    return "Windows" in platform.system()


def on_mac_platform():
    return "Darwin" in platform.system()


def main():
    print platform.system()


if __name__ == "__main__":
    main()