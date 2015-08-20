pywe
#!/usr/bin/python
#
# Python-bases PmWiki Editor (Pywe)
# =================================
#
# Copyright and Legalese
# ----------------------
#
# Copyright (c) 2006 Benjamin C. Wilson. All Rights Reserved.  
#
# This software referred to as Pywe ("Software") was developed by Benjamin C.
# Wilson, and may include voluntary contributions. For more information on this
# Software, visit its web site at http://www.dausha.net/Pywe.
#
# Installation, use, reproduction, and display of this Software, without
# modification, are not permitted.  You may not republish without The express,
# written concent of the copyright holder.  Permission to publish is granted to
# pmwiki.org, but no permission to modify is granted. Any exercise of rights
# under this license by you is subject to the following conditions.
#    1. If you remix, transform, or build upon the material, you may not 
#       distribute the modified material.
#    2. Any user documentation must include the copyright statement.
#    3. This copyright statement, disclaimers and limitations must remain with 
#       the software.
#    4. Consent to the following disclaimer and limitations of liability.
#
# Disclaimer
# ~~~~~~~~~~
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY, OF SATISFACTORY QUALITY, AND FITNESS
# FOR A PARTICULAR PURPOSE OR USE ARE DISCLAIMED. THE COPYRIGHT HOLDER AND
# CONTRIBUTORS MAKE NO REPRESENTATION THAT THE SOFTWARE, MODIFICATIONS,
# ENHANCEMENTS OR DERIVATIVE WORKS THEREOF, WILL NOT INFRINGE ANY PATENT,
# COPYRIGHT, TRADEMARK, TRADE SECRET OR OTHER PROPRIETARY RIGHT. 
# 
# Limitations of Liability
# ~~~~~~~~~~~~~~~~~~~~~~~~
#
# THE COPYRIGHT HOLDER AND CONTRIBUTORS SHALL HAVE NO LIABILITY TO LICENSEE OR
# OTHER PERSONS FOR DIRECT, INDIRECT, SPECIAL, INCIDENTAL, CONSEQUENTIAL,
# EXEMPLARY, OR PUNITIVE DAMAGES OF ANY CHARACTER INCLUDING, WITHOUT
# LIMITATION, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES, LOSS OF USE, DATA OR
# PROFITS, OR BUSINESS INTERRUPTION, HOWEVER CAUSED AND ON ANY THEORY OF
# CONTRACT, WARRANTY, TORT (INCLUDING NEGLIGENCE), PRODUCT LIABILITY OR
# OTHERWISE, ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGES. 
# 
# License Revisions
# ~~~~~~~~~~~~~~~~~
#
# The Software Copyright Holder may publish revised and/or new versions of this
# this License from time to time. Each version will be given a distinguishing
# version number. Once a version of Software has been published under a
# particular version of this License, you may continue to use it under the
# terms of that license version. You may also choose to use such Software under
# the terms of any subsequent version of this License published by the
# Copyright Holder. No one other than the Copyright Holder has the right to
# modify the terms of this License.
#
# If you have any questions, comments or concerns, please contact the author at
# <ameen@dausha.net>
#
# Follow the GitHub Repository: https://github.com/Merovex/pywe
#
# License Version: v1.0 - May 20, 2006.
#
# Software version: v1.0 - Public Release May 20, 2006
# Software version: v1.1 - Public Release May 30, 2006
# Software version: v1.2 - Public Release June 2, 2006
# Software version: v1.3 - Public Release February 7, 2007
# Software version: v1.3.1 - Public Release February 9, 2007
# Software version: v1.3.2 - Public Release August 20, 2015
__version__ = "v1.3.2 - August 20, 2015"

import ConfigParser
import optparse
import getpass
import logging
import os
import re
import string
import signal
import sys
import tempfile
import time
import urllib
import urlparse

#===================================
# Various Custom Exception Classes.
class NeedsAuthenticationError(Exception): 
    def __init__(self, url=''):
        say_error("Wiki said authentication needed." + url)

class NoEditorError(Exception):
    def __init__(self, msg):
        say_error(msg)

class NoSourceFileError(Exception):
    def __init__(self):
        say_error("No local source file to read from.")

class TempWriteError(Exception):
    def __init__(self):
        say_error("Could not write to the temporary file")

