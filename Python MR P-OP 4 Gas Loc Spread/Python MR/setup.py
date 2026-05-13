import setuptools

long_description = "EPNL Volue Algo Trading"


# ===============================
setuptools.setup(
    name = 'MaR Loop',
    version = '1.0',
    author = "bicc-data-science",
    author_email = "macunagonzalez@pzem.nl",
    description = "bicc data science library",
    package_dir = {
        '' : 'src/python',
        },
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://dev.azure.com/pzemdevops/BICC%20Data%20Science/_git/sample_model",
    packages = setuptools.find_packages('src/python') + setuptools.find_packages('lib'),
    classifiers = [
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires = '>=3.7',
    platforms = ['any'],
    install_requires=[
        'numpy==1.23.4',
        'pandas==1.5.1',
        'pytz==2021.1',
        'requests==2.25.1',
        'easydict==1.10',
    ]
)
