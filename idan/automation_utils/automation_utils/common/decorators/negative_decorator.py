import logging
import collections
from functools import wraps

import orbital.common as common

logger = common.get_logger(__file__)


class NotRaisedException(Exception):
    """
    raises in case an expected exception wasn't raised during the validation process
    """


def negative(expected_exceptions=(Exception,)):
    """
    wrap validation in order to use same validation logic as negative test.
    negative validation check if an exception as raised, otherwise, NotRaisedException exception will raise.
    In addition, there is an option to look for specific exception message.


    after using the negative decorator, addition arguments should send to the function in order to invoke
    the negative behavior.

    the addition arguments are:
        negate_validation: specify if we expect for an exception from expected_exceptions
        matched_msg: if specified, checks if the exception message contain the text
        error_message: provides a custom failure message if the expected exception is not raised


    example:

        @negative(allowed_exceptions=ValueError)
        def validate_greater_then(number, anchor=3):
            if number <= anchor:
                raise ValueError(f"number({number}) is smaller then or equal to anchor({anchor})...")
        return True


        validate_greater_then(2) - will raise ValueError (as the validation should do)
        validate_greater_then(2, negate_validation=True) - will pass, due that we expect for an exception
        validate_greater_then(2, negate_validation=True ,matched_msg='foo') - will raise NotRaisedException, due
                                                                              that matched_msg not appears in the
                                                                              exception message

    :param expected_exceptions: check if a c function call raises any exception from expected_exception
            and raise a NotRaisedException exception otherwise
    """
    KEY = "negate_validation"
    EXPECTED_MSG = "matched_msg"
    ERR_MSG = "error_message"

    # support single or multiple exceptions
    if isinstance(expected_exceptions, collections.abc.Iterable):
        expected_exceptions = tuple(expected_exceptions)
    elif expected_exceptions is not None:
        expected_exceptions = (expected_exceptions,)

    def negate_decorator(func):

        @wraps(func)
        def negate_function(*args, **kwargs):
            exceptions_names = ",".join(
                [exception.__name__ for exception in expected_exceptions]
            )
            default_err_msg = (
                f"Exception of types {exceptions_names} isn’t raised during the function "
                f"'{func.__name__}' execution, although have expected."
            )

            # In case examining the content of the exception is not necessary, an empty string will set
            matched_msg = kwargs.pop(EXPECTED_MSG, "")

            # default behavior of the validation is not to expect for failure
            negate_validation = bool(kwargs.pop(KEY, False))

            # which message sent in case of expected exception didn't raised
            err_msg = kwargs.pop(ERR_MSG, default_err_msg)

            if negate_validation:
                logger.info(
                    f"The function '{func.__name__}' was invoked with negate_validation attribute. "
                    f"i.e. an exception should raise during the execution of this function.."
                )
            try:
                result = func(*args, **kwargs)

            except expected_exceptions as e:
                # check if an exception should raise
                if negate_validation:
                    # examining the content of the exception. i.e. if the content of exception is as expected
                    if matched_msg not in str(e):
                        raise NotRaisedException(
                            f"An exception type of '{e.__class__.__name__}' has raised but his "
                            f"content which is:'{str(e)}' don't contain in any way the expected"
                            f" content '{matched_msg}'"
                        )
                    logger.info(
                        f"An exception type of '{e.__class__.__name__}' has raised as expected with message="
                        f"'{str(e)}'"
                    )
                # Throws forward the exception
                else:
                    raise e

            # In case an exception did'nt raised
            else:
                # check if failure was expected
                if negate_validation:
                    raise NotRaisedException(err_msg)
                return result

        return negate_function

    return negate_decorator