#===================================
# PmWiki Configuration Class
#-----------------------------------
class PmwikiConfig:
    def __init__(self, dom='DEFAULT', url=None):

        if dom is None: dom = 'DEFAULT'
        dom = dom.upper()

        setattr(self,'_config',ConfigParser.ConfigParser())
        setattr(self,'dom', dom) 
        setattr(self,'file', os.path.expanduser('~/.pywerc'))

        c = self._config
        c.read(self.file)

        config_keys = [
            'author',
            'browser',
            'editor',
            'enablepathinfo',
            'keep',
            'page',
            'password',
            'url',
        ]
        defaults = c.defaults()
        for option in config_keys:
            val = ''
            if c.has_section(dom) and c.has_option(dom, option):
                val = c.get(dom,option)
            elif defaults.has_key(option):
                val = defaults[option]
            else: val = 0

            if val == 'yes': val = 1
            elif val == 'no' : val = 0
            setattr(self,option,val)

        if url is not None: self.url = url
# class PmwikiClass


#===================================
# PmWiki Page Class
#-----------------------------------
class PmwikiPage :
    def __init__(self, url, page, epi):
        setattr(self, 'enablepathinfo', epi)
        setattr(self, 'page', page)
        setattr(self, 'passwd', None)
        setattr(self, 'text', None)
        setattr(self, 'url', url)

    def _fmtPage(self, action):
        page = self.page
        url = self.url
        if self.enablepathinfo:
            if url[-1] != '/': url += '/'
            return urlparse.urljoin(url, page) + '?action=' + action
        else:
            url = re.sub('/$','',url)
            page = re.sub('/','.', page)
            return '%s?n=%s&action=%s' % (url, page, action)

    def readpage(self, author='', passwd=None):
        """Retrieves the PmWiki source from the web site"""
        source = self._fmtPage('source')
        params = urllib.urlencode({'authid' : author, 'authpw' : passwd})
        try:                                
            fh  = urllib.urlopen(source, params)
            content = fh.read()
            if content[4:11] == 'DOCTYPE':
                raise NeedsAuthenticationError(self.url)
            else: 
                return content

        except IOError:
            say_error("Could not access: " + self.url)

    def writepage(self, text, src, author='', passwd=None):
        """Writes the page back to the web site"""
        page = self.page
        url = self.url
        if  src == text :
            say_info("Original and revision are the same. Not uploading.")
        else :
            if text != 'delete': 
                text = self.editMark(text)
            url = self._fmtPage('edit')
            opts = {'action' : 'edit', 'authid' : author, 'author' : author,
             'authpw' : passwd, 'n' : page, 'post' : 1, 'text' : text
            }
            if passwd is None:
                del(opts['authid'])
                del(opts['authpw'])

            params = urllib.urlencode(opts)
            try:                                
                fh  = urllib.urlopen(url, params)
            except IOError, e:
                self.savepage(text)
                msg = "Failed Write to web site, check for '%s' (%s)" % (fn, e)
                say_error(msg)

    def savepage(self, t):
        fn = '%s-%d' %(self.page, time.time())
        fn = fn.replace('/','.')
        f = open(fn,'w+')
        f.write(t)
        f.close()
        return fn

    def editpage(self, editor, text=None):
        """Sends page to your favorite editor"""
        if text is None: text = self.readpage()
        if len(text) == 0: 
            say_info("%s is a new page. So the contents are blank." % self.page)
            time.sleep(5)

        f = tempfile.NamedTemporaryFile(
                'r+w', -1, '.pmwiki', 'pywe-', tempfile.tempdir
            )
        say_info("Using Tempfile: " + f.name)
        try:                                
            f.write(text)
            f.flush()
            f.seek(0)
        except IOError:
            raise TempWriteError

        cmd = editor + ' ' + f.name
        os.system(cmd)
        output = f.read()
        f.close()
        return output

    def editMark(self, t) :
        m = "\n(:comment This page has been edited using Pywe:)"
        m_RE = re.compile("\n+\(:comment This page has been edited using Pywe:\)")
        t = m_RE.sub('', t)
        t += m
        return t

# class PmWikiPage

