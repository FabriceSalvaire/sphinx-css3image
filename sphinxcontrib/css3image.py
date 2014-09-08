# -*- coding: utf-8 -*-

""" This plugin provides an enhanced ``image`` directive with additional CSS properties for Sphinx
Documentation Generator.

The code is mainly a copy of the one for the original ``image`` directive, since there is no other
way to do.
"""

####################################################################################################

import os
import posixpath
import re
import sys
import urllib

from docutils import nodes
from docutils.nodes import fully_normalize_name, whitespace_normalize_name
from docutils.parsers.rst import directives, states
from docutils.parsers.rst.roles import set_classes
from sphinx.util.compat import Directive

####################################################################################################

try:
    import PIL # check for the Python Imaging Library
except ImportError:
    PIL = None

####################################################################################################

class Css3Image(nodes.image):
    """
    cf. ```/usr/lib/python2.7/site-packages/docutils/nodes.py``
    """

####################################################################################################

# Fixme: design a better option validation API

def degree(argument):
    """ Check for a degree argument and return a normalized string of the form "<value>deg" (without
    space in between).

    To be called from directive option conversion functions.

    cf. ``/usr/lib/python2.7/site-packages/docutils/parsers/rst/directives/__init__.py``
    """
    match = re.match(r'^(-?)([0-9.]+) *(|deg)$', argument)
    try:
        assert match is not None
        float(match.group(2))
    except (AssertionError, ValueError):
        raise ValueError('Value must be in degree')
    return match.group(1) + match.group(2) + match.group(3)

####################################################################################################

def one_length(argument):
    return directives.get_measure(argument, directives.length_units)

####################################################################################################

def list_of_lengths(argument, length_max, separator=' '):
    if ',' in argument:
        entries = argument.split(',')
    else:
        entries = argument.split()
    entries = [one_length(x) for x in entries]
    if len(entries) > length_max:
        raise ValueError("Value must be a list of one to {} length"
                         " separated by spaces or commas".format(length_max))
    return separator.join(entries)

####################################################################################################

def two_lengths(argument):
    return list_of_lengths(argument, length_max=2)

def three_lengths(argument):
    return list_of_lengths(argument, length_max=3)

def four_lengths(argument):
    return list_of_lengths(argument, length_max=4)

def two_lengths_comma(argument):
    return list_of_lengths(argument, length_max=2, separator=',')

def three_lengths_comma(argument):
    return list_of_lengths(argument, length_max=3, separator=',')

def four_lengths_comma(argument):
    return list_of_lengths(argument, length_max=4, separator=',')

####################################################################################################

