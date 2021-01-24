import setuptools
from setuptools.command.install import install
import json


class DownloadNltkPackages(install):
    def run(self):
        install.run(self)
        try:
            import nltk
            print('Installing nltk required packages...')
        except ImportError:
            raise ImportError('nltk is required')

        nltk.download('punkt')
        nltk.download('stopwords')
        nltk.download('wordnet')
        nltk.download('averaged_perceptron_tagger')


if __name__ == '__main__':

    with open('README.md', 'r',  encoding='UTF-8') as fh:
        long_description = fh.read()

    with open('setup.json', 'r') as sf:
        setup_infos = json.load(sf)

    setuptools.setup(include_package_data=True,
                     cmdclass={'install': DownloadNltkPackages},
                     packages=setuptools.find_packages(),
                     long_description=long_description,
                     setup_requires=['nltk >= 3'],
                     install_requires=['nltk >= 3'],
                     **setup_infos)
