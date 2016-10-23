from setuptools import setup, find_packages


requirements = [
    'configobj==5.0.6',
    'networkx==1.9.1',
    'numpy==1.9.2',
    'pandas==0.15.2',
    'Pillow==3.4.2',
    'scikit-image==0.11.2',
    'scikit-learn==0.15.2',
    'scipy==0.15.1'
]

test_requirements = [
    'matplotlib==1.4.3',
    'pytest==2.6.4'
]

setup(
    name="Texture_Synthesis",
    version="0.1",
    description='Procedural image processor',
    long_description=open('README.md').read() + "\n",
    packages=find_packages(),
    install_requires=requirements,
    test_requirements=test_requirements,

    entry_points={
        'console_scripts': [
            'main = Texture_Synthesis.Application:main'
        ]
    },

    author="Shoeboxam",
    author_email="shoeboxam@gmail.com",
    license="License :: OSI Approved :: MIT License",
    url="https://github.com/Shoeboxam/Texture_Synthesis",
    classifiers=[
        'Programming Language :: Python :: 3'
    ]
)
