from setuptools import setup

setup(
    name="nemesiskarutachan",
    version="0.0.1",
    license="MIT",
    install_requires=[
        "fire",
        "mwt",
        "pandas",
        "pillow",
        "python-telegram-bot"
    ],
    packages=["nemesiskarutachan"],
    entry_points={
        "console_scripts": [
            "nemesiskarutachan=nemesiskarutachan.karutabot:run"
        ]
    }
)
