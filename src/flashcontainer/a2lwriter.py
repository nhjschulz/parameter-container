""" Write A2L parameter description file
"""
# BSD 3-Clause License
#
# Copyright (c) 2022-2023, Haju Schulz (haju.schulz@online.de)
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#


from typing import Dict
from pathlib import Path

import flashcontainer.datamodel as DM
from flashcontainer.byteconv import ByteConvert

class A2lWriter(DM.Walker):
    """A2l file writer"""

    _TYPE_MAPPING = {
        DM.ParamType.UINT8: ("UBYTE", 0, 0xFF),
        DM.ParamType.UINT16: ("UWORD", 0, 0xFFFF),
        DM.ParamType.UINT32: ("ULONG", 0, 0xFFFFFFFF),
        DM.ParamType.UINT64: ("A_UINT64", 0, 0xFFFFFFFFFFFFFFFF),
        DM.ParamType.INT8: ("SBYTE", -128, +127),
        DM.ParamType.INT16: ("SWORD", -32768, +32767),
        DM.ParamType.INT32: ("SLONG", -2147483648, +2147483647),
        DM.ParamType.INT64: ("_A_INT64", -9223372036854775808, +9223372036854775807),
        DM.ParamType.FLOAT32: ("FLOAT32_IEEE", 1.175494351E-38, 3.402823466E+38),
        DM.ParamType.FLOAT64: ("FLOAT64_IEEE", 2.2250738585072014E-308, 1.7976931348623158E+308),
        DM.ParamType.UTF8: ("UBYTE", 0, 0xFF)
    }

    _BYTEORDER_MAPPING = {
        DM.Endianness.LE: "MSB_LAST",
        DM.Endianness.BE: "MSB_FIRST"
    }

    def __init__(self, model: DM.Model, options: Dict[str, any]):
        super().__init__(model, options)
        self.a2l_file = None

    def pre_run(self) -> None:
        filename = Path.joinpath(
            self.options.get("DESTDIR"),
            self.options.get("BASENAME") + ".a2l")

        print(f"Generating A2l description {filename}.")

        self.a2l_file = filename.open(mode='w')

        self.a2l_file.write(
            f"/* AUTOGENERATED by {self.options.get('PNAME')} "
            f"{self.options.get('VERSION')}\n"
            f" * A2L parameter description for {self.options.get('INPUT')}\n"
            f" * cmd: {self.options.get('CMDLINE')}\n"
        )

        if self.options.get("STATICOUTPUT") is False:
            self.a2l_file.write(
                f" * Date: {self.options.get('DATETIME')}\n"
                f" * Buildkey: {self.options.get('GUID')}\n"
            )
        self.a2l_file.write(" */\n\n")
        self.a2l_file.write("ASAP2_VERSION 1 70\n")
        self.a2l_file.write(f"/begin PROJECT {self.options.get('BASENAME')} \"\"\n\n")
        self.a2l_file.write(f"  /begin HEADER \"{self.options.get('BASENAME')}\"\n")
        self.a2l_file.write("  /end HEADER \n\n")

    def begin_container(self, container: DM.Container) -> None:
        self.a2l_file.write(f"  /begin MODULE {container.name} \"\"\n")

    def end_container(self, container: DM.Container) -> None:
        self.a2l_file.write("\n  /end MODULE\n")

    def begin_block(self, block: DM.Block) -> None:
        if block.header is not None:
            self.a2l_file.write(
                "\n"
                "    /begin TYPEDEF_MEASUREMENT\n"
                f"        T_{block.name}_USHORT\n"
                "        \"block 16 bit parameter type\"\n"
                f"        {self._TYPE_MAPPING[DM.ParamType.UINT16][0]}\n"
                "        NO_COMPU_METHOD \n"
                "        0\n"
                "        0\n"
                f"        {self._TYPE_MAPPING[DM.ParamType.UINT16][1]}\n"
                f"        {self._TYPE_MAPPING[DM.ParamType.UINT16][2]}\n"
                "    /end TYPEDEF_MEASUREMENT\n"
                "\n"
                "    /begin TYPEDEF_MEASUREMENT\n"
                f"        T_{block.name}_ULONG\n"
                "        \"block 32 bit parameter type\"\n"
                f"        {self._TYPE_MAPPING[DM.ParamType.UINT32][0]}\n"
                "        NO_COMPU_METHOD \n"
                "        0\n"
                "        0\n"
                f"        {self._TYPE_MAPPING[DM.ParamType.UINT32][1]}\n"
                f"        {self._TYPE_MAPPING[DM.ParamType.UINT32][2]}\n"
                "    /end TYPEDEF_MEASUREMENT\n"
                "\n"
                "    /begin TYPEDEF_STRUCTURE\n"
                f"        {block.name}_header_type_t\n"
                "        \"Block header structure\"\n"
                "        16\n"
                "        /begin STRUCTURE_COMPONENT\n"
                f"            id T_{block.name}_USHORT\n"
                "            0\n"
                "        /end STRUCTURE_COMPONENT\n"
                "        /begin STRUCTURE_COMPONENT\n"
                f"            major T_{block.name}_USHORT\n"
                "            2\n"
                "        /end STRUCTURE_COMPONENT\n"
                "        /begin STRUCTURE_COMPONENT\n"
                f"            minor T_{block.name}_USHORT\n"
                "            4\n"
                "        /end STRUCTURE_COMPONENT\n"
                "        /begin STRUCTURE_COMPONENT\n"
                f"            dataver T_{block.name}_USHORT\n"
                "            6\n"
                "        /end STRUCTURE_COMPONENT\n"
                "        /begin STRUCTURE_COMPONENT\n"
                f"           reserved T_{block.name}_ULONG\n"
                "            8\n"
                "        /end STRUCTURE_COMPONENT\n"
                "        /begin STRUCTURE_COMPONENT\n"
                f"           length T_{block.name}_ULONG\n"
                "            12\n"
                "        /end STRUCTURE_COMPONENT\n"
                "    /end TYPEDEF_STRUCTURE\n"
                "    /begin INSTANCE\n"
                f"        {block.name}_blkhdr\n"
                "        \"block header instance\"\n"
                f"        {block.name}_header_type_t\n"
                f"        {hex(block.addr)}\n"
                "    /end INSTANCE\n"
            )


    def begin_parameter(self, param: DM.Parameter) -> None:
        """Write parameter as measurement"""

        self.a2l_file.write(f"\n    /begin MEASUREMENT {param.name}\n")

        self.a2l_file.write("        \"")
        if param.comment is not None:
            self.a2l_file.write(param.comment.splitlines()[0])
        else:
            self.a2l_file.write("No comment defined")
        self.a2l_file.write("\"\n")

        self.a2l_file.write(
            f"        {self._TYPE_MAPPING[param.ptype][0]}\n"
            "        NO_COMPU_METHOD \n"
            "        0\n"
            "        0\n"
            f"        {self._TYPE_MAPPING[param.ptype][1]}\n"
            f"        {self._TYPE_MAPPING[param.ptype][2]}\n"
            f"        BYTE_ORDER {self._BYTEORDER_MAPPING[self.ctx_block.endianess]}\n"
        )

        # check for array
        element_size = ByteConvert.get_type_size(param.ptype)
        if (DM.ParamType.UTF8 == param.ptype) or (element_size < len(param.value)):
            self.a2l_file.write(f"        MATRIX_DIM {int(len(param.value) / element_size)}\n")

        self.a2l_file.write(
            f"        ECU_ADDRESS {hex(param.offset)}\n"
            "        ECU_ADDRESS_EXTENSION 0x0\n"
            f"        DISPLAY_IDENTIFIER {param.name}\n"
            "        READ_WRITE\n"
        )

        self.a2l_file.write("    /end MEASUREMENT\n")

    def post_run(self):
        """Close output file"""

        self.a2l_file.write("\n/end PROJECT\n")
        self.a2l_file.close()
