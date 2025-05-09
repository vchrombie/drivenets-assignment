from abc import ABC, abstractmethod

"""
EXAMPLE for request to AI tool for creating a new decipher:

In the '/automation_utils/automation_utils/helpers/deciphers/' folder, there is a Decipher helpers intended for parsing string text and converting it to a structured objects.
All deciphers inherit from the base class Decipher. Each decipher class must implement the decipher(cli_response: str) -> object method.
Classes that represent data objects are located in '/automation_utils/automation_utils/data_objects/'.
Create a new decipher file called <new_decipher.py> in in '/automation_utils/automation_utils/data_objects/VENDOR_NAME/'. Implement there a decipher class called <NewDecipher> that inherits from Decipher and implements the decipher method that does the following:
The input 'cli_response' is a string text in the following format:

<provide a CLI output here ....>

As a result, it should provide a class object. Create a new class object for the result, called <NewDataObject> in '/automation_utils/automation_utils/data_objects/'.
Inside the decipher method, use the following mapping. The mapping defines how to extract data from the cli_response and assign it to corresponding attributes in the <NewDataObject>:

<A1> from the input corresponds to <A2> of the <NewDataObject>
<B1> from the input corresponds to <B2> of the <NewDataObject>

Implement a test to validate your implementation.
The tests reside in 'tests/automation_utils/test_parsers/' folder. Make the test similar to others in this folder.
"""


class Decipher(ABC):

    @abstractmethod
    def decipher(cli_response: str) -> object:
        pass
