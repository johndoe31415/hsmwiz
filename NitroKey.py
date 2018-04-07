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

	def login(self, with_sopin = False):
		cmd = [ "pkcs11-tool", "--module", self._shared_obj("opensc-pkcs11.so"), "--login", "--list-objects" ]
		if with_sopin:
			cmd += [ "--login-type", "so" ]
			if self.__sopin is not None:
				cmd += [ "--so-pin", self.__sopin ]
		else:
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

		openssl_cmds_str = "\n".join(CmdTools.cmdline(cmd) for cmd in openssl_cmds)
		if self.__verbose:
			print("OpenSSL command lines:")
			print(openssl_cmds_str)
		openssl_cmds = openssl_cmds_str.encode() + b"\n"

		output = subprocess.check_output([ "openssl" ], input = openssl_cmds)
		return output

	def _print_csr(self, pem_bytes):
		output = subprocess.check_output([ "openssl", "req", "-text" ], input = pem_bytes)
		print(output.decode().rstrip("\r\n"))

	def _gencsr_crt(self, key_id, subject, validity_days = None, hashfnc = None):
		with tempfile.NamedTemporaryFile(prefix = "csr_crt_", suffix = ".pem") as temp_csr_crt:
			openssl_cmd = [ "req", "-new" ]
			openssl_cmd += [ "-keyform", "engine", "-engine", "pkcs11" ]
			openssl_cmd += [ "-key", "0:%d" % (key_id) ]
			if validity_days is not None:
				openssl_cmd += [ "-x509", "-days", str(validity_days) ]
			if hashfnc is not None:
				openssl_cmd += [ "-%s" % (hashfnc) ]
			openssl_cmd += [ "-subj", subject ]
			openssl_cmd += [ "-out", temp_csr_crt.name ]
			if self.__verbose:
				openssl_cmd += [ "-text" ]
			output = self._execute_openssl_engine(openssl_cmd)
			with open(temp_csr_crt.name) as f:
				print(f.read().rstrip("\r\n"))

	def gencsr(self, key_id, subject = "/CN=NitroKey Example"):
		return self._gencsr_crt(key_id = key_id, subject = subject)

	def gencrt(self, key_id, subject = "/CN=NitroKey Example", validity_days = 365, hashfnc = "sha256"):
		return self._gencsr_crt(key_id = key_id, subject = subject, validity_days = validity_days, hashfnc = hashfnc)

	def putcrt(self, crt_derdata, cert_id, cert_label = None):
		with tempfile.NamedTemporaryFile("wb", prefix = "crt_", suffix= ".der") as crt_tempfile:
			crt_tempfile.write(crt_derdata)
			crt_tempfile.flush()

			cmd = [ "pkcs11-tool", "--module", self._shared_obj("opensc-pkcs11.so"), "--login" ]
			if self.__pin is not None:
				cmd += [ "--pin", self.__pin ]
			if cert_id is not None:
				cmd += [ "--id", str(cert_id) ]
			if cert_label is not None:
				cmd += [ "--label", cert_label ]
			cmd += [ "--write-object", crt_tempfile.name, "--type", "cert" ]
			self._call(cmd)

	def change_pin(self, new_value):
		cmd = [ "pkcs11-tool", "--module", self._shared_obj("opensc-pkcs11.so"), "--login" ]
#		, "--login-type", "so" ]
#		if self.__sopin is not None:
#			cmd += [ "--so-pin", self.__sopin ]
		if self.__pin is not None:
			cmd += [ "--pin", self.__pin ]
		cmd += [ "--change-pin", "--new-pin", str(new_value) ]
		self._call(cmd)

	def change_sopin(self, new_value):
		cmd = [ "pkcs11-tool", "--module", self._shared_obj("opensc-pkcs11.so"), "--login" ]
		cmd += [ "--login-type", "so" ]
		if self.__sopin is not None:
			cmd += [ "--so-pin", self.__sopin ]
		cmd += [ "--change-pin", "--new-pin", str(new_value) ]
		self._call(cmd)

	def format(self):
		assert(self.__sopin is not None)
		if not self.login(with_sopin = True):
			raise Exception("Login with SO-PIN failed. Cannot format smartcard.")
		cmd = [ "sc-hsm-tool", "--initialize", "--so-pin", self.__sopin, "--pin", self._INITIAL_PIN ]
		self._call(cmd)
		if self.__sopin != self._INITIAL_SOPIN:
			self.change_sopin(self._INITIAL_SOPIN)
		print("Smartcard successfully formatted. New SO-PIN: %s and PIN: %s" % (self._INITIAL_SOPIN, self._INITIAL_PIN))
