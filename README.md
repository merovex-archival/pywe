Table of Contents
Background
Comments
Download
Usage
Issue Tracking
Release Notes

**Q: I would like to edit PmWiki pages using my favorite text editor.**

A: The Python-based PmWiki Editor is a program intended to serve as an intermediary between your editor and the PmWiki page you want to edit. It was originally written to support vim. However, it should work with any text editor.
If you use Emacs, please consider the Emacs PmWiki Mode as it was designed with Emacs in mind. Not that this recipe slights Emacs, but that recipe may provide a better solution for your Emacs-need.
In case you're wondering, as of October 2010; this script is still in use and working fine.

## Background

Scott Duff wrote a program called pmwikiedit, a Perl-based application that retrieves source from a Pmwiki site, allows the individual to edit the source using his favorite text editor, then repost the amended content back to the web server. I used that program greatly in the beginning, but when PmWiki v.2.0 came along, I found increasing difficulty with its use.
Recently, I wanted to edit pages using vim like I used to when pmwikiedit worked. I also was working on my Python skills. As I am prone to doing, when trying to master a new language, I wrote this program from scratch in Python. I also sought to introduce various features that I found interesting to have. Pywe is a Python-based wiki-editor that allows the user to edit PmWiki pages using his preferred text editor.

## Comments

The user-contributed commentary and notes regarding this recipe are found on the Pywe Discussion page.

### Related Recipes Used

Share other recipes that you use in combination with this recipe.
Alternative Recipes Used

Share a recipe you use instead of this one.
It's not a recipe, but I use "it's all text" as an extension to firefox to enable me to edit stuff in vim. (Go, Vim!)
Download

* Attach:pywe-1.3.1.txtΔ This is the main application. Note: Because the PmWiki site does not support the Python extension, you will need to rename the file to pywe-1.3.1.py.
* Attach:sample-pywerc Δ This is a sample configuration file for Pywe.
* Attach:syntax-pmwiki.txtΔ This is a vim syntax file for PmWiki. Because the PmWiki site does not support the vim extension, you will need to rename this file to pmwiki.vim

## Usage

pywe [ options ] domain:Group.Pagename
pywe [ options ] http://www.example.org/pmwiki.php/Main/Sandbox
pywe --help: Will print this usage statement on the command line.
In the first example, the "domain" refers to the section of the .pywerc file that contains the wiki-specific configuration. This approach allows the editor to preset values to spare typing on the command line.

## Options

<dl>
<dt>-a AUTHOR, --author=AUTHOR</dt>
<dd>sets author's name from the command line</dd>
<dt>-b BROWSE,</dt>
<dd>after edit, load the page in the configured browser.</dd>
<dt>-c, --calendar</dt>
<dd>appends date format YMD to pages for use with Pm Calendar.</dd>
<dt>-d, --delete</dt>
<dd>initates page delete dialog.</dd>
<dt>-e EDITOR, --editor=EDITOR</dt>
<dd>sets editor (full path) from the command line.</dd>
<dt>-h, --help</dt>
<dd>show this help message and exit.</dd>
<dt>-i FILE, --inject=FILE</dt>
<dd>inject local source into wiki.</dd>
<dt>-j, --journal</dt>
<dd>append today's date to page</dd>
<dt>-k, --keep</dt>
<dd>keep local copy of page source after edit.</dd>
<dt>-n, --nopass</dt>
<dd>site does not require a password.</dd>
<dt>-p, --pull</dt>
<dd>pull source and save locally sans editing.</dd>
<dt>-u URL, --url=URL</dt>
<dd>read the PmWiki source from URI for editing.</dd>
<dt>-v VERBOSE, --verbose=VERBOSE</dt>
<dd>Not yet implemented right.</dd>
<dt>--version</dt>
<dd>show program's version number and exit.</dd>
</dl>

**Local File Interface.** Pywe has three primary ways of using local files. First, the inject option submits a local text file to the PmWiki page. Second, the keep option keeps a local copy of the wiki page after it is edited by the author. That is, the remote copy is fed into the editor, and the copy submitted to the wiki site is kept as a local copy. Finally, the pull option simply pulls the remote copy and saves as a local copy. This can be used in conjunction with inject to allow the author to pull down a copy, edit and repost (although interviening changes would be overwritten). Beyond these three methods, a failed upload should archive the edited copy (similar to keep) locally to allow the author to inject the page when the network interference has passed.

**Deleting Pages.** Pywe will allow deleting of pages. When invoked, the delete option will ask the user to confirm deletion by typing the word 'delete,' which is meant to put a person in the process and avoid automated deletions.

**Dating Pages.** Pywe has two options for dating pages. This is meant to help those who either journal or update a Pm Calendar using this application. The date format for the calendar is "YMD" and the format for journalling is "Y-M-D."

## Pywerc File

The Pywerc file is an RFC 822 compliant "*.ini" file formatted configuration file. This allows the user to configure options via a configuration file such that a different set of configurations exists per domain. This is represented by the pywe [ options ] domain:Group.Pagename style of usage. The "domain" is the section delimiter in the .pywerc file. For more specific information on how it is used, please consult the Attach:sample-pywerc Δ file.
Pywerc Configuration Variables. To reduce typing, the .pywerc file stores the following values on a per domain basis.
author
The user name who is editing the page.
browser
The full path to your preferred browser, with options.
editor
The full path to your preferred editor, with options.
enablepathinfo
Whether to submit the page in Enable Path Info format or not. Refer to the PmWiki features for more information on this format.
keep
Whether the author would always like an edited page "kept."
page
A default pagename.
password
Whether a password is required to edit the page.
url
The URL is the full-URL path to the wiki you are trying to edit.
Issue Tracking

Are you aware of a problem with Pmwe? This recipe is actively maintained on a the Python-based PmWiki Editor web page. There I maintain a development journal, a repository for defects and features and a more complete release history.

## Release Notes

* v.1.3.1 February 9, 2007 BenWilson February 09, 2007, at 09:56 AM
** Added some authentication testing.
** Classed error handling.
* v.1.3.0 February 7, 2007 BenWilson February 08, 2007, at 09:50 AM
** Fixed problem with being unable to delete pages via Pywe.
** Fixed problem with accidently creating a new page when mistyping the pagename.
** Added support for the common PmWiki calendar date format.
* v.1.2.0 June 2, 2006 Implemented Injection feature. BenWilson June 02, 2006, at 11:02 PM
* v.1.1.1 May 30, 2006 Fixed broken journal option. BenWilson May 30, 2006, at 05:40 PM
* v.1.1.0 May 29, 2006 Initial Public Release. BenWilson May 29, 2006, at 12:12 PM