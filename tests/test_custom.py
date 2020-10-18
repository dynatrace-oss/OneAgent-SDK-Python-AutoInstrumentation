import sys
import os

import autodynatrace
import autodynatrace.wrappers.custom.wrapper as custom_wrapper


@autodynatrace.trace
def module_function():
    return 1


class MyClass:
    def class_method(self):
        pass

    @staticmethod
    def static_method(self):
        pass


def test_custom_service_name():
    my_class = MyClass()
    assert custom_wrapper.generate_service_name(module_function) == "tests.test_custom"
    assert custom_wrapper.generate_service_name(my_class.class_method) == "MyClass"

    if sys.version_info[0] == 2:
        assert custom_wrapper.generate_service_name(my_class.static_method) == "tests.test_custom"
        assert custom_wrapper.generate_service_name(MyClass.static_method) == "tests.test_custom"
    else:
        assert custom_wrapper.generate_service_name(my_class.static_method) == "MyClass"
        assert custom_wrapper.generate_service_name(MyClass.static_method) == "MyClass"

    os.environ["AUTODYNATRACE_CUSTOM_SERVICE_NAME"] = "CustomServiceName"
    assert custom_wrapper.generate_service_name(module_function) == "CustomServiceName"


def test_custom_service_instrumentation():
    assert module_function() == 1
