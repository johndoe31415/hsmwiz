#!/usr/bin/python3
#	hsmwiz - Simplified handling of Hardware Security Modules
#	Copyright (C) 2018-2020 Johannes Bauer
#
#	This file is part of hsmwiz.
#
#	hsmwiz is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; this program is ONLY licensed under
#	version 3 of the License, later versions are explicitly excluded.
#
#	hsmwiz is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#	Johannes Bauer <JohannesBauer@gmx.de>

import sys
from .MultiCommand import MultiCommand
from .ActionIdentify import ActionIdentify
from .ActionVerifyPIN import ActionVerifyPIN
from .ActionCheckEngine import ActionCheckEngine
from .ActionInit import ActionInit
from .ActionFormat import ActionFormat
from .ActionChangePIN import ActionChangePIN
from .ActionExplore import ActionExplore
from .ActionUnblock import ActionUnblock
from .ActionKeyGen import ActionKeyGen
from .ActionGetPublicKey import ActionGetPublicKey
from .ActionRemoveKey import ActionRemoveKey
from .ActionGenCSR import ActionGenCSR
from .ActionPutCRT import ActionPutCRT
from .FriendlyArgumentParser import baseint

_default = {
	"sopath":	"/usr/local/lib:/usr/lib:/usr/lib/x86_64-linux-gnu:/usr/lib/x86_64-linux-gnu/openssl-1.0.2/engines:/usr/lib/x86_64-linux-gnu/engines-1.1",
}

mc = MultiCommand()
def genparser(parser):
	parser.add_argument("-v", "--verbose", action = "count", default = 0, help = "Increase verbosity. Can be specified multiple times.")
mc.register("identify", "Check if a HSM is connected and list all contents", genparser, action = ActionIdentify)

def genparser(parser):
	parser.add_argument("--pin", metavar = "pin", type = str, help = "Specifies the PIN/SO-PIN of the smartcard. If this argument is not given, the command will ask for it interactively.")
	parser.add_argument("--verify-sopin", action = "store_true", help = "Instead of specifying/verifying the PIN, verify the SO-PIN instead.")
	parser.add_argument("--so-path", metavar = "path", type = str, default = _default["sopath"], help = "Search path, separated by ':' characters, in which to look for shared objects like opensc-pkcs11.so. Defaults to %(default)s")
	parser.add_argument("-v", "--verbose", action = "count", default = 0, help = "Increase verbosity. Can be specified multiple times.")
mc.register("verifypin", "Try to login a HSM by entering a PIN or SO-PIN", genparser, action = ActionVerifyPIN)

def genparser(parser):
	parser.add_argument("--so-path", metavar = "path", type = str, default = _default["sopath"], help = "Search path, separated by ':' characters, in which to look for shared objects like opensc-pkcs11.so. Defaults to %(default)s")
	parser.add_argument("-v", "--verbose", action = "count", default = 0, help = "Increase verbosity. Can be specified multiple times.")
mc.register("checkengine", "Check if the OpenSSL engine driver works", genparser, action = ActionCheckEngine)

def genparser(parser):
	parser.add_argument("-v", "--verbose", action = "count", default = 0, help = "Increase verbosity. Can be specified multiple times.")
mc.register("init", "Initialize the smartcard for the first time, set default SO-PIN and PIN", genparser, action = ActionInit)

def genparser(parser):
	parser.add_argument("--so-pin", metavar = "so-pin", type = str, required = True, help = "Specifies the current SO-PIN. Mandatory argument.")
	parser.add_argument("--so-path", metavar = "path", type = str, default = _default["sopath"], help = "Search path, separated by ':' characters, in which to look for shared objects like opensc-pkcs11.so. Defaults to %(default)s")
	parser.add_argument("-v", "--verbose", action = "count", default = 0, help = "Increase verbosity. Can be specified multiple times.")
mc.register("format", "Reinitialize the smartcard completely (removing all keys and certificates) and set SO-PIN and PIN back to their factory default", genparser, action = ActionFormat)

