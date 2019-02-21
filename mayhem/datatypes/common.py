#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  mayhem/datatypes/structure.py
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following disclaimer
#    in the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of the project nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  'AS IS' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#  OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

import _ctypes
import collections
import ctypes

_function_cache = {}
_function_cache_entry = collections.namedtuple('FunctionCacheEntry', ('restype', 'argtypes', 'flags'))

class MayhemCFuncPtr(ctypes._CFuncPtr):
	_argtypes_ = ()
	_restype_ = None
	_flags_ = 0
	@property
	def address(self):
		return ctypes.cast(self, ctypes.c_void_p).value

	def duplicate(self, other):
		if callable(other):
			if isinstance(other, ctypes._CFuncPtr):
				other = ctypes.cast(other, ctypes.c_void_p).value
		elif not isinstance(other, int):
			other = ctypes.cast(other, ctypes.c_void_p).value
		return self.__class__(other)

	@classmethod
	def new(cls, name, restype=None, argtypes=None, flags=0):
		new = type(name, (cls,), {
			'_argtypes_': argtypes,
			'_restype_': restype,
			'_flags_': flags
		})
		return new

class MayhemStructure(ctypes.Structure):
	pass

# why is this even wrong
# def _WINFUNCTYPE(restype, use_errno=False, use_last_error=False, *argtypes):
# 	flags = _ctypes.FUNCFLAG_STDCALL
# 	if use_errno:
# 		flags |= _ctypes.FUNCFLAG_USE_ERRNO
# 	if use_last_error:
# 		flags |= _ctypes.FUNCFLAG_USE_LASTERROR
# 	cache_entry = _function_cache_entry(restype=restype, argtypes=argtypes, flags=flags)
# 	function = _function_cache.get(cache_entry)
# 	if function is not None:
# 		return function
# 	FunctionType = MayhemCFuncPtr.new('CFunctionType', **cache_entry._asdict())
# 	_function_cache[cache_entry] = FunctionType
# 	# print type(FunctionType)
# 	# print FunctionType.__class__
# 	return FunctionType

# ripped from https://github.com/debasishm89/OpenXMolar/blob/master/ExtDepLibs/winappdbg/win32/__init__.py
def _WINFUNCTYPE(restype, *argtypes, **kw):
        flags = ctypes._FUNCFLAG_STDCALL
        if kw.pop("use_errno", False):
            flags |= ctypes._FUNCFLAG_USE_ERRNO
        if kw.pop("use_last_error", False):
            flags |= ctypes._FUNCFLAG_USE_LASTERROR
        if kw:
            raise ValueError("unexpected keyword argument(s) %s" % kw.keys())
        try:
            return ctypes._win_functype_cache[(restype, argtypes, flags)]
        except KeyError:
			class WinFunctionType(ctypes._CFuncPtr):
				_argtypes_ = argtypes
				_restype_ = restype
				_flags_ = flags
				@property
				def address(self):
					return ctypes.cast(self, ctypes.c_void_p).value
			ctypes._win_functype_cache[(restype, argtypes, flags)] = WinFunctionType
			return WinFunctionType 