class Css3ImageDirective(Directive):

    """ This class defines a ``css3image`` directive.

    Should be derived from Image.

    cf. ``/usr/lib/python2.7/site-packages/docutils/parsers/rst/directives/images.py``
    """

    align_h_values = ('left', 'center', 'right')
    align_v_values = ('top', 'middle', 'bottom')
    align_values = align_v_values + align_h_values

    ##############################################

    def align(argument):
        # This is not callable as self.align.  We cannot make it a staticmethod because we're saving
        # an unbound method in option_spec below.
        return directives.choice(argument, Css3ImageDirective.align_values)

    ##############################################

    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {'alt': directives.unchanged,
                   'height': directives.length_or_unitless,
                   'width': directives.length_or_percentage_or_unitless,
                   'scale': directives.percentage,
                   'align': align,
                   'name': directives.unchanged,
                   'target': directives.unchanged_required,
                   'class': directives.class_option,
                   # css3image: Added some options
                   'margin': four_lengths,
                   'margin-left': one_length,
                   'margin-right': one_length,
                   'margin-bottom': one_length,
                   'margin-top': one_length,
                   'border-radius': one_length,
                   'transform-origin': three_lengths,
                   'translate': two_lengths_comma,
                   'translatex': one_length, # options are converted to lower case!
                   'translatey': one_length,
                   # 'scale': directives.unchanged,
                   'scalex': directives.unchanged, # float 1.0 and not 1.
                   'scaley': directives.unchanged,
                   'rotate': degree,
                   # matrix(n,n,n,n,n,n)
                   # skew(x-angle,y-angle)
                   }

    ##############################################

    def run(self):

        if 'align' in self.options:
            if isinstance(self.state, states.SubstitutionDef):
                # Check for align_v_values.
                if self.options['align'] not in self.align_v_values:
                    raise self.error(
                        'Error in "%s" directive: "%s" is not a valid value '
                        'for the "align" option within a substitution '
                        'definition.  Valid values for "align" are: "%s".'
                        % (self.name, self.options['align'], '", "'.join(self.align_v_values)))
            elif self.options['align'] not in self.align_h_values:
                raise self.error(
                    'Error in "%s" directive: "%s" is not a valid value for '
                    'the "align" option.  Valid values for "align" are: "%s".'
                    % (self.name, self.options['align'], '", "'.join(self.align_h_values)))

        messages = []
        reference = directives.uri(self.arguments[0])
        self.options['uri'] = reference
        reference_node = None

        if 'target' in self.options:
            block = states.escape2null(self.options['target']).splitlines()
            block = [line for line in block]
            target_type, data = self.state.parse_target(block, self.block_text, self.lineno)
            if target_type == 'refuri':
                reference_node = nodes.reference(refuri=data)
            elif target_type == 'refname':
                reference_node = nodes.reference(refname=fully_normalize_name(data),
                                                 name=whitespace_normalize_name(data))
                reference_node.indirect_reference_name = data
                self.state.document.note_refname(reference_node)
            else: # malformed target
                messages.append(data) # data is a system message
            del self.options['target']

        set_classes(self.options)
        # css3image: customise Class
        image_node = Css3Image(self.block_text, **self.options)
        self.add_name(image_node)

        if reference_node:
            reference_node += image_node
            return messages + [reference_node]
        else:
            return messages + [image_node]

####################################################################################################

def format_css_property(name, value):
    return '{}: {};'.format(name, value)

####################################################################################################

def css3_prefix(style_property):
    return ' '.join([prefix + style_property for prefix in ('', '-ms-', '-moz-', '-webkit-')])

####################################################################################################

