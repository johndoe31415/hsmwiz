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

class CmdTools(object):
	@classmethod
	def cmdline(cls, cmd):
		def escape(text):
			if (" " in text) or ("\"" in text):
				return "\"%s\"" % (text.replace("\"", "\\\""))
			else:
				return text
		return " ".join(escape(arg) for arg in cmd)
