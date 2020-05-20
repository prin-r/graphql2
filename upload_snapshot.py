import time
import os
import subprocess
import zipfile


def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(
                os.path.join(root, file),
                os.path.relpath(
                    os.path.join(root, file), os.path.join(path, "..")
                ),
            )


def main():
    uuid = int(time.time())
    filename = "{}.zip".format(uuid)
    with zipfile.ZipFile(filename, "w", zipfile.ZIP_DEFLATED) as fzip:
        fzip.write("__main__.py")
        zipdir("app", fzip)
        zipdir("abis", fzip)
        zipdir("config", fzip)
    print("Uploading {}".format(filename))
    subprocess.check_call(
        ["scp", filename, "ubuntu@54.146.96.106:/home/ubuntu/subs"]
    )
    os.unlink(filename)


if __name__ == "__main__":
    main()

