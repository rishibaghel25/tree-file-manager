from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tree-file-manager",
    version="0.1.0",  
    author="Rishi",
    author_email="rishinamansingh@gmail.com",
    description="A modern file manager with tree view for Linux systems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rishibaghel25/tree-file-manager",
    license="MIT", 
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: System :: Filesystems",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.7",
    install_requires=[
        "PyQt5>=5.15.0",
        "psutil>=5.8.0",
    ],
    entry_points={
        "console_scripts": [
            "tree-file-manager=tree_file_manager.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "tree_file_manager": ["icons/*.png"],
    },
    zip_safe=False,
)