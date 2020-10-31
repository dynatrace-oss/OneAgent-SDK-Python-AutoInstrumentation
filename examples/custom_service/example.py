import autodynatrace


@autodynatrace.trace
def my_method():
    # Service: __main__
    # Request: my_method
    print("Hello World!")


@autodynatrace.trace("MyService")
def my_service_method():
    # Service: MyService
    # Request: my_service_method
    print("Hello World!")


@autodynatrace.trace("MyService", "my_method")
def my_custom_method():
    # Service: MyService
    # Request: my_method
    print("Hello World!")


def main():
    my_method()
    my_service_method()
    my_custom_method()


if __name__ == "__main__":
    main()