def findApp(f,m="Could not find application: "):
    """If we don't have the application at first, we go looking."""
    if os.path.isfile(f): return f
    dirs = sys.path
    dirs.insert(0,os.environ['HOME'])
    for d in dirs:
      c = os.path.join(d, f)
      if os.path.isfile(c): return c
    raise NoEditorError(m+f)

def say_info(msg):
    sys.stderr.write(msg+"\n")
    logging.info(msg)

def say_error(msg):
    """Prints errors to stderr, logs the error and quits."""
    sys.stderr.write(msg)
    logging.error(msg)
    sys.exit(0)

def shorthelp(option, opt_str, value, p):
    """Prints terse help message in technicolor"""
    esc_seq = "\x1b["
    codes = {}
    codes["reset"] = esc_seq + "39;49;00m"
    codes["bold"] = esc_seq + "01m"
    codes["green"] = esc_seq + "32;01m"
    codes["turq"] = esc_seq + "36;01m"
    def green(txt): return "%s%s%s" % (codes["green"],txt,codes["reset"])
    def bold(txt): return "%s%s%s" % (codes["bold"],txt,codes["reset"])
    def turq(txt): return "%s%s%s" % (codes["turq"],txt,codes["reset"])

    opt = {}
    def getem(d,k):
        ret = ''
        try:
            if d.has_key(k) and d[k] is not None: 
                if isinstance(d[k], list) and len(d[k]): ret = d[k][0]
                elif not len(d[k]): ret = ''
                else: ret = d[k]
        except:
            print d
        return ret

    def help_msg(d,k,m=1):
        s = getem(d[k],'short')
        l = getem(d[k],'long')
        dst = getem(d[k],'dest')
        h = getem(d[k],'help')
        d = dst.upper()
        if len(dst) and len(l): dl = "="+dst.upper()
        else: dl = ''

        if len(s):
            if len(d): d = ' '+d
            out = "%s%s, %s%s" % (s,d,l,dl)
            pad = 36
            clor = "  %s%s, %s%s" % (green(s),turq(d), green(l),turq(dl))
        else:
            out = "  %s%s" % (l,dl)
            pad = 38
            clor = "  %s%s" % (green(l),turq(dl))
        return clor + (' '* (pad - len(out))) + h

    for o in p.option_list:
        e = "%s" % o # Options convert to strings when asked.
        e = e.split('/')[0]
        e = e[e.rindex('-')+1:]
        opt[e] = { 
            'help': o.help, 
            'short': o._short_opts, 
            'long': o._long_opts, 
            'dest': o.dest, 
        }
        if not len(opt[e]['short']) : opt[e]['short'] = None

    prog = turq('pywe')
    opts = "[ %s ]" % green('options')
    acts = "[ %s ]" % green('action')

    print bold("\nUsage:")
    print '  '+' '.join([prog, opts, acts, turq('dom:Group.Pagename' )])
    print '  '+' '.join(
      [prog, opts, acts, turq('http://www.example.org/pmwiki.php/Main/Sandbox')]
    )
    print '  '+' '.join([prog, turq('--help')])
    print bold("Options:")

    #-----------------------------------
    # The DRY principle in motion. All the work above allows adding an option
    # to Optparse that will dynamically print a short message about itself when
    # asked.
    keys = opt.keys()
    keys.sort()
    for k in keys: print help_msg(opt,k)

    print
    sys.exit(0)

def checkApp(o, a, m):
    if not o: return 0
    msg = {
      'noeditor': "You must configure an editor to edit a page.",
      'nobrowser': "You must configure a browser to us this option."
    }
    check = a.split(' ',1)[0]
    
    a = findApp(check)
    if not os.path.isfile(check): say_error(msg[m])
    return True

