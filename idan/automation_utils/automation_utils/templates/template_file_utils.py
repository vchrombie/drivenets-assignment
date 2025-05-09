import shutil
import typing
import pathlib
import contextlib

import yaml

import orbital.common as common

from . import variables_extractor

logger = common.get_logger(__file__)

TEMPLATE_VARIABLES_DIRECTORY: str = "template_variables"
TEMPLATE_VARIABLES_DEFAULT_PATH: pathlib.Path = (
    pathlib.Path(__file__).parent / TEMPLATE_VARIABLES_DIRECTORY
)


@contextlib.contextmanager
def use_template_variables_default_path(
    default_path: typing.Union[str, pathlib.Path]
):
    global TEMPLATE_VARIABLES_DEFAULT_PATH
    default_path = pathlib.Path(default_path)
    if not default_path.stem == TEMPLATE_VARIABLES_DIRECTORY:
        default_path = default_path / TEMPLATE_VARIABLES_DIRECTORY

    TEMPLATE_VARIABLES_DEFAULT_PATH = root_path = default_path
    root_path.mkdir(mode=0o755, parents=True, exist_ok=True)
    yield root_path
    shutil.rmtree(root_path, ignore_errors=True)


def create_template_variables_file(
    template_name: str,
    file_path: pathlib.Path,
    variables: variables_extractor.VariableType,
):
    """Wwill create a yaml file where user can specify the values for each template variables
    Example: bundle-settings.yaml
         template: bundle-settings
         variables:
           AGG_BW: '_AGG_BW'
           INTERFACE_MODE: '_INTERFACE_MODE'
           INTERFACE_TYPE: '_INTERFACE_TYPE'
           LAG_MIN_LINKS: '_LAG_MIN_LINKS'
           LAG_NUMBER: '_LAG_NUMBER'
           REMOTE_HOST: '_REMOTE_HOST'
           REMOTE_LAG_INTERFACE: '_REMOTE_LAG_INTERFACE'
     If there are many templates to be rendered for each template name (e.g. bundle-settings)
     We'll create separate template variable files for each template
     Example: bundle-settings.yaml, bundle-settings.1.yaml, bundle-settings.2.yaml
    """

    data = {
        "template": template_name,
        "variables": variables,
    }
    if file_path.exists():
        file_data: dict[str, str] = read_template_variables_fom_file(file_path)
        logger.warning(
            f"File {file_path.name} exists. Your file data {file_data} will be overwritten!"
        )

    with open(file_path, "w") as writer:
        yaml.safe_dump(data, writer)


def read_template_variables_fom_file(
    file_path: pathlib.Path,
) -> variables_extractor.VariableType:
    with open(file_path) as reader:
        data = yaml.safe_load(reader)
    return data["variables"]


class VariablesFileNameRetriever:
    def __init__(self):
        self.file_cache: dict[str, typing.Generator[str, None, None]] = dict()

    def register_template(
        self, template_name: str, file: typing.Optional[str]
    ):
        if template_name in self.file_cache:
            return
        if not file:
            file = TEMPLATE_VARIABLES_DEFAULT_PATH / f"{template_name}.yaml"
        self.file_cache[template_name] = self._file_generator(file)

    def get_unique_file_name(self, template_name: str) -> pathlib.Path:
        cache = self.file_cache
        if template_name not in cache:
            self.register_template(template_name)
        return next(self.file_cache[template_name])

    @staticmethod
    def _file_generator(file_name: typing.Union[str, pathlib.Path]):
        file: pathlib.Path = pathlib.Path(file_name).expanduser()
        if not file.is_absolute():
            file = TEMPLATE_VARIABLES_DEFAULT_PATH / file
        stem: str = file.stem
        suffix: str = file.suffix
        root: pathlib.Path = file.parent

        yield file
        counter = 1
        while True:
            yield root / (stem + ".{}".format(counter) + suffix)
            counter += 1
