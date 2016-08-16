# -*- coding: utf-8 -*-
#
# Copyright (c) 2016 -- Lars Heuer - Semagia <http://www.semagia.com/>.
# All rights reserved.
#
# License: BSD License
#
"""\
QR Code and Micro QR Code implementation.

"QR Code" and "Micro QR Code" are registered trademarks of DENSO WAVE INCORPORATED.

:author:       Lars Heuer (heuer[at]semagia.com)
:organization: Semagia - http://www.semagia.com/
:license:      BSD License
"""
from __future__ import absolute_import, unicode_literals
import sys
import io
from . import encoder
from .encoder import QRCodeError, ErrorLevelError, ModeError, MaskError, \
    VersionError, DataOverflowError
from . import writers, utils

__version__ = '0.1.2'

__all__ = ('make', 'make_qr', 'make_micro', 'QRCode', 'QRCodeError',
           'ErrorLevelError', 'ModeError', 'MaskError', 'VersionError',
           'DataOverflowError')


def make(content, error=None, version=None, mode=None, mask=None, encoding=None,
         eci=False, micro=None):
    """\
    Creates a (Micro) QR Code.

    This is main entry point to create QR Codes and Micro QR Codes.

    Aside from `content`, all parameters are optional and an optimal (minimal)
    (Micro) QR Code is generated.

    :param content: The data to encode. Either a Unicode string, an integer or
            bytes. If bytes are provided, the `encoding` parameter should be
            used to specify the used encoding.
    :type content: str, int, bytes
    :param error: Error correction level. If ``None`` (default), error
            correction level ``M`` is used (note: Micro QR Code version M1 does
            not support error correction. If an explicit error level is used,
            a M1 QR Code won't be generated).
            Valid values: ``None`` (allowing generation of M1 codes or use error
            correction level "M"), "L", "M", "Q", "H" (error correction level
            "H" isn't available for Micro QR Codes).

            =====================================   ===========================
            Error correction level                  Error correction capability
            =====================================   ===========================
            L                                       recovers  7% of data
            M (Segno's default unless version M1)   recovers 15% of data
            Q                                       recovers 25% of data
            H (not available for Micro QR Codes)    recovers 30% of data
            =====================================   ===========================

            Higher error levels require larger QR Codes (see also `version`
            parameter).

            The `error` parameter is case insensitive.
    :type error: str or None
    :param version: QR Code version. If the value is ``None`` (default), the
            minimal version which fits for the input data will be used.
            Valid values: "M1", "M2", "M3", "M4" (for Micro QR Codes) or an
            integer between 1 and 40 (for QR Codes).
            The `version` parameter is case insensitive.
    :type version: int, str or None.
    :param mode: "numeric", "alphanumeric", "byte", or "kanji". If the value is
            ``None`` (default) the appropriate mode will automatically be
            determined.
            If `version` refers a to Micro QR Code, this function may raise a
            :py:class:`ModeError` if the provided `mode` is not supported.

            ============    =======================
            Mode            (Micro) QR Code Version
            ============    =======================
            numeric         1 - 40, M1, M2, M3, M4
            alphanumeric    1 - 40,     M2, M3, M4
            byte            1 - 40,         M3, M4
            kanji           1 - 40,         M3, M4
            ============    =======================

            The `mode` parameter is case insensitive.

    :type mode: str or None
    :param mask: Data mask. If the value is ``None`` (default), the
            appropriate data mask is choosen automatically. If the `mask`
            parameter if provided, this function may raise a :py:exc:`MaskError`
            if the mask is invalid.
    :type mask: int or None
    :param encoding: Indicates the encoding in mode "byte". By default
            (`encoding` is ``None``) the implementation tries to use the
            standard conform ISO/IEC 8859-1 encoding and if it does not fit, it
            will use UTF-8. Note that no ECI mode indicator is inserted by
            default (see `eci`).
            The `encoding` parameter is case insensitive.
    :type encoding: str or None
    :param bool eci: Indicates if binary data which does not use the default
            encoding (ISO/IEC 8859-1) should enforce the ECI mode. Since a lot
            of QR Code readers do not support the ECI mode, this feature is
            disabled by default and the data is encoded in the provided
            `encoding` using the usual "byte" mode. Set `eci` to ``True`` if
            an ECI header should be inserted into the QR Code. Note that
            the implementation may not know the ECI designator for the provided
            `encoding` and may raise an exception if the ECI designator cannot
            be found.
            The ECI mode is not supported by Micro QR Codes.
    :param micro: If `version` is ``None`` this parameter can be used
            to allow the creation of a Micro QR Code.
            If set to ``False``, a QR Code is generated. If set to
            ``None`` (default) a Micro QR Code may be generated if applicable.
            If set to ``True`` the algorithm generates a Micro QR Code or
            raises an exception if the `mode` is not compatible or the `content`
            is too large for Micro QR Codes.
    :type micro: bool or None
    :raises: :py:exc:`QRCodeError`: In case of a problem. In fact, it's more
            likely that a derived exception is thrown:
            :py:exc:`ModeError`: In case of problems with the mode (i.e. invalid
            mode or invalid `mode` / `version` combination.
            :py:exc:`VersionError`: In case the `version` is invalid or the
            `micro` parameter contradicts the provided `version`.
            :py:exc:`ErrorLevelError`: In case the error level is invalid or the
            error level is not supported by the provided `version`.
            :py:exc:`DataOverflowError`: In case the data does not fit into a
            (Micro) QR Code or it does not fit into the provided `version`.
            :py:exc:`MaskError`: In case an invalid data mask was specified.
    :rtype: QRCode
    """
    return QRCode(encoder.encode(content, error, version, mode, mask, encoding,
                                 eci, micro))