def genparser(parser):
	parser.add_argument("--old", metavar = "pin/so-pin", type = str, help = "Specifies the old PIN or SO-PIN of the smartcard. If this argument is not given, the command will ask for it interactively.")
	group = parser.add_mutually_exclusive_group()
	group.add_argument("--new", metavar = "pin/so-pin", type = str, help = "Specifies the new PIN or SO-PIN of the smartcard. If this argument is not given, the command will ask for it interactively.")
	group.add_argument("--randomize-new", action = "store_true", help = "Randomize the new PIN or SO-PIN and print the new value on the command line.")
	parser.add_argument("--affect-so-pin", action = "store_true", help = "By default, the PIN is changed. When this option is given, the SO-PIN is changed instead.")
	parser.add_argument("--so-path", metavar = "path", type = str, default = _default["sopath"], help = "Search path, separated by ':' characters, in which to look for shared objects like opensc-pkcs11.so. Defaults to %(default)s")
	parser.add_argument("-v", "--verbose", action = "count", default = 0, help = "Increase verbosity. Can be specified multiple times.")
mc.register("changepin", "Change device PIN or SO-PIN", genparser, action = ActionChangePIN)

def genparser(parser):
	parser.add_argument("-v", "--verbose", action = "count", default = 0, help = "Increase verbosity. Can be specified multiple times.")
mc.register("explore", "Explore the smartcard structure interactively", genparser, action = ActionExplore)

def genparser(parser):
	parser.add_argument("--so-pin", metavar = "so-pin", type = str, help = "Specifies the SO-PIN that should be used for authorizing unblocking, in ASCII format. If this argument is not given, the command will ask for it interactively.")
	parser.add_argument("--pin", metavar = "pin", type = str, help = "Specifies the PIN that should be set after unblocking, in ASCII format. If this argument is not given, the command will ask for it interactively.")
	parser.add_argument("--so-path", metavar = "path", type = str, default = _default["sopath"], help = "Search path, separated by ':' characters, in which to look for shared objects like opensc-pkcs11.so. Defaults to %(default)s")
	parser.add_argument("-v", "--verbose", action = "count", default = 0, help = "Increase verbosity. Can be specified multiple times.")
mc.register("unblock", "Unblock the transponder's blocked PIN using the SO-PIN", genparser, action = ActionUnblock)

def genparser(parser):
	parser.add_argument("--id", metavar = "key_id", type = baseint, default = 1, help = "Specifies the key ID to use for generating the new key. Must be an integer and defaults to %(default)d.")
	parser.add_argument("--label", metavar = "key_label", type = str, help = "Specifies the key label to use for generating the new key.")
	parser.add_argument("--pin", metavar = "pin", type = str, help = "Specifies the PIN of the smartcard. If this argument is not given, the command will ask for it interactively.")
	parser.add_argument("--so-path", metavar = "path", type = str, default = _default["sopath"], help = "Search path, separated by ':' characters, in which to look for shared objects like opensc-pkcs11.so. Defaults to %(default)s")
	parser.add_argument("-v", "--verbose", action = "count", default = 0, help = "Increase verbosity. Can be specified multiple times.")
	parser.add_argument("keyspec", metavar = "keyspec", type = str, help = "Key specification string to generate. Can be either 'rsa:BITLENGTH' or 'EC:CURVENAME'. Examples are 'rsa:1024', 'EC:brainpool256r1' or 'EC:prime256v1'.")
mc.register("keygen", "Create a new private keypair on the smartcard", genparser, action = ActionKeyGen, aliases = [ "genkey" ])

def genparser(parser):
	group = parser.add_mutually_exclusive_group()
	group.add_argument("--id", metavar = "key_id", type = baseint, help = "Specifies the key ID to fetch.")
	group.add_argument("--label", metavar = "key_label", type = str, help = "Specifies the key label to fetch.")
	parser.add_argument("--pin", metavar = "pin", type = str, help = "Specifies the PIN of the smartcard. If this argument is not given, the command will ask for it interactively.")
	parser.add_argument("-f", "--key-format", choices = [ "pem", "ssh" ], default = "pem", help = "Specifies how the retrieved key should be displayed; can be either of %(choices)s, defaults to %(default)s.")
	parser.add_argument("--so-path", metavar = "path", type = str, default = _default["sopath"], help = "Search path, separated by ':' characters, in which to look for shared objects like opensc-pkcs11.so. Defaults to %(default)s")
	parser.add_argument("-v", "--verbose", action = "count", default = 0, help = "Increase verbosity. Can be specified multiple times.")
mc.register("getkey", "Fetch a public key from the smartcard", genparser, action = ActionGetPublicKey, aliases = [ "getpubkey" ])

