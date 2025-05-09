import os
import enum
import json
import types
import typing
import pathlib
import collections

import jinja2
import configargparse
from automation_utils.common import exceptions as aut_util_exc

import orbital.common as common
from orbital.mechanics import composer
from orbital.mechanics import template as orbital_template
from orbital.mechanics.exceptions import OrbitalError

from . import type_helper, template_file_utils, variables_extractor

logger = common.get_logger(__file__)

ERROR_NEED_ROOT = "Need a --root directory to lookup templates."
DEFAULT_CONFIG_FILES = ["/etc/orbital/cli.conf", "~/.config/orbital/cli.conf"]

configargparser = configargparse.ArgParser(
    default_config_files=DEFAULT_CONFIG_FILES
)

# only options starting with '--' can be set in a config file [ConfigArgParse docs]
configargparser.add(
    "--root",
    is_config_file=True,
    required=True,
    help="Root directory for Orbital Templates",
    type=str,
)
parsed_args, _ = configargparser.parse_known_args()


def set_root_dir_for_templates_lookup(
    parsed_args: configargparse.Namespace,
) -> str:
    root = os.path.expanduser(parsed_args.root) if parsed_args.root else None
    if not root or not os.path.isdir(root):
        logger.warn(ERROR_NEED_ROOT)
        raise aut_util_exc.OrbitalTemplateException(ERROR_NEED_ROOT)
    return root


data_dir: str = set_root_dir_for_templates_lookup(parsed_args)

logger.info(f"Using root template lookup directory {data_dir}")

composer_obj: composer.Composer = composer.Composer(data_dir)

FileExceptions = aut_util_exc.FileExceptions


class FetchStatus(enum.Enum):
    COMPLETED = enum.auto()
    FAILED = enum.auto()
    PARTIALLY_COMPLETED = enum.auto()


