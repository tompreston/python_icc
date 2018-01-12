"""
parse_icc.py - Parse ICC profiles
Copyright (C) 2017 Codethink Ltd.
Author: Thomas Preston <thomas.preston@codethink.co.uk>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
from collections import namedtuple
import argparse
import struct

# VCGT tags http://www.color.org/groups/medical/displays/controllingVCGT.pdf
TAG_SIGS = {
    "desc": "descriptionTag",
    "cprt": "copyrightTag",
    "dmnd": "deviceMfgDescTag",
    "dmdd": "deviceModelDescTag",
    "vcgt": "videoCardGammaTableTag",
    "rXYZ": "redPrimaryXYZData",
    "gXYZ": "greenPrimaryXYZData",
    "bXYZ": "bluePrimaryXYZData",
    "rTRC": "redTRCTag",
    "gTRC": "greenTRCTag",
    "bTRC": "blueTRCTag",
    "wtpt": "mediaWhitePointTag",
}

ICCHeader = namedtuple("ICCHeader",
                       ["size", "pref_cmm_type", "version", "profile_class",
                        "colour_space", "pcs", "created_at", "acsp",
                        "primary_plat_sig", "flags", "dev_manufacturer",
                        "dev_model", "dev_attributes", "rendering_intent",
                        "nCIEXYZ", "creator_sig", "id", "spectral_pcs",
                        "spectral_pcs_wl", "bispectral_pcs_wl", "mcs_sig",
                        "subclass", "reserved"])
ICCTag = namedtuple("ICCTag", ["signature", "offset", "size"])

class ICCProfile():
    """An ICC Profile according to ICC Specification
    ICC.1:2001-12 http://www.color.org/newiccspec.pdf
    ICC.2-2017    http://www.color.org/iccmax/ICC.2-2017.pdf
    Note: There are different tags in different specs
    """
    def __init__(self, filename=None):
        if filename:
            self.unpack(filename)

    def unpack(self, filename):
        """Unpack an ICC profile."""
        with open(filename, "rb") as iccf:
            header_data = struct.unpack(">2I4s3I12s5IQI12sI16sI6s6s3I",
                                        iccf.read(128))
            self.header = ICCHeader(*header_data)
            self.num_tags = struct.unpack(">I", iccf.read(4))[0]
            self.tags = [ICCTag(*struct.unpack(">4sII", iccf.read(12)))
                         for i in range(self.num_tags)]
            self.tag_elements = [iccf.read(tag.size) for tag in self.tags]

    def print(self):
        """Print an ICC profile in a human readable format."""
        print("size: {}B".format(self.header.size))
        print("version: {}".format(self.get_version_str()))
        print("num tags: {}".format(self.num_tags))
        for i, tag in enumerate(self.tags):
            print(i, tag)
        for i, tag_element in enumerate(self.tag_elements):
            print(i, tag_element)

    def get_version_str(self):
        """Return the version string from the ICC profile header."""
        verfmt = "{major}.{minor}.{bugfix} sub {smajor}.{sminor}"
        return verfmt.format(major=self.header.version[0],
                             minor=self.header.version[1] >> 4,
                             bugfix=self.header.version[1] & 0xf,
                             smajor=self.header.version[2],
                             sminor=self.header.version[3])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("icc_file", help="ICC profile", metavar="FILE")
    args = parser.parse_args()

    icc = ICCProfile(args.icc_file)
    icc.print()