def genparser(parser):
	group = parser.add_mutually_exclusive_group()
	group.add_argument("--id", metavar = "key_id", type = baseint, help = "Specifies the key ID to remove.")
	group.add_argument("--label", metavar = "key_label", type = str, help = "Specifies the key label to remove.")
	parser.add_argument("--pin", metavar = "pin", type = str, help = "Specifies the PIN of the smartcard. If this argument is not given, the command will ask for it interactively.")
	parser.add_argument("--so-path", metavar = "path", type = str, default = _default["sopath"], help = "Search path, separated by ':' characters, in which to look for shared objects like opensc-pkcs11.so. Defaults to %(default)s")
	parser.add_argument("-v", "--verbose", action = "count", default = 0, help = "Increase verbosity. Can be specified multiple times.")
mc.register("removekey", "Remove a keypair from the smartcard", genparser, action = ActionRemoveKey, aliases = [ "delkey", "deletekey" ])

def genparser(parser):
	parser.add_argument("-s", "--subject", metavar = "subject", type = str, default = "/CN=Hardware Security Module Example", help = "Specifies the CSR subject. Defaults to \"%(default)s\".")
	parser.add_argument("-i", "--id", metavar = "key_id", type = baseint, default = 1, help = "Specifies the key ID of which to include the public key into the CSR. Defaults to %(default)d.")
	parser.add_argument("--pin", metavar = "pin", type = str, help = "Specifies the PIN of the smartcard. If this argument is not given, the command will ask for it interactively.")
	parser.add_argument("--so-path", metavar = "path", type = str, default = _default["sopath"], help = "Search path, separated by ':' characters, in which to look for shared objects like opensc-pkcs11.so. Defaults to %(default)s")
	parser.add_argument("-v", "--verbose", action = "count", default = 0, help = "Increase verbosity. Can be specified multiple times.")
mc.register("gencsr", "Generate a certificate signing request from a HSM-contained private key", genparser, action = ActionGenCSR)

def genparser(parser):
	parser.add_argument("-s", "--subject", metavar = "subject", type = str, default = "/CN=Hardware Security Module Example", help = "Specifies the certificate subject. Defaults to \"%(default)s\".")
	parser.add_argument("--validity-days", metavar = "days", type = int, default = 365, help = "Time in days that the self-signed certificate is valid for. Defaults to %(default)d days.")
	parser.add_argument("--hashfnc", metavar = "hashfnc", type = str, default = "sha256", help = "Hash function that is used during signing. Defaults to %(default)s.")
	parser.add_argument("-i", "--id", metavar = "key_id", type = baseint, default = 1, help = "Specifies the key ID of which to include the public key into the CSR. Defaults to %(default)d.")
	parser.add_argument("--pin", metavar = "pin", type = str, help = "Specifies the PIN of the smartcard. If this argument is not given, the command will ask for it interactively.")
	parser.add_argument("--so-path", metavar = "path", type = str, default = _default["sopath"], help = "Search path, separated by ':' characters, in which to look for shared objects like opensc-pkcs11.so. Defaults to %(default)s")
	parser.add_argument("-v", "--verbose", action = "count", default = 0, help = "Increase verbosity. Can be specified multiple times.")
mc.register("gencrt", "Generate a self-signed certificate from a HSM-contained private key", genparser, action = ActionGenCSR)

def genparser(parser):
	parser.add_argument("-i", "--id", metavar = "cert_id", type = int, default = 1, help = "Specifies the cert ID under which the certificate will be stored on the smartcard. Defaults to %(default)d.")
	parser.add_argument("--label", metavar = "cert_label", type = str, help = "Specifies the certificate's label.")
	parser.add_argument("--pin", metavar = "pin", type = str, help = "Specifies the PIN of the smartcard. If this argument is not given, the command will ask for it interactively.")
	parser.add_argument("--so-path", metavar = "path", type = str, default = _default["sopath"], help = "Search path, separated by ':' characters, in which to look for shared objects like opensc-pkcs11.so. Defaults to %(default)s")
	parser.add_argument("-v", "--verbose", action = "count", default = 0, help = "Increase verbosity. Can be specified multiple times.")
	parser.add_argument("crt_pemfile", metavar = "crt_pemfile", type = str, help = "Certificate to put on the smartcart, in PEM format.")
mc.register("putcrt", "Put a certificate on the smartcard", genparser, action = ActionPutCRT)

mc.run(sys.argv[1:])
