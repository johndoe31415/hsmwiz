#	nitrotool - Frontend for NitroKey USB HSM
#	Copyright (C) 2018-2020 Johannes Bauer
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

import sys
import subprocess
from .BaseAction import BaseAction
from .NitroKey import NitroKey

class ActionPutCRT(BaseAction):
	def __init__(self, cmdname, args):
		BaseAction.__init__(self, cmdname, args)
		crt_derdata = subprocess.check_output([ "openssl", "x509", "-outform", "der", "-in", self.args.crt_pemfile ])
		nitrokey = NitroKey(verbose = (self.args.verbose > 0), so_path = self.args.so_path, pin = self.args.pin)
		nitrokey.putcrt(crt_derdata = crt_derdata, cert_id = self.args.id, cert_label = self.args.label)
