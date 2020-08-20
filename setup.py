from setuptools import setup, find_packages

setup(
    name="autodynatrace",
    version="1.0.63",
    packages=find_packages(),
    package_data={"autodynatrace": ["wrappers/*"]},
    install_requires=["wrapt>=1.11.2", "oneagent-sdk>=1.3.0", "six>=1.10.0", "autowrapt>=1.0"],
    entry_points={"autodynatrace": ["string = autodynatrace:load"]},
    python_requires=">=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*",
    author="David Lopes",
    author_email="david.lopes@dynatrace.com",
    description="Auto instrumentation for the OneAgent SDK",
    long_description="The autodynatrace package will auto instrument your python apps",
    url="https://github.com/dlopes7/autodynatrace",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved",
        "License :: OSI Approved :: Apache Software License",  # 2.0
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: CPython",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Topic :: System :: Monitoring",
    ],
    project_urls={"Issue Tracker": "https://github.com/dlopes7/autodynatrace/issues"},
)