def make_qr(content, error=None, version=None, mode=None, mask=None,
            encoding=None, eci=False):
    """\
    Creates a QR Code (never a Micro QR Code).

    See :py:func:`make` for a description of the parameters.

    :rtype: QRCode
    """
    return make(content, error=error, version=version, mode=mode, mask=mask,
                encoding=encoding, eci=eci, micro=False)


def make_micro(content, error=None, version=None, mode=None, mask=None,
               encoding=None):
    """\
    Creates a Micro QR Code.

    See :py:func:`make` for a description of the parameters.

    Note: Error correction level "H" isn't available for Micro QR Codes. If
    used, this function raises a :py:class:`segno.ErrorLevelError`.

    :rtype: QRCode
    """
    return make(content, error=error, version=version, mode=mode, mask=mask,
                encoding=encoding, micro=True)


class QRCode(object):
    """\
    Represents a (Micro) QR Code.
    """
    def __init__(self, code):
        """\
        Initializes the QR Code object.

        :param code: An object with a ``matrix``, ``version``, ``error``,
            ``mask`` and ``segments`` attribute.
        """
        self.matrix = code.matrix
        """\
        Returns the matrix (tuple of bytearrays).
        """
        self._version = code.version
        self._error = code.error
        self.mask = code.mask
        """\
        Returns the data mask pattern reference (an integer).
        """
        self._mode = code.segments[0].mode if len(code.segments) == 1 else None

    @property
    def version(self):
        """\
        (Micro) QR Code version. Either a string ("M1", "M2", "M3", "M4") or
        an integer in the range of 1 .. 40.
        """
        return encoder.get_version_name(self._version)

    @property
    def error(self):
        """\
        Error correction level; either a string ("L", "M", "Q", "H") or ``None``
        if the QR Code provides no error correction (Micro QR Code version M1)
        """
        if self._error is None:
            return None
        return encoder.get_error_name(self._error)

    @property
    def mode(self):
        """\
        String indicating the mode ("numeric", "alphanumeric", "byte", "kanji").
        May be ``None`` if multiple modes are used.
        """
        if self._mode is not None:
            return encoder.get_mode_name(self._mode)
        return None

    @property
    def designator(self):
        """\
        Returns the version and error correction level as string `V-E` where
        `V` represents the version number and `E` the error level.
        """
        version = str(self.version)
        return '-'.join((version, self.error) if self.error else (version,))

    @property
    def default_border_size(self):
        """\
        Indicates the default border size aka quiet zone.
        """
        return utils.get_default_border_size(self._version)

    @property
    def is_micro(self):
        """\
        Indicates if this QR Code is a Micro QR Code
        """
        return self._version < 1

    def __eq__(self, other):
        return self.matrix == other.matrix

    def symbol_size(self, scale=1, border=None):
        """\
        Returns the symbol size (width x height) with the provided border and
        scaling factor.

        :param scale: Indicates the size of a single module (default: 1).
                The size of a module depends on the used output format; i.e.
                in a PNG context, a scaling factor of 2 indicates that a module
                has a size of 2 x 2 pixel. Some outputs (i.e. SVG) accept
                floating point values.
        :type scale: int or float
        :param int border: The border size or ``None`` to specify the
                default quiet zone (4 for QR Codes, 2 for Micro QR Codes).
        :rtype: tuple (width, height)
        """
        return utils.get_symbol_size(self._version, scale=scale, border=border)

    def show(self, delete_after=20, scale=10, border=None, color='#000',
             background='#fff'):  # pragma: no cover
        """\
        Displays this QR code.

        This method is mainly intended for debugging purposes.

        This method saves the output of the :py:meth:`png` method (by default
        with a scaling factor of 10) to a temporary file and opens it with the
        standard PNG viewer application or within the standard webbrowser.
        The temporary file is deleted afterwards (unless `delete_after` is set
        to ``None``).

        If this method does not show any result, try to increase the
        `delete_after` value or set it to ``None``

        :param delete_after: Time in seconds to wait till the temporary file is
                deleted.
        """
        import os
        import time
        import tempfile
        import webbrowser
        import threading
        try:  # Python 2
            from urlparse import urljoin
            from urllib import pathname2url
        except ImportError:  # Python 3
            from urllib.parse import urljoin
            from urllib.request import pathname2url

        def delete_file(name):
            time.sleep(delete_after)
            try:
                os.unlink(name)
            except OSError:
                pass

        f = tempfile.NamedTemporaryFile('wb', suffix='.png', delete=False)
        try:
            self.png(f, scale=scale, color=color, background=background,
                     border=border)
        except:
            f.close()
            os.unlink(f.name)
            raise
        f.close()
        webbrowser.open_new_tab(urljoin('file:', pathname2url(f.name)))
        if delete_after is not None:
            t = threading.Thread(target=delete_file, args=(f.name,))
            t.start()

    def svg_data_uri(self, scale=1, border=None, color='#000', background=None,
                     xmldecl=False, svgns=True, title=None, desc=None,
                     svgid=None, svgclass='segno', lineclass='qrline',
                     omitsize=False, unit='', encoding='utf-8', svgversion=None,
                     nl=False, encode_minimal=False, omit_charset=False):
        """\
        Converts the QR Code into a SVG data URI.

        The XML declaration is omitted by default (set ``xmldecl`` to ``True``
        to enable it), further the newline is omitted by default (set ``nl`` to
        ``True`` to enable it).

        Aside from the missing ``out`` parameter and the different ``xmldecl``
        and ``nl`` default values and the additional parameter ``encode_minimal``
        and ``omit_charset`` this function uses the same parameters as the
        usual SVG serializer.

        :param bool encode_minimal: Indicates if the resulting data URI should
                        use minimal percent encoding (disabled by default).
        :param bool omit_charset: Indicates if the ``;charset=...`` should be omitted
                        (disabled by default)
        :rtype: str
        """
        return writers.as_svg_data_uri(self.matrix, self._version, scale=scale,
                                border=border, color=color,
                                background=background, xmldecl=xmldecl,
                                svgns=svgns, title=title, desc=desc,
                                svgid=svgid, svgclass=svgclass,
                                lineclass=lineclass, omitsize=omitsize,
                                unit=unit, encoding=encoding,
                                svgversion=svgversion, nl=nl,
                                encode_minimal=encode_minimal,
                                omit_charset=omit_charset)

    def png_data_uri(self, scale=1, border=None, color='#000', background='#fff',
                     compresslevel=9, addad=True):
        """\
        Converts the provided `qrcode` into a PNG data URI.

        :rtype: str
        """
        return writers.as_png_data_uri(self.matrix, self._version, scale=scale,
                                border=border, color=color,
                                background=background,
                                compresslevel=compresslevel, addad=addad)

    def terminal(self, out=None, border=None):
        """\
        Serializes the matrix as ANSI escape code.

        :param out: Filename or a file-like object supporting to write text.
                If ``None`` (default), the matrix is written to ``stdout``.
        :param int border: Integer indicating the size of the quiet zone.
                If set to ``None`` (default), the recommended border size
                will be used (``4`` for QR Codes, ``2`` for a Micro QR Codes).
        """
        writers.write_terminal(self.matrix, self._version, out or sys.stdout,
                               border)

    def save(self, file_or_name, kind=None, **kw):
        """\
        Serializes the QR Code in one of the supported formats.
        The serialization format depends on the filename extension.

        :param file_or_name: A filename or a writable file-like object with a
                ``name`` attribute.
        :param kind: If the desired output format cannot be extracted from
                the filename, this parameter can be used to indicate the
                serialization format (i.e. "svg" to enforce SVG output)
        :param kw: Any of the supported keywords by the specific serialization
                method.
        """
        writers.save(self.matrix, self._version, file_or_name, kind, **kw)

    def __getattr__(self, name):
        """\
        This is used to plug-in external serializers.

        When a "to_<name>" method is invoked, this method tries to find
        a ``segno.plugin.converter`` plugin with the provided ``<name>``.
        If such a plugin exists, a callable function is returned. The result
        of invoking the function depends on the plugin.
        """
        if name.startswith('to_'):
            from pkg_resources import iter_entry_points
            from functools import partial
            for ep in iter_entry_points(group='segno.plugin.converter',
                                        name=name[3:]):
                plugin = ep.load()
                return partial(plugin, self)
        raise AttributeError('{0} object has no attribute {1}'
                             .format(self.__class__, name))