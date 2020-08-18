#	hsmwiz - Frontend for NitroKey USB HSM
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

import os
import sys
from .BaseAction import BaseAction
from .NitroKey import NitroKey

class ActionChangePIN(BaseAction):
	@staticmethod
	def _gen_int_pin(digits):
		assert(digits >= 2)
		min_value = 10 ** (digits - 1)
		max_value = (10 ** digits) - 1
		val_range = max_value - min_value + 1
		# Choose candidate so large that the bias because of the modulo
		# operation becomes neglegible
		candidate = int.from_bytes(os.urandom(8 + digits), byteorder = "little")
		result = min_value + (candidate % val_range)
		assert(min_value <= result <= max_value)
		return result

	def __init__(self, cmdname, args):
		BaseAction.__init__(self, cmdname, args)
		if self.args.affect_so_pin:
			pin = None
			sopin = self.args.old
		else:
			pin = self.args.old
			sopin = None

		if self.args.randomize_new:
			if self.args.affect_so_pin:
				new_value = os.urandom(8).hex()
				print("!!! Do not lose this !!!")
				print("--> New SO-PIN: %s <--" % (new_value))
				print("!!! Do not lose this !!!")
			else:
				new_value = self._gen_int_pin(6)
				print("New PIN: %s" % (new_value))
		else:
			new_value = self.args.new

		nitrokey = NitroKey(verbose = (self.args.verbose > 0), so_path = self.args.so_path, pin = pin, sopin = sopin)
		if self.args.affect_so_pin:
			nitrokey.change_sopin(new_value)
		else:
			nitrokey.change_pin(new_value)
