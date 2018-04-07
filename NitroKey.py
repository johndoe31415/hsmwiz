#	nitrotool - Frontend for NitroKey USB HSM
#	Copyright (C) 2018-2018 Johannes Bauer
#
#	This file is part of nitrotool.
#
#	nitrotool is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; this program is ONLY licensed under
#	version 3 of the License, later versions are explicitly excluded.
#
#	nitrotool is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#	Johannes Bauer <JohannesBauer@gmx.de>

import os
import subprocess
import tempfile
from CmdTools import CmdTools

class NitroKey(object):
	_INITIAL_SOPIN = "3537363231383830"
	_INITIAL_PIN = "648219"

	def __init__(self, verbose = False, pin = None, sopin = None, so_path = None):
		self.__verbose = verbose
		self.__pin = pin
		self.__sopin = sopin
		self.__sopath = so_path
		self.__initialized = self.__identify()
		if self.__verbose:
			print("Default SO-PIN: %s    Default PIN: %s" % (self._INITIAL_SOPIN, self._INITIAL_PIN))

	def __identify(self):
		proc = subprocess.Popen([ "sc-hsm-tool" ], stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
		(stdout, _) = proc.communicate()
		if self.__verbose:
			print(stdout.decode())
			print("~" * 120)
		if b"No smart card readers" in stdout:
			raise Exception("No smart card readers connected.")

		return b"has never been initialized" not in stdout

	def _shared_obj(self, soname):
		if self.__sopath is None:
			raise Exception("No shared object search path was given, cannot locate '%s'." % (soname))
		for path in self.__sopath.split(":"):
			path = os.path.realpath(os.path.expanduser(path))
			if not path.endswith("/"):
				path += "/"
			path += soname
			if os.path.isfile(path):
				return path
		raise Exception("Could not find shared object '%s' anywhere in SO-searchpath '%s'." % (soname, self.__sopath))

	def _call(self, cmd):
		if self.__verbose:
			print(CmdTools.cmdline(cmd))
		subprocess.check_call(cmd)

	@property
	def initialized(self):
		return self.__initialized

	def initialize(self):
		assert(not self.intialized)
		cmd = [ "sc-hsm-tool", "--initialize", "--so-pin", self._INITIAL_SOPIN, "--pin", self._INITIAL_PIN ]
		self._call(cmd)

	def list(self):
		self._call([ "pkcs15-tool", "--dump" ])

	def login(self):
		cmd = [ "pkcs11-tool", "--module", self._shared_obj("opensc-pkcs11.so"), "--login", "--list-objects" ]
		if self.__pin is not None:
			cmd += [ "--pin", self.__pin ]
		try:
			self._call(cmd)
			return True
		except subprocess.CalledProcessError:
			return False

	def unblock_pin(self):
		cmd = [ "pkcs11-tool", "--module", self._shared_obj("opensc-pkcs11.so"), "--login", "--login-type", "so" ]
		if self.__sopin is not None:
			cmd += [ "--so-pin", self.__sopin ]
		cmd += [ "--init-pin" ]
		self._call(cmd)

	def explore(self):
		if self._verbose:
			print("Verify PIN   : verify chv129")
			print("Change PIN   : change chv129 \"648219\" \"123456\"")
			print("Change SO-PIN: change chv136 \"3537363231383830\" \"16b72e4528d5063e\"")
			print("=" * 120)
		self._call([ "opensc-explorer", "--mf", "aid:E82B0601040181C31F0201" ])

	def keygen(self, key_spec, key_id, key_label = None):
		cmd = [ "pkcs11-tool", "--module", self._shared_obj("opensc-pkcs11.so"), "--login" ]
		if self.__pin is not None:
			cmd += [ "--pin", self.__pin ]
		cmd += [ "--keypairgen", "--key-type", key_spec, "--id", str(key_id) ]
		if key_label is not None:
			cmd += [ "--label", key_label ]
		self._call(cmd)

	def _print_pubkey_derfile(self, derfile_name):
		for (openssl_cmd, name) in [ ("rsa", "RSA"), ("ec", "ECC") ]:
			try:
				pem_pubkey = subprocess.check_output([ "openssl", openssl_cmd, "-pubin", "-inform", "der", "-in", derfile_name ], stderr = subprocess.DEVNULL)
				print("# %s key:" % (name))
				print(pem_pubkey.decode().rstrip("\r\n"))
				return
			except subprocess.CalledProcessError:
				pass
		raise Exception("Could not successfully decode DER-encoded public key in '%s'." % (derfile_name))

	def getpubkey(self, key_id, key_label = None):
		assert((key_id is None) ^ (key_label is None))
		with tempfile.NamedTemporaryFile(prefix = "pubkey_", suffix = ".der") as pubkey_derfile:
			cmd = [ "pkcs11-tool", "--module", self._shared_obj("opensc-pkcs11.so"), "--login" ]
			if self.__pin is not None:
				cmd += [ "--pin", self.__pin ]
			if key_id is not None:
				cmd += [ "--id", str(key_id) ]
			if key_label is not None:
				cmd += [ "--label", key_label ]
			cmd += [ "--read-object", "--type", "pubkey" ]
			cmd += [ "--output-file", pubkey_derfile.name ]
			self._call(cmd)
			self._print_pubkey_derfile(pubkey_derfile.name)

	def removekey(self, key_id, key_label = None):
		assert((key_id is None) ^ (key_label is None))
		cmd = [ "pkcs11-tool", "--module", self._shared_obj("opensc-pkcs11.so"), "--login" ]
		if self.__pin is not None:
			cmd += [ "--pin", self.__pin ]
		if key_id is not None:
			cmd += [ "--id", str(key_id) ]
		if key_label is not None:
			cmd += [ "--label", key_label ]
		cmd += [ "--delete-object", "--type", "privkey" ]
		self._call(cmd)

	def check_engine(self):
		cmd = [ "openssl", "engine" ]
		cmd += [ "-tt" ]
		cmd += [ "-pre", "SO_PATH:%s" % (self._shared_obj("libpkcs11.so")) ]
		cmd += [ "-pre", "ID:pkcs11" ]
		cmd += [ "-pre", "LIST_ADD:1" ]
		cmd += [ "-pre", "LOAD" ]
		cmd += [ "-pre", "MODULE_PATH:%s" % (self._shared_obj("opensc-pkcs11.so")) ]
		cmd += [ "dynamic" ]
		self._call(cmd)

	def _execute_openssl_engine(self, user_openssl_cmd):
		openssl_cmds = [ ]
		openssl_cmd = [ "engine" ]
		openssl_cmd += [ "-tt" ]
		openssl_cmd += [ "-pre", "SO_PATH:%s" % (self._shared_obj("libpkcs11.so")) ]
		openssl_cmd += [ "-pre", "ID:pkcs11" ]
		openssl_cmd += [ "-pre", "LIST_ADD:1" ]
		openssl_cmd += [ "-pre", "LOAD" ]
		if self.__pin is not None:
			openssl_cmd += [ "-pre", "PIN:%s" % (self.__pin) ]
		openssl_cmd += [ "-pre", "MODULE_PATH:%s" % (self._shared_obj("opensc-pkcs11.so")) ]
		openssl_cmd += [ "dynamic" ]
		openssl_cmds.append(openssl_cmd)
		openssl_cmds.append(user_openssl_cmd)

		openssl_cmds_str = "\n".join(CmdTools.cmdline(cmd) for cmd in openssl_cmds) + "\n"
		openssl_cmds = openssl_cmds_str.encode()

		output = subprocess.check_output([ "openssl" ], input = openssl_cmds)
		print(output)

	def gencsr(self, key_id, subject = "/CN=NitroKey Example"):
		openssl_cmd = [ "req", "-new", "-x509" ]
		openssl_cmd += [ "-keyform", "engine", "-engine", "pkcs11" ]
		openssl_cmd += [ "-key", "0:%d" % (key_id) ]
		openssl_cmd += [ "-subj", subject ]
		self._execute_openssl_engine(openssl_cmd)

#		cmd += [ "-key", "0:%s" % (str(key_id)) ]
		#-pre SO_PATH:/usr/local/lib/engines/engine_pkcs11.so -pre ID:pkcs11 -pre LIST_ADD:1 -pre LOAD -pre MODULE_PATH:/usr/local/lib/pkcs11/opensc-pkcs11.so
#		cmd = [ "openssl", "req", "-new", "-keyform", "engine", "-engine", "dynamic" ]

#		cmd = [ "pkcs11-tool", "--module", self._shared_obj("opensc-pkcs11.so"), "--login" ]
#		if self.__pin is not None:
#			cmd += [ "--pin", self.__pin ]
#		if key_id is not None:
#			cmd += [ "--id", str(key_id) ]
#		if key_label is not None:
#			cmd += [ "--label", key_label ]
#		cmd += [ "--delete-object", "--type", "privkey" ]
