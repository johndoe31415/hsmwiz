import setuptools

with open("README.md") as f:
	long_description = f.read()

setuptools.setup(
	name = "hsmwiz",
	packages = setuptools.find_packages(),
	version = "0.0.1",
	license = "gpl-3.0",
	description = "Frontend for OpenSC, pkcs11tool and pkcs15tool to ease handling of HSM smartcards",
	long_description = long_description,
	long_description_content_type = "text/markdown",
	author = "Johannes Bauer",
	author_email = "joe@johannes-bauer.com",
	url = "https://github.com/johndoe31415/hsmwiz",
	download_url = "https://github.com/johndoe31415/hsmwiz/archive/0.0.1.tar.gz",
	keywords = [ "hsm", "pcsc", "smart", "card", "frontend", "openssl" ],
	entry_points = {
		"console_scripts": [
			"hsmwiz = hsmwiz.__main__:main"
		]
	},
	classifiers = [
		"Development Status :: 5 - Production/Stable",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
		"Programming Language :: Python :: 3",
		"Programming Language :: Python :: 3 :: Only",
		"Programming Language :: Python :: 3.5",
		"Programming Language :: Python :: 3.6",
		"Programming Language :: Python :: 3.7",
		"Programming Language :: Python :: 3.8",
	],
)
