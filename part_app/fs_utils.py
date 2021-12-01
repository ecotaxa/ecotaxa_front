import pathlib


def CreateDirConcurrentlyIfNeeded(DirPath: pathlib.Path):
    """
    Permet de créer le répertoire passé en paramètre s'il n'existe pas et le crée si nécessaire.
    Si la création échoue, il teste s'il n'a pas été créé par un autre processus, et dans ce cas ne remonte pas d'erreur.
    :param DirPath: répertoire à créer sous forme de path
    """
    try:
        if not DirPath.exists():
            DirPath.mkdir()
    except Exception as e:
        if not DirPath.exists():
            raise e

