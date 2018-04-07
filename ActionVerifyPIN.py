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

import sys
from BaseAction import BaseAction
from NitroKey import NitroKey

class ActionVerifyPIN(BaseAction):
	def __init__(self, cmdname, args):
		BaseAction.__init__(self, cmdname, args)
		nitrokey = NitroKey(verbose = (self.args.verbose > 0), so_path = self.args.so_path, pin = self.args.pin)
		if nitrokey.login():
			print("PIN correct.", file = sys.stderr)
		else:
			print("PIN was WRONG!", file = sys.stderr)