def visit_Css3Image_html(self, node):

    """

    cf. ``/usr/lib/python2.7/site-packages/sphinx/writers/html.py``
    """

    # print 'css3image.visit_Css3Image_html'

    olduri = node['uri']
    # rewrite the URI if the environment knows about it
    if olduri in self.builder.images:
        node['uri'] = posixpath.join(self.builder.imgpath, self.builder.images[olduri])

    uri = node['uri']
    ext = os.path.splitext(uri)[1].lower()
    if ext in ('.svg', '.svgz'):
        atts = {'src': uri}
        if 'width' in node:
            atts['width'] = node['width']
        if 'height' in node:
            atts['height'] = node['height']
        if 'alt' in node:
            atts['alt'] = node['alt']
        if 'align' in node:
            self.body.append('<div align="%s" class="align-%s">' % (node['align'], node['align']))
            self.context.append('</div>\n')
        else:
            self.context.append('')
        self.body.append(self.emptytag(node, 'img', '', **atts))
        return

    if 'scale' in node:
        # Try to figure out image height and width.  Docutils does that too,
        # but it tries the final file name, which does not necessarily exist
        # yet at the time the HTML file is written.
        if PIL and not (node.has_key('width') and node.has_key('height')):
            try:
                image = PIL.Image.open(os.path.join(self.builder.srcdir, olduri))
            except (IOError, # Source image can't be found or opened
                    UnicodeError): # PIL doesn't like Unicode paths.
                pass
            else:
                if 'width' not in node:
                    node['width'] = str(image.size[0])
                if 'height' not in node:
                    node['height'] = str(image.size[1])
                del image

    # from docutils.writers.html4css1 import HTMLTranslator as BaseTranslator
    # BaseTranslator.visit_image(self, node)

    atts = {}
    uri = node['uri']
    # place SVG and SWF images in an <object> element
    types = {'.svg': 'image/svg+xml',
             '.swf': 'application/x-shockwave-flash'}
    ext = os.path.splitext(uri)[1].lower()
    if ext in ('.svg', '.swf'):
        atts['data'] = uri
        atts['type'] = types[ext]
    else:
        atts['src'] = uri
        atts['alt'] = node.get('alt', uri)

    # image size
    if 'width' in node:
        atts['width'] = node['width']
    if 'height' in node:
        atts['height'] = node['height']
    if 'scale' in node:
        if (PIL and not ('width' in node and 'height' in node)
            and self.settings.file_insertion_enabled):
            imagepath = urllib.url2pathname(uri)
            try:
                img = PIL.Image.open(imagepath.encode(sys.getfilesystemencoding()))
            except (IOError, UnicodeEncodeError):
                pass # TODO: warn?
            else:
                self.settings.record_dependencies.add(imagepath.replace('\\', '/'))
                if 'width' not in atts:
                    atts['width'] = str(img.size[0])
                if 'height' not in atts:
                    atts['height'] = str(img.size[1])
                del img
        for att_name in 'width', 'height':
            if att_name in atts:
                match = re.match(r'([0-9.]+)(\S*)$', atts[att_name])
                assert match
                atts[att_name] = '%s%s' % (float(match.group(1)) * (float(node['scale']) / 100),
                                           match.group(2))

    style = []
    for att_name in 'width', 'height':
        if att_name in atts:
            value = atts[att_name]
            if re.match(r'^[0-9.]+$', value):
                # Interpret unitless values as pixels.
                value += 'px'
            style.append('%s: %s;' % (att_name, value))
            del atts[att_name]

    # css3image: Added some styles
    for property_name in ('margin-left', 'margin-right', 'margin.bottom', 'margin-top',
                          'margin',
                          'border-radius',
                          ):
        if property_name in node:
            style.append(format_css_property(property_name, node[property_name]))
    for property_name in ('transform-origin',):
        if property_name in node:
            style.append(css3_prefix(format_css_property(property_name, node[property_name])))
    transform = []
    for property_name in ('translate', 'translatex', 'translatey',
                          'scalex', 'scaley', # 'scale',
                          'rotate',
                          ):
        if property_name in node:
            value = node[property_name]
            for axe in 'x', 'y':
                if property_name.endswith(axe):
                    property_name = property_name[:-1] + axe.upper()
            transform.append('{}({})'.format(property_name, value))
    if transform:
        style.append(css3_prefix('transform: ' + ' '.join(transform) + ';'))

    if style:
        atts['style'] = ' '.join(style)
    if (isinstance(node.parent, nodes.TextElement) or
        (isinstance(node.parent, nodes.reference) and
         not isinstance(node.parent.parent, nodes.TextElement))):
        # Inline context or surrounded by <a>...</a>.
        suffix = ''
    else:
        suffix = '\n'
    if 'align' in node:
        atts['class'] = 'align-%s' % node['align']
    self.context.append('')
    if ext in ('.svg', '.swf'): # place in an object element,
        # do NOT use an empty tag: incorrect rendering in browsers
        self.body.append(self.starttag(node, 'object', suffix, **atts) +
                         node.get('alt', uri) + '</object>' + suffix)
    else:
        self.body.append(self.emptytag(node, 'img', suffix, **atts))

####################################################################################################

def depart_Css3Image_html(self, node):
    # print 'css3image.depart_Css3Image_html'
    self.body.append(self.context.pop())

####################################################################################################

def visit_Css3Image_text(self, node):
    # print 'css3image.visit_Css3Image_text'
    pass

####################################################################################################

def depart_Css3Image_text(self, node):
    # print 'css3image.depart_Css3Image_text'
    pass

####################################################################################################

def setup(app):

    # print 'Load css3image'
    
    app.add_node(Css3Image,
                 html=(visit_Css3Image_html, depart_Css3Image_html),
                 text=(visit_Css3Image_text, depart_Css3Image_text),
                 )

    app.add_directive('css3image', Css3ImageDirective)

####################################################################################################
# 
# End
# 
####################################################################################################
