from conf.settings import FilesConf
import os


def create_dir(reference_path):
    if not os.path.exists(reference_path):
        os.mkdir(reference_path)


def create_dirs():
    create_dir(FilesConf.Paths.data)
    create_dir(FilesConf.Paths.model)
    create_dir(FilesConf.Paths.datasets)
    create_dir(FilesConf.Paths.output)
    create_dir("logs")


if __name__ == "__main__":
    create_dirs()