class TemplateParser:
    """
    TemplateParser identifies orbital templates by relying on orbital.mechanics composition Python code
    Identified templates are rendered (i.e. S2 substitution) and the resulted output is sent to router as a cli command
    """

    TPL_METADATA_NETWORKS: str = "networks"
    TPL_METADATA_PLATFORMS: str = "platforms"
    TPL_METADATA_ROLES: str = "roles"
    TPL_METADATA_STATUS: str = "status"
    TPL_METADATA_VENDOR: str = "vendor"
    ALL_TPL_METADATA_FILTERS: dict[str, typing.Type] = {
        TPL_METADATA_NETWORKS: list[str],
        TPL_METADATA_PLATFORMS: list[str],
        TPL_METADATA_ROLES: list[str],
        TPL_METADATA_STATUS: str,
        TPL_METADATA_VENDOR: str,
    }

    def __init__(self, **kwargs):
        """create a template parser according to specified filters dictionary
        The following filter keys arre supported
        {
            "networks": list[str],
            "platforms": list[str],
            "roles": list[str],
            "status": str,
            "vendor": str,
        }
        """
        templates_metadata: dict[str, typing.Any] = dict()

        for filter_key, filter_value in kwargs.items():
            if filter_key not in self.ALL_TPL_METADATA_FILTERS:
                logger.warning(
                    f"Unknown filter {{{filter_key}: {filter_value}}} detected. Ignoring.."
                )
                continue
            expected_filter_type: types.GenericAlias = (
                self.ALL_TPL_METADATA_FILTERS[filter_key]
            )
            if not type_helper.check_type_equality(
                filter_value, expected_filter_type
            ):
                logger.warning(
                    f"Expected filter {{{filter_key}: {filter_value}}} to have "
                    + f"type {expected_filter_type} but actual type is {type(filter_value)}. Ignoring.."
                )
                continue

            templates_metadata[filter_key] = filter_value
        self.templates_metadata = templates_metadata

        self.templates: list[orbital_template.Template] = list()

        self.variables_file_name_retriever = (
            template_file_utils.VariablesFileNameRetriever()
        )

    def filter_by_network(self, network: str):
        """
        Add a filter by network type in :py:data: `composer.ComposerParameters` metaparams
        """
        self._add_filter(self.TPL_METADATA_NETWORKS, network)

    def filter_by_platform(self, platform: str):
        """
        Add a filter by platform type in :py:data: `composer.ComposerParameters` metaparams
        """
        self._add_filter(self.TPL_METADATA_PLATFORMS, platform)

    def filter_by_role(self, role: str):
        """
        Add a filter by role type in :py:data: `composer.ComposerParameters` metaparams
        """
        self._add_filter(self.TPL_METADATA_ROLES, role)

    def _add_filter(self, key, value):
        values = self.templates_metadata.get(key)
        if not values:
            self.templates_metadata[key] = [value]
        elif value not in values:
            values.append(value)

    def filter_by_vendor(self, vendor: str):
        """
        Add a filter by vendor type in :py:data: `composer.ComposerParameters` metaparams
        """
        self.templates_metadata[self.TPL_METADATA_VENDOR] = vendor

    @property
    def filters(self) -> dict[str, typing.Union[str, list[str]]]:
        """retrieve the filters dictionary used to fetch Orbital Templates"""
        return self.templates_metadata

    def matched_templates(
        self, template_name: typing.Optional[str] = None
    ) -> list[orbital_template.Template]:
        """
        Get the list of fetched templates as list of :py:data: `Template`
        :param template_name: optional string value. If specified will return the list of matched templates filtered by template_name
        Otherwise will return the entire list of matched templates
        """
        if template_name is None:
            return self.templates
        return [
            template
            for template in self.templates
            if template_name == self._get_template_name(template)
        ]

    def match_orbital_templates(
        self, *template_names: typing.Iterable[str]
    ) -> FetchStatus:
        """
        Invokes :py:data: `composer.Composer` compose method to obtain the list of templates according to given template names
        :param template_names: sequence of strings representing template names to be composed

        Raises OrbitalTemplateException

        returns :py:data: FetchStatus
         - COMPLETED: there is exactly one template match for each template name given by the user
         - PARTIALLY_COMPLETED: some template names did not match any porbital temnplate due to filtering criteria
        """

        def unique_items(items):
            return list(set(items))

        templates_metadata = {
            k: v for k, v in self.templates_metadata.items() if bool(v)
        }
        params: composer.ComposerParameters = composer.ComposerParameters(
            all_template_variants=True, metaparams=templates_metadata
        )

        template_names = unique_items(template_names)
        try:
            composition_list: list[orbital_template.Template] = (
                composer_obj.compose(template_names, params, flatten=True)
            )
            # all types for composition_list: t.Union[None, t.List[Template], "TemplateList"]
        except OrbitalError as orbital_error:
            logger.error(
                f"Failed to compose templates {template_names}. Error {orbital_error}"
            )
            raise aut_util_exc.OrbitalTemplateException(
                f"Failed to compose templates {template_names}"
            ) from orbital_error

        self.templates = composition_list

        if len(template_names) == len(
            unique_items(
                [
                    self._get_template_name(template)
                    for template in composition_list
                ]
            )
        ):
            return FetchStatus.COMPLETED

        return FetchStatus.PARTIALLY_COMPLETED

    @staticmethod
    def _get_template_name(template: orbital_template.Template) -> str:
        return template.name

    def create_template_variables_file(
        self,
        template: orbital_template.Template,
        file: typing.Optional[str] = None,
    ) -> pathlib.Path:
        """
        writes the required template variables to file having the following format
         template: bundle-settings
         variables:
           AGG_BW: ' '
           INTERFACE_MODE: ''
           INTERFACE_TYPE: ''
        This means that for some template variant from bundle-settings template,
        these 3 variables are mandatory: AGG_BW, INTERFACE_MODE, INTERFACE_TYPE

        :param template: the orbital template instance
        :param file: optional parameter indicating the file path where the meplate variable file is written
                      If optional the possible files look like <template_name>.yaml, <template_name>.1.yaml, <template_name>.2.yaml
                      (one file is create for each tenplate variant)
        """

        template_name: str = self._get_template_name(template)
        try:
            self.variables_file_name_retriever.register_template(
                template_name, file
            )
            file_path: pathlib.Path = (
                self.variables_file_name_retriever.get_unique_file_name(
                    template_name
                )
            )
            template_variables: variables_extractor.VariableType = (
                self.get_template_variables(template)
            )
            template_file_utils.create_template_variables_file(
                template_name, file_path, template_variables
            )
            return file_path
        except FileExceptions as e:
            raise aut_util_exc.OrbitalTemplateException(
                f"Failed to create template variables file for template {template_name}"
            ) from e

    def render_template_from_file(
        self,
        template: orbital_template.Template,
        render_args_file: typing.Union[pathlib.Path, str],
    ) -> str:
        render_args_file_str: str = (
            render_args_file
            if isinstance(render_args_file, str)
            else render_args_file.as_posix()
        )
        template_name: str = self._get_template_name(template)
        try:
            render_args: dict[str, typing.Any] = (
                template_file_utils.read_template_variables_fom_file(
                    render_args_file
                )
            )
            return self.render_template_from_dict(template, render_args)
        except FileExceptions as e:
            raise aut_util_exc.OrbitalTemplateException(
                f"Failed to render template {template_name} from file {render_args_file_str}"
            ) from e

    def render_template_from_dict(
        self,
        template: orbital_template.Template,
        render_args: dict[str, typing.Any],
    ) -> str:
        """
        Produces a cli command as a string
        Each command represent an S2 rendering of the template
        :param template: tenmplate as an instance of :py:data: `Template`
        :param render_args: dictionary where the kayes are variable names (as they appear in the template yaml file)
                            and values are the values of those variables
        """
        jinja2_config = {
            "autoescape": False,
            "trim_blocks": True,
            "lstrip_blocks": True,
            "undefined": jinja2.StrictUndefined,
        }

        template_name: str = self._get_template_name(template)
        required_variables: variables_extractor.VariableType = (
            self.get_template_variables(template)
        )

        error_message: typing.Optional[str] = (
            variables_extractor.VariablesExtractor.compare_variables(
                required_variables=required_variables,
                received_variables=render_args,
            )
        )
        if error_message:
            raise aut_util_exc.OrbitalTemplateException(
                f"Template {self._get_template_name(template)}: rendering failed; error_message={error_message}"
            )

        try:
            # this stage corresponds to S2 rendering (variables denoted by {{  }})
            j2 = jinja2.Template(template.template_out, **jinja2_config)
            return j2.render(**render_args)
        except Exception as exc:
            logger.error(
                f"Failed to render template {template_name}"
                + f"\ntemplate variant:\n{template.template_out}\n>>> end of template variant"
                + f"\nrender args: {render_args}\n"
            )
            raise aut_util_exc.OrbitalTemplateException(
                f"Failed to render template {template_name}"
            ) from exc

    def get_template_variables(
        self,
        template: orbital_template.Template,
    ) -> variables_extractor.VariableType:
        """
        Identifies the required variables from an orbital template
        after any s1 rendering is completed but before s2
        """
        try:
            # invoke template introspection to render the the template in S1 stage (variables denoted by [[  ]])
            s2_introspection: orbital_template.Introspection = (
                template.s2_introspection
            )
            return variables_extractor.VariablesExtractor.extract_variables(
                template_in=template.template_out
            )
        except aut_util_exc.OrbitalTemplateException as e:
            template_name: str = self._get_template_name(template)
            raise aut_util_exc.OrbitalTemplateException(
                f"Template {template_name}: get_template_variables failed. Failed variant"
                + f"\n{template.template_out}"
                + f"\n>>>end of failed variant"
            ) from e

    @staticmethod
    def _validate_templates(composition_list: list[orbital_template.Template]):
        """
        performs a template validation in the sense that
        there is only 1 variant per template (single item from variants: key in template yaml file is read)
        Raises OrbitalTemplateException
        """

        def _construct_error_message(variants: list[typing.Dict[str, str]]):
            messages: list[str] = list()
            for index, variant in enumerate(variants, start=1):
                messages.append(
                    f"Template variant {index}\n"
                    + json.dumps(variant, indent=True)
                )
            return "\n".join(messages)

        template_variants: dict[str, list[typing.Dict[str, str]]] = (
            collections.defaultdict(list)
        )
        for template in composition_list:
            template_name = TemplateParser._get_template_name(template)
            template_informaion = collections.OrderedDict()
            template_informaion["template_name"] = template_name
            for key in template.metadata.metadata_keymap.keys():
                template_informaion[key] = template.metadata.__getattribute__(
                    key
                )
            template_informaion["template"] = template.template_in
            template_variants[template_name].append(template_informaion)

        for template_name in template_variants:
            variants: list[typing.Dict[str, str]] = template_variants[
                template_name
            ]
            if len(variants) > 1:
                logger.error(
                    f"More than a single variant was fetched for template name {template_name}\n"
                    + _construct_error_message(variants)
                )
                raise aut_util_exc.OrbitalTemplateException(
                    f"Template variants validation exception for template name {template_name}"
                )

    def render_template_by_name(
        self, template_name: str, template_vars: dict
    ) -> str:
        """
        Render template by template name.
        If more than 1 template found according to provided filter, OrbitalTemplateException exception will be raised
        Args:
            template_name: template name
            template_vars: dict of the template parameters
        Returns:
            A string with a rendered template

        Raises:
            OrbitalTemplateException
        """
        template_names: list[str] = [template_name]
        status = self.match_orbital_templates(*template_names)
        if FetchStatus.COMPLETED != status:
            raise aut_util_exc.OrbitalTemplateException(
                f"Failed to render template {template_name}"
            )
        templates = self.matched_templates()
        if len(templates) != 1:
            message = (
                f"No templates found for '{template_name}'"
                if not templates
                else f"More than one template found for '{template_name}'"
            )
            raise aut_util_exc.OrbitalTemplateException(message)

        return self.render_template_from_dict(templates[0], template_vars)

    @staticmethod
    def render_template(
        template_name: str, platforms: list, roles: list, template_vars: dict
    ) -> str:
        """
        Render template by template name.
        If more than 1 template found according to provided filter, OrbitalTemplateException exception will be raised

        Args:
            template_name: template name
            template_vars: dict of the template parameters
            platform: list of the related platforms
            roles: list of the related roles
        Returns:
            A string with a rendered template

        Raises:
            OrbitalTemplateException
        """
        parser = TemplateParser(platforms=platforms, roles=roles)
        return parser.render_template_by_name(template_name, template_vars)
