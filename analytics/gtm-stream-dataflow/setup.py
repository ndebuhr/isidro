import setuptools

setuptools.setup(
    name='gtm_stream',
    version='0.0.1',
    install_requires=[
        'google-cloud-storage>=2.6.0,<3.0.0'
    ],
    packages=setuptools.find_packages()
)