import sys
import os

import autodynatrace
import autodynatrace.wrappers.custom.wrapper as custom_wrapper


@autodynatrace.trace
def module_function():
    return 1


def another_function():
    pass


class MyClass:
    def class_method(self):
        pass

    @staticmethod
    def static_method(self):
        pass


@autodynatrace.trace("Service")
def decorated_service_only():
    return 1


@autodynatrace.trace(method="method")
def decorated_method_only():
    return 1


@autodynatrace.trace("Service", "method")
def decorated_service_and_method():
    return 1

def test_custom_service_name():
    my_class = MyClass()

    os.environ.pop("AUTODYNATRACE_CUSTOM_SERVICE_USE_FQN", None)
    os.environ.pop("AUTODYNATRACE_CUSTOM_SERVICE_NAME", None)
    assert custom_wrapper.generate_service_name(module_function) == "tests.test_custom"
    assert custom_wrapper.generate_service_name(my_class.class_method) == "MyClass"
    assert custom_wrapper.generate_service_name(classmethod(my_class.class_method)) == "MyClass"
    assert custom_wrapper.generate_service_name(module_function) == custom_wrapper.generate_service_name(another_function)

    if sys.version_info[0] == 2:
        assert custom_wrapper.generate_service_name(my_class.static_method) == "tests.test_custom"
        assert custom_wrapper.generate_service_name(MyClass.static_method) == "tests.test_custom"
    else:
        assert custom_wrapper.generate_service_name(my_class.static_method) == "MyClass"
        assert custom_wrapper.generate_service_name(MyClass.static_method) == "MyClass"

    os.environ["AUTODYNATRACE_CUSTOM_SERVICE_NAME"] = "CustomServiceName"
    assert custom_wrapper.generate_service_name(module_function) == "CustomServiceName"


def test_custom_service_name_fqn_true():
    my_class = MyClass()

    os.environ["AUTODYNATRACE_CUSTOM_SERVICE_USE_FQN"] = "TRUE"
    os.environ.pop("AUTODYNATRACE_CUSTOM_SERVICE_NAME", None)
    assert custom_wrapper.generate_service_name(module_function) == "tests.test_custom"
    assert custom_wrapper.generate_service_name(my_class.class_method) == "tests.test_custom.MyClass"
    assert custom_wrapper.generate_service_name(classmethod(my_class.class_method)) == "tests.test_custom.MyClass"
    assert custom_wrapper.generate_service_name(module_function) == custom_wrapper.generate_service_name(another_function)

    if sys.version_info[0] == 2:
        assert custom_wrapper.generate_service_name(my_class.static_method) == "tests.test_custom"
        assert custom_wrapper.generate_service_name(MyClass.static_method) == "tests.test_custom"
    else:
        assert custom_wrapper.generate_service_name(my_class.static_method) == "tests.test_custom.MyClass"
        assert custom_wrapper.generate_service_name(MyClass.static_method) == "tests.test_custom.MyClass"

    os.environ["AUTODYNATRACE_CUSTOM_SERVICE_NAME"] = "CustomServiceName"
    assert custom_wrapper.generate_service_name(module_function) == "CustomServiceName"


def test_custom_method_name_fqn_false():
    my_class = MyClass()

    os.environ.pop("AUTODYNATRACE_CUSTOM_SERVICE_USE_FQN", None)
    os.environ.pop("AUTODYNATRACE_CUSTOM_SERVICE_NAME", None)
    assert custom_wrapper.generate_method_name(module_function) == "module_function"
    assert custom_wrapper.generate_method_name(my_class.class_method) == "class_method"
    assert custom_wrapper.generate_method_name(classmethod(my_class.class_method)) == "class_method"
    assert custom_wrapper.generate_method_name(another_function) == "another_function"

    assert custom_wrapper.generate_method_name(my_class.static_method) == "static_method"
    assert custom_wrapper.generate_method_name(MyClass.static_method) == "static_method"

    os.environ["AUTODYNATRACE_CUSTOM_SERVICE_NAME"] = "CustomServiceName"
    assert custom_wrapper.generate_method_name(module_function) == "tests.test_custom.module_function"
    assert custom_wrapper.generate_method_name(my_class.class_method) == "MyClass.class_method"
    assert custom_wrapper.generate_method_name(classmethod(my_class.class_method)) == "MyClass.class_method"
    assert custom_wrapper.generate_method_name(another_function) == "tests.test_custom.another_function"

    if sys.version_info[0] == 2:
        assert custom_wrapper.generate_method_name(my_class.static_method) == "tests.test_custom.static_method"
        assert custom_wrapper.generate_method_name(MyClass.static_method) == "tests.test_custom.static_method"
    else:
        assert custom_wrapper.generate_method_name(my_class.static_method) == "MyClass.static_method"
        assert custom_wrapper.generate_method_name(MyClass.static_method) == "MyClass.static_method"


def test_custom_method_name_fqn_true():
    my_class = MyClass()

    os.environ["AUTODYNATRACE_CUSTOM_SERVICE_USE_FQN"] = "TRUE"
    os.environ.pop("AUTODYNATRACE_CUSTOM_SERVICE_NAME", None)
    assert custom_wrapper.generate_method_name(module_function) == "tests.test_custom.module_function"
    assert custom_wrapper.generate_method_name(my_class.class_method) == "tests.test_custom.MyClass.class_method"
    assert custom_wrapper.generate_method_name(classmethod(my_class.class_method)) == "tests.test_custom.MyClass.class_method"
    assert custom_wrapper.generate_method_name(another_function) == "tests.test_custom.another_function"

    os.environ["AUTODYNATRACE_CUSTOM_SERVICE_NAME"] = "CustomServiceName"
    assert custom_wrapper.generate_method_name(module_function) == "tests.test_custom.module_function"
    assert custom_wrapper.generate_method_name(my_class.class_method) == "tests.test_custom.MyClass.class_method"
    assert custom_wrapper.generate_method_name(classmethod(my_class.class_method)) == "tests.test_custom.MyClass.class_method"
    assert custom_wrapper.generate_method_name(another_function) == "tests.test_custom.another_function"

    if sys.version_info[0] == 2:
        assert custom_wrapper.generate_method_name(my_class.static_method) == "tests.test_custom.static_method"
        assert custom_wrapper.generate_method_name(MyClass.static_method) == "tests.test_custom.static_method"
    else:
        assert custom_wrapper.generate_method_name(my_class.static_method) == "tests.test_custom.MyClass.static_method"
        assert custom_wrapper.generate_method_name(MyClass.static_method) == "tests.test_custom.MyClass.static_method"


def test_custom_service_instrumentation():
    assert module_function() == 1
    assert decorated_method_only() == 1
    assert decorated_service_only() == 1
    assert decorated_service_and_method() == 1


def test_decorator_with_arguments():
    assert custom_wrapper.generate_service_name(module_function, "Service") == "Service"
    assert custom_wrapper.generate_method_name(module_function, "method") == "method"
