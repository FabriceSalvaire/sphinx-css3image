# -*- coding: utf-8 -*-

""" Enhanced ``image`` directive for Sphinx Documentation Generator. """

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

def degree(argument):
    match = re.match(r'^(-?)([0-9.]+) *(|deg)$', argument)
    try:
        assert match is not None
        float(match.group(2))
    except (AssertionError, ValueError):
        raise ValueError('Value must be in degree')
    return match.group(1) + match.group(2) + match.group(3)

####################################################################################################

class Css3ImageDirective(Directive):

    """ This class defines a ``css3image`` directive.

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
                   'rotate': degree,
                   'translationX': directives.length_or_unitless,
                   'translationY': directives.length_or_unitless,
                   'margin-left': directives.length_or_unitless,
                   'margin-right': directives.length_or_unitless,
                   'margin-bottom': directives.length_or_unitless,
                   'margin-top': directives.length_or_unitless,
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
        image_node = Css3Image(self.block_text, **self.options)
        # image_node = nodes.image(self.block_text, **self.options)
        self.add_name(image_node)

        if reference_node:
            reference_node += image_node
            return messages + [reference_node]
        else:
            return messages + [image_node]

####################################################################################################

def visit_Css3Image_html(self, node):

    """

    cf. ``/usr/lib/python2.7/site-packages/sphinx/writers/html.py``
    """

    print 'css3image.visit_Css3Image_html'

    olduri = node['uri']
    # rewrite the URI if the environment knows about it
    if olduri in self.builder.images:
        node['uri'] = posixpath.join(self.builder.imgpath, self.builder.images[olduri])
    print self.builder.imgpath, node['uri']

    if (node['uri'].lower().endswith('svg') or
        node['uri'].lower().endswith('svgz')):
        atts = {'src': node['uri']}
        if node.has_key('width'):
            atts['width'] = node['width']
        if node.has_key('height'):
            atts['height'] = node['height']
        if node.has_key('alt'):
            atts['alt'] = node['alt']
        if node.has_key('align'):
            self.body.append('<div align="%s" class="align-%s">' % (node['align'], node['align']))
            self.context.append('</div>\n')
        else:
            self.context.append('')
        self.body.append(self.emptytag(node, 'img', '', **atts))
        return

    if node.has_key('scale'):
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
                if not node.has_key('width'):
                    node['width'] = str(image.size[0])
                if not node.has_key('height'):
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
            if re.match(r'^[0-9.]+$', atts[att_name]):
                # Interpret unitless values as pixels.
                atts[att_name] += 'px'
            style.append('%s: %s;' % (att_name, atts[att_name]))
            del atts[att_name]
    transform = []
    for att_name in 'rotate', 'translationX', 'translationY':
        if att_name in node:
            transform.append('{}({})'.format(att_name, node[att_name]))
    if transform:
        style.append('transform: ' + ' '.join(transform) + ';')
    for att_name in ('margin-left', 'margin-right', 'margin.bottom', 'margin-top'):
        if att_name in node:
            value = node[att_name]
            if re.match(r'^[0-9.]+$', value):
                # Interpret unitless values as pixels.
                value += 'px'
            style.append('%s: %s;' % (att_name, value))
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
    print 'css3image.depart_Css3Image_html'
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

    print 'Load css3image'
    
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
