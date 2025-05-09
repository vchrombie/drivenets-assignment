import typing

import jinja2.nodes
import jinja2schema
import jinja2.environment
import jinja2schema.model
from automation_utils.common import exceptions as aut_util_exc

__all__ = ["VariablesExtractor", "VariableType"]

jinja_env: jinja2.environment.Environment = jinja2.Environment(
    undefined=jinja2.StrictUndefined
)
jinja_schema_config: jinja2schema.Config = jinja2schema.Config()
DEFAULT_VARIABLE_VALUE: str = str()

VariableType = typing.Union[
    str, list["VariableType"], dict[str, "VariableType"]
]


class VariablesExtractor:
    @staticmethod
    def extract_variables(template_in: str) -> dict[str, VariableType]:
        """
        :param: template_in: a string representing an unrendered template
        """
        try:
            template_ast: jinja2.nodes.Template = jinja_env.parse(template_in)
            schema: jinja2schema.model.Dictionary = (
                jinja2schema.infer_from_ast(
                    template_ast, config=jinja_schema_config
                )
            )

            return VariablesExtractor.recurse_schema_dictionary(schema)
        except (
            jinja2.TemplateSyntaxError,
            jinja2schema.InferException,
            jinja2schema.MergeException,
            jinja2schema.UnexpectedExpression,
            jinja2schema.InvalidExpression,
            # sometimes Exception is raised, as in
            #     raise Exception('expression visitor for {0} is not found'.format(type(ast)))
            Exception,
        ) as e:
            raise aut_util_exc.OrbitalTemplateException(
                f"Failed to extract variables from template"
            ) from e

    @staticmethod
    def recurse_schema_dictionary(schema: jinja2schema.model.Dictionary):
        variables = dict()
        for key, value in schema.items():
            if VariablesExtractor.is_list(value):
                variables[key] = [
                    VariablesExtractor.recurse_schema_dictionary(value.item)
                ]
            elif VariablesExtractor.is_dict(value):
                variables[key] = VariablesExtractor.recurse_schema_dictionary(
                    value
                )
            else:
                assert VariablesExtractor.is_primitive_type(value)
                variables[key] = DEFAULT_VARIABLE_VALUE
        return variables

    @staticmethod
    def is_list(data: jinja2schema.model.Variable):
        return isinstance(data, jinja2schema.model.List) or isinstance(
            data, jinja2schema.model.Tuple
        )

    @staticmethod
    def is_dict(data: jinja2schema.model.Variable):
        return isinstance(data, jinja2schema.model.Dictionary)

    @staticmethod
    def is_primitive_type(data: jinja2schema.model.Variable):
        """Primitive types are Scaler (string, number, boolean or None)"""
        return isinstance(data, jinja2schema.model.Scalar) or isinstance(
            data, jinja2schema.model.Unknown
        )

    @staticmethod
    def compare_variables(
        required_variables: dict[str, VariableType],
        received_variables: dict[str, VariableType],
    ) -> typing.Optional[str]:
        """
        validates if received_variables matches required_variables
        :param: required_variables: dictionary of required template variables, usually retrioeved via extract_variables
        :param: received_variables: user data that is used to render the jinja template
        Returns None if the validation is successful; otherwise a string denoting the error message
        """

        def _inner(
            required_variables_prefix, required_variables, received_variables
        ):
            if VariablesExtractor._is_primitive_type(required_variables):
                return required_variables_prefix, None
            required_variables_type = type(required_variables)
            received_variables_type = type(received_variables)

            if required_variables_type != received_variables_type:
                return (
                    required_variables_prefix,
                    f"required type {required_variables_type}. Actual type {received_variables_type}",
                )

            if required_variables_type == type(list()):
                required_elem = required_variables[0]
                for pos, received_elem in enumerate(received_variables):
                    prefix = required_variables_prefix + f".[{pos}]"
                    prefix, res = _inner(prefix, required_elem, received_elem)
                    if res:
                        return prefix, res
            else:
                unmatched_keys = VariablesExtractor._compare_dict_keys(
                    required_variables, received_variables
                )
                if unmatched_keys:
                    return (
                        required_variables_prefix,
                        f"Dictionary keys {sorted(unmatched_keys)} are missing!",
                    )
                for key, value in required_variables.items():
                    if VariablesExtractor._is_primitive_type(value):
                        continue
                    prefix = required_variables_prefix + f".{key}"
                    prefix, res = _inner(
                        prefix, value, received_variables[key]
                    )
                    if res:
                        return prefix, res
            return required_variables_prefix, None

        prefix, error = _inner(str(), required_variables, received_variables)
        if error:
            return f"prefix: {prefix.strip('.')}: error: {error}"

    @staticmethod
    def _compare_dict_keys(dict1, dict2) -> list[str]:
        """If some dict1 keys are not found in dict2, they will be returned"""
        unmatched_keys = list()
        for key in dict1:
            if key not in dict2:
                unmatched_keys.append(key)
        return unmatched_keys

    @staticmethod
    def _is_primitive_type(t) -> bool:
        return type(t) in (bool, str, int, float, None)