#===================================
# Main:
#-----------------------------------
def main(argv=None):
    dom = 'DEFAULT'
    page = None
    url = None

    def siftUrl(s):
        """Tries to produce a valid web page when user munges things"""
        page = group = ''
        bits = urlparse.urlsplit(s)
        url = '://'.join([bits[0],bits[1]]) + '/' # http://www.example.org/
        query = bits[2].split('/')
        if '' in query: query.remove('')
        if len(query) > 1: page = query.pop()
        if len(query) > 0 and query[-1][0] == query[-1].capitalize()[0]:
            group = query.pop()
        if len(query): url += '/'.join(query) + '/'
        if page == '': page = 'Main'
        if group == '': group = 'Main'
        page = '.'.join([group,page])
        return url, page

    # TODO: Commented options are not available at time of publication. 
    #       Planned. v.1.3.0
    #-----------------------------------
    # Optparse allows me to easily set up the base options. Additionally, it
    # lets me add an option here and it will appear in the shorthelp display.
    p = optparse.OptionParser(
            conflict_handler="resolve",version="%prog "+__version__)
    p.add_option(
            '-a','--author',dest='author', 
            help="sets author's name from the command line")
    p.add_option(
            '-b',action='store_true',dest='browse',
            help='after edit, load the page in the configured browser.')
    p.add_option(
            '-c','--calendar',action='store_true',
            help="append today's date to page")
    p.add_option(
            '-d','--delete',action='store_true',dest='delete',
            help='Allows deletion of a page.')
    p.add_option(
            '-e','--editor',dest='editor', 
            help='sets editor (full path) from the command line.')
    p.add_option(
            '-i','--inject',dest='inject', 
            help='inject local source text file into wiki.')
    p.add_option(
            '-h','--help',action='callback', callback=shorthelp, 
            help='show this help message and exit.')
    p.add_option(
            '-j','--journal',action='store_true',
            help="append today's date to page")
    p.add_option(
            '-k','--keep',action='store_true',dest='keep',
            help='retain local copy of page source after edit.')
    p.add_option(
            '-n','--nopass',action='store_true',dest='nopass',
            help='site does not require a password.')
    p.add_option(
            '-p','--pull',action='store_true',dest='pull',
            help='pull source and save locally sans editing.')
    p.add_option(
            '-v','--verbose',type='int',dest='verbose')
    option, args = p.parse_args()
    # - Done Optparse: options are in "option" object.

    argv_e = {
        'mas' : "Too many arguments.",
    }

    if len(args):
        (dom, page) = args[0].split(':')
        if dom == 'http': url, page = siftUrl(args[0])

    c = PmwikiConfig(dom, url)
    if not page: page = c.page

    pm = PmwikiPage(c.url, page, c.enablepathinfo)

    #-----------------------------------
    # Editor checksum
    if (option.editor): c.editor = option.editor
    checkApp(True, c.editor, 'noeditor')

    if (option.keep): c.keep = option.keep

    #-----------------------------------
    # Get the password.
    if option.nopass or not c.password: password = None
    else: password = getpass.getpass()

    #-----------------------------------
    # Looking for an inject source. 
    if option.inject:
        if os.path.isfile(option.inject):
            say_info("Injecting: "+page+" ("+c.url+")")
            f = open(option.inject,'r')
            new = f.read()
            f.close()
            src = ''
        else:
            raise NoSourceFileError

    elif option.delete:
        delete = raw_input("Deleting: "+page+". Are you sure? (Type delete)\n")
        if delete == 'delete':
            src = ''
            new = 'delete'
        else:
            print "Deletion aborted."
            sys.exit(0)
    else:
        if option.journal: pm.page += time.strftime('-%Y-%m-%d')
        if option.calendar: pm.page += time.strftime('%Y%m%d')

        say_info("Editing: "+page+" ("+c.url+")")
        src = pm.readpage(c.author, password)
        if option.pull: 
            say_info("Pulling: "+page+" ("+c.url+")")
            print pm.savepage(src)
            sys.exit(0)
        else:
            new = pm.editpage(c.editor, src)

    if (option.keep or c.keep): 
        pm.savepage(new)

    pm.writepage(new, src, c.author, password)

    if checkApp(option.browse, c.browser, 'nobrowser'):
        cmd = "%s %s" % (c.browser, c.url)
        os.system(cmd)

if __name__ == '__main__':
    '''When we're running from the command line. Perhaps in the future a GUI
    will come?'''

    try:
        logging.basicConfig(
            level=logging.ERROR,
            format='%(asctime)s %(levelname)-8s %(message)s',
            datefmt='%a, %d %b %Y %H:%M:%S',
            filename = "/tmp/pywe.log",
            filemode='a+')
    except TypeError:
        logging.basicConfig()

    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        say_error('User terminated program via keyboard')
