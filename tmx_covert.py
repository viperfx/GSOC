from lxml import etree
from StringIO import StringIO


def tmx_convert():
    tmx_file = open('./memoire_en-US_en-GB.tmx', 'r')
    tmx_tree = etree.parse(tmx_file)
    print tmx_tree


def validate_tbx(path):
    tbx_file = open(path, 'r')
    tbx_tree = etree.parse(tbx_file)
    tbx_rng = etree.RelaxNG(file='./TBX-resources/TBX_RNGV02.rng')
    # validates True with RelaxNG.
    print "File %s - Validated against RelaxNG scheme: %s" % (path, tbx_rng.validate(tbx_tree))


if __name__ == '__main__':
    validate_tbx('./memoire_en-US_en-GB_1.tbx')
    # tmx_convert()

# What fields are important?
# Merge all languages into into TBX?
# How are the fields uniquely identified?
