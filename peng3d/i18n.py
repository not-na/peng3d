#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  i18n.py
#
#  Copyright 2018-2022 notna <notna@apparat.org>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

__all__ = [
    "TranslationManager",
]

import glob
import re

from .util import ActionDispatcher

from typing import TYPE_CHECKING, Dict, List, Optional, Tuple, Any, Union

if TYPE_CHECKING:
    import peng3d


# TODO: add test cases for translations
class TranslationManager(ActionDispatcher):
    """
    Manages sets of translation files in multiple languages.

    This Translation System uses language codes to identify languages, there is
    no requirement to follow a specific standard, but it is recommended to use
    simple 2-digit codes like ``en`` and ``de``\\ , adding an underscore to
    define sub-languages like ``en_gb`` and ``en_us``\\ .

    Whenever a new translation file is needed, it will be parsed and then cached.
    This speeds up access times and also practically eliminates load times when
    switching languages.

    Several events are sent by this class, see :ref:`events-i18n`\\ .

    Most of these events are also sent as actions, these actions are described
    in the methods that cause them.

    There are also severale config options that determine the behaviour of this class.
    See :ref:`cfg-i18n` for more information.


    This Manager requires the :py:class:`~peng3d.resource.ResourceManager()` to
    be already initialized.
    """

    def __init__(self, peng: "peng3d.Peng"):
        if not peng.cfg["rsrc.enable"]:
            raise RuntimeError(
                "ResourceManager needs to be enabled to use Translations"
            )
        elif peng.rsrcMgr is None:
            raise RuntimeError(
                "ResourceManager needs to be initialized before TranslationManager"
            )

        self.peng: "peng3d.Peng" = peng

        self.lang: str = self.peng.cfg["i18n.lang"]

        self.cache: Dict[
            str, Dict[str, Dict[str, str]]
        ] = {}  # dict of dicts, first lang, then domain

        self.peng.sendEvent("peng3d:i18n.init", {"lang": self.lang, "i18n": self})
        self.setLang(self.peng.cfg["i18n.lang"])

    def setLang(self, lang: str) -> None:
        """
        Sets the default language for all domains.

        For recommendations regarding the format of the language code, see
        :py:class:`TranslationManager`\\ .

        Note that the ``lang`` parameter of both :py:meth:`translate()` and
        :py:meth:`translate_lazy()` will override this setting.

        Also note that the code won't be checked for existence or plausibility.
        This may cause the fallback strings to be displayed instead if the language
        does not exist.

        Calling this method will cause the ``setlang`` action and the
        :peng3d:event`peng3d:i18n.set_lang` event to be triggered. Note that both
        action and event will be triggered even if the language did not actually change.

        This method also automatically updates the :confval:`i18n.lang` config value.
        """
        self.lang = lang
        self.peng.cfg["i18n.lang"] = lang

        if lang not in self.cache:
            self.cache[lang] = {}

        self.doAction("setlang")
        self.peng.sendEvent("peng3d:i18n.set_lang", {"lang": self.lang, "i18n": self})

    def discoverLangs(self, domain: str = "*") -> List[str]:
        """
        Generates a list of languages based on files found on disk.

        The optional ``domain`` argument may specify a domain to use when checking
        for files. By default, all domains are checked.

        This internally uses the :py:mod:`glob` built-in module and the
        :confval:`i18n.lang.format` config option to find suitable filenames.
        It then applies the regex in :confval:`i18n.discover_regex` to extract the
        language code.
        """
        rsrc = self.peng.cfg["i18n.lang.format"].format(domain=domain, lang="*")
        pattern = self.peng.rsrcMgr.resourceNameToPath(
            rsrc, self.peng.cfg["i18n.lang.ext"]
        )
        files = glob.iglob(pattern)

        langs = set()
        r = re.compile(self.peng.cfg["i18n.discover_regex"])

        for f in files:
            m = r.fullmatch(f.replace("\\", "/"))
            if m is not None:
                langs.add(m.group("lang"))

        return list(langs)

    def translate(
        self, key: str, translate: bool = True, lang: Optional[str] = None
    ) -> str:
        """
        Translates the given key.

        If no language was given, the language last passed to :py:meth:`setLang()` will
        be used.

        If the translation key could not be found (e.g. because the language code is invalid),
        the key itself will be returned.

        Note that this method returns a string and thus does not have any way to modify
        the returned value if the language is changed by the user. If dynamic translation
        is required, :py:meth:`translate_lazy()` should be used instead.
        """
        if lang is None:
            lang = self.lang

        if not translate or key.count(":") != 1:
            return key
        domain, name = key.split(":")

        if domain not in self.cache[lang]:
            self.loadDomain(domain, lang)
        if (
            lang not in self.cache
            or domain not in self.cache[lang]
            or name not in self.cache[lang][domain]
        ):
            self.peng.sendEvent("peng3d:i18n.miss", {"key": key, "lang": lang})
            return key  # would just display the key to the user, good enough to be understood
        return self.cache[lang][domain][name]

    t = translate

    def translate_lazy(
        self,
        key: str,
        data: Optional[Dict] = None,
        translate: bool = True,
        lang: Optional[str] = None,
    ) -> "_LazyTranslator":
        """
        Lazily translates a given translation key.

        This method is similar to :py:meth:`translate()`\\ , but returns a special object
        rather than a string. This allows for on-the-fly changing of the language without
        having to re-set all the places where translated strings are used.

        Whenever the returned object is converted to a string by :py:func:`str()` or :py:func:`repr()`
        or is formatted using either the old ``%``\\ -notation or the newer :py:meth:`str.format()`\\ ,
        the translation key will be looked up again, in case the language has changed.

        Note that this requires support from the widgets (or other consumers of the returned value),
        namely that they only convert to string just prior to rendering and re-render either
        regularly or whenever either the ``setlang`` action or the :peng3d:event:`peng3d:i18n.set_lang` event
        is called.

        Most built-in widgets support this, but some special cases are not supported yet.
        For example, setting the window title dynamically requires using the ``caption_t``
        parameter instead of the raw ``caption`` parameter.
        """
        return _LazyTranslator(self, key, data, translate, lang)

    tl = translate_lazy

    def loadDomain(
        self, domain: str, lang: Optional[str] = None, encoding: str = "utf-8"
    ) -> bool:
        """
        Loads the translation data of a single domain for a specific language from disk
        into the cache.

        If no language was given, the current language is used.

        If the translation file could not be found or any errors occur while reading it,
        these errors will be silently discarded, only recognizable by a return value of ``False``\\ .

        If the load was successful, the action ``loaddomain`` will be executed and this
        method will return ``True``\\ .
        """
        if lang is None:
            lang = self.lang

        if lang not in self.cache:
            self.cache[lang][
                domain
            ] = {}  # prevents errors if function aborts prematurely

        rsrc = self.peng.cfg["i18n.lang.format"].format(domain=domain, lang=lang)
        if not self.peng.rsrcMgr.resourceExists(rsrc, self.peng.cfg["i18n.lang.ext"]):
            return False  # prevents errors
        fname = self.peng.rsrcMgr.resourceNameToPath(
            rsrc, self.peng.cfg["i18n.lang.ext"]
        )
        try:
            with open(fname, "r", encoding=encoding, errors="surrogateescape") as f:
                data = f.readlines()
        except Exception:
            return False  # prevents errors

        d = {}
        for line in data:
            line.strip()
            if line == "" or line.startswith("#"):
                continue
            ls = line.split("=")
            k = ls.pop(0)  # first ever useful application of pop
            v = "=".join(ls).strip()
            d[k] = v.replace("\\n", "\n")
        self.cache[lang][domain] = d

        self.doAction("loaddomain")
        return True

    def __getitem__(self, key: str) -> str:
        return self.translate(key)


class _LazyTranslator(object):
    _dynamic = True

    def __init__(
        self,
        i18n: TranslationManager,
        key: str,
        data: Optional[Dict] = None,
        translate: bool = True,
        lang: Optional[str] = None,
    ):
        self.i18n = i18n
        self.key = key
        self.data = data
        self.translate = translate
        self.lang = lang

    def __str__(self) -> str:
        t = self.i18n.translate(self.key, self.translate, self.lang)

        if self.data is not None:
            try:
                return t.format(**self.data)
            except Exception:
                return t
        else:
            return t

    def __repr__(self) -> str:
        return str(self)

    def __mod__(self, other: Union[Any, Tuple]) -> str:
        try:
            return str(self) % other
        except Exception:
            return str(self)

    def format(self, *args, **kwargs) -> str:
        try:
            return str(self).format(*args, **kwargs)
        except Exception:
            return str(self)
