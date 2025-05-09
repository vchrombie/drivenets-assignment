import threading
from time import sleep, monotonic

from timeout_decorator import timeout

import orbital.common as common

from . import consts
from ..exceptions import SigKillTimeout

logger = common.get_logger(__file__)


def wait(
    timeout_seconds,
    expected_result=True,
    sleep_time=consts.SECONDS_BETWEEN_COMMANDS,
    delay=0,
    func=None,
    func_name=None,
    error_message="",
    severity=logger.error,
    allowed_exceptions=(),
    raise_original=False,
    min_runtime=0,
    retry=True,
    reduce_logs=False,
    consecutive=1,
    stable_time=0,
    **kwargs,
):
    """
    waiting x seconds for a function to return an expected result.
    raises TimeoutExpired if expected result is not matched after the defined time
    can be used as a decorator or with lambda functions.

    :param timeout_seconds: number of seconds to wait for expected_value
    :param expected_result: expected return value of the passed function. use 'None' to wait for exception-free run
    :param sleep_time: number of seconds to wait between iterations
    :param delay: in seconds, wait before first executing the function
    :param func: lambda function
    :param func_name: a name for lambda functions, used in error messages
    :param error_message: error message for TimeoutError exception and logger
    :param severity: logger severity to use when an error_message is passed
    :param allowed_exceptions: a tuple of exceptions to ignore
    :param raise_original: raise the original exception if it was the result of original function
    :param min_runtime: the minimum allowed time for a function to return the expected value.
           if a function finish too quick, TimeoutError is raised
    :param retry: if True, run original method 1 more time after timeout
    :param reduce_logs: indicates whether to print debug message with result of the wrapping function or not
    :param consecutive: number of times that the expected result should be returned in a row
    :param stable_time: number of seconds that the expected result should be returned in a row
    """
    # use signals only when running from the main thread, to prevent the error : 'signal only works in main thread'
    # WA : QA-1227 timeout signal from non-main thread
    use_signals = threading.current_thread() == threading.main_thread()

    def wait_decorator(decorator_func):
        name = func_name if func_name else decorator_func.__name__
        error = (
            "function {} was killed with SIGKILL by timeout decorator, "
            "after waiting extra {} seconds for it to finish naturally".format(
                name, consts.EXTRA_TIMEOUT_SECONDS
            )
        )

        @timeout(
            (timeout_seconds or 0) + consts.EXTRA_TIMEOUT_SECONDS + delay,
            exception_message=error,
            timeout_exception=SigKillTimeout,
            use_signals=use_signals,
        )
        def wait_for_time(*args, **kwargs):
            if delay:
                logger.debug(
                    f"waiting {delay} seconds before executing function '{name}'"
                )
                sleep(delay)
            start_time = monotonic()
            end_time = start_time + timeout_seconds
            _expected_res = (
                expected_result
                if expected_result is not None
                else "an exception-free result"
            )
            logger.debug(
                f"waiting {timeout_seconds} seconds for {name} to return {_expected_res}..."
            )
            result = None
            _retry = True
            _first_expected_result_time = None
            while _retry:
                if monotonic() > end_time:
                    if not retry:
                        break  # don't retry command if timeout expires
                    _retry = False  # try to execute original function 1 more time after timeout expires
                try:
                    result = decorator_func(*args, **kwargs)
                except allowed_exceptions as e:
                    result = e  # show exception details as the returned value
                else:
                    if result == expected_result or expected_result is None:
                        # if expected result is returned, or the expected result is exception-free
                        _first_expected_result_time = (
                            _first_expected_result_time or monotonic()
                        )
                        func_runtime = monotonic() - start_time
                        if func_runtime < min_runtime:
                            err = (
                                f"function {name} returned the expected value '{expected_result}', faster then "
                                f"expected, after {func_runtime} seconds, last returned value: '{result}'"
                            )
                            severity(err)
                            raise TimeoutError(err)
                        logger.debug(
                            f"function '{name}' returned the expected result '{result}' in "
                            f"{round(func_runtime, 2)} seconds"
                        )
                        if consecutive <= 1 or _validate_consecutive(
                            consecutive,
                            allowed_exceptions,
                            decorator_func,
                            result,
                            sleep_time,
                            reduce_logs,
                            *args,
                            **kwargs,
                        ):
                            # if the same result was returned 'consecutive' times in a row
                            if (
                                monotonic() - _first_expected_result_time
                                >= stable_time
                            ):
                                if stable_time:
                                    logger.debug(
                                        f"the expected result was returned and was stable for "
                                        f"{stable_time} seconds"
                                    )
                                return result
                            if not reduce_logs:
                                logger.debug(
                                    f"continuing to execute the method, until it is stable for "
                                    f"{stable_time} seconds"
                                )
                        else:
                            _first_expected_result_time = None
                if not reduce_logs and _first_expected_result_time:
                    logger.debug(
                        "'{}' returned '{}', keep waiting for '{}'...".format(
                            name, result, _expected_res
                        )
                    )
                sleep(sleep_time)

            # if last returned value is exception, raise it if flag is true
            if isinstance(result, BaseException) and raise_original:
                raise result

            # if expected value not returned:
            if error_message:
                err = error_message + "\nlast returned value: '{}'".format(
                    result
                )
            else:
                err = (
                    f"function {name} did not return {_expected_res} after {timeout_seconds} seconds, "
                    f"last returned value: '{result}'"
                )

            severity(err)

            raise TimeoutError(err)

        return (
            wait_for_time if timeout_seconds else decorator_func
        )  # don't warp original method if no timeout is set

    if func:
        return wait_decorator(func)()
    else:
        return wait_decorator


def _validate_consecutive(
    consecutive,
    allowed_exceptions,
    decorator_func,
    result,
    sleep_time,
    reduce_logs,
    *args,
    **kwargs,
):
    """
    helper method to validate that the expected result is returned 'consecutive' times in a row.
    params according to 'wait' logic.
    :return: True if all consecutive results are the same
    """
    for i in range(
        1, consecutive
    ):  # if the same result should be returned consecutively
        if not reduce_logs:
            logger.debug(
                f"validating consecutive result number #{i + 1}/{consecutive}"
            )
        sleep(sleep_time)
        try:
            new_result = decorator_func(*args, **kwargs)
        except allowed_exceptions as e:
            new_result = e
        if new_result != result:
            if not reduce_logs:
                logger.debug(
                    f"result number #{i + 1}/{consecutive}, '{new_result}', is different from the expected "
                    f"result"
                )
            return False
    logger.debug(
        f"the expected result was returned {consecutive} times in a row"
    )
    return True
