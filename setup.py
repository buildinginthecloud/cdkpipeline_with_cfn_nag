import setuptools


with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="cdkpipeline",
    version="0.0.1",

    description="An empty CDK Python app",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="author",

    package_dir={"": "cdkpipeline"},
    packages=setuptools.find_packages(where="cdkpipeline"),

    install_requires=[
        # ⚠️ CRITICAL SECURITY WARNING ⚠️
        # AWS CDK v1 reached End-of-Support on June 1, 2023
        # This version no longer receives security updates
        # Known CVEs: CVE-2024-45037, CVE-2025-2598, CVE-2025-23206
        # MIGRATE TO: aws-cdk-lib>=2.178.0, constructs>=10.0.0
        "aws-cdk.core==1.121.0",  # ❌ DEPRECATED - Security risk
    ],

    # SECURITY: Python 3.6 and 3.7 are End-of-Life and contain vulnerabilities
    # Updated to require Python 3.8+ (minimum supported version)
    # Recommended: Python 3.9+ for best security posture
    python_requires=">=3.8",

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",

        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        # Removed EOL Python versions (3.6, 3.7) - security risk
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",

        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",

        "Typing :: Typed",
    ],
)
