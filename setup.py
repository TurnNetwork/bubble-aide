from setuptools import (
    setup,
    find_packages,
)


deps = {
    'bubble-aide': [
        'bubble.py>=0.1.0',
        'eth_account>=0.8.0',
        'eth_hash>=0.5.1',
        'eth_keys>=0.4.0',
        'eth_typing>=3.0.0',
        'eth_utils>=2.1.0',
        'rlp>=3.0.0',
        'gql>=3.0.0rc0',
    ]
}

with open('./README.md', encoding='utf-8') as readme:
    long_description = readme.read()

setup(
    name='bubble-aide',
    # *IMPORTANT*: Don't manually change the version here. Use the 'bumpversion' utility.
    version='2.1.7',
    description="""bubble aide""",
    # long_description=long_description,
    # long_description_content_type='text/markdown',
    author='Shing',
    author_email='shinnng@outlook.com',
    url='https://github.com/shinnng/bubble-aide',
    include_package_data=True,
    install_requires=['bubble-sdk>=0.1.0'],
    py_modules=['bubble_aide'],
    extras_require=deps,
    license="MIT",
    zip_safe=False,
    package_data={'bubble-aide': ['py.typed']},
    keywords='bubble-aide',
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
