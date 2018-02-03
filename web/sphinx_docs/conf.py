#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# sphinx_backend documentation build configuration file, created by
# sphinx-quickstart on Mon Jul 24 09:27:23 2017.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# @TODO Issue pertaining to http not in app.domains fixed here:
# https://github.com/sphinx-doc/sphinx/issues/3760
# https://bitbucket.org/birkenfeld/sphinx-contrib/issues/182/sphinxcontribautohttpflask-sphinx-object
#

import os
import sys
import subprocess
sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('../..'))  # For getting the /common files


def get_git_revision_hash():
    """Get git revision number in long form as a SHA-1 hash to identify it

   From:
    https://stackoverflow.com/questions/14989858/get-the-current-git-hash-in-a-python-script

    Args:
        None

    Returns:
        A long string representation of the current git revision

    Raises:
        None

    When running within a docker container will return errors
    """
    return subprocess.check_output(['git',
                                    'rev-parse',
                                    'HEAD']).decode('utf-8').rstrip()


def get_git_revision_short_hash():
    """Get git revision number in short form as a SHA-1 hash to identify it

   From:
    https://stackoverflow.com/questions/14989858/get-the-current-git-hash-in-a-python-script

    Args:
        None

    Returns:
        A short 10 char string representation of the current git revision

    Raises:
        None
    When running within a docker container will return errors
    """
    return subprocess.check_output(['git',
                                    'rev-parse',
                                    '--short',
                                    'HEAD']).decode('utf-8').rstrip()


def get_git_branch_name():
    """Get the abbreviated reference name of the current git branch

    Args:
        None

    Returns:
        String of the current branch

    Raises:
        None
    When running within a docker container will return errors
    """
    return subprocess.check_output(['git',
                                    'rev-parse',
                                    '--abbrev-ref',
                                    'HEAD']).decode('utf-8').rstrip()


def get_git_release_tag():
    """Get the release tag for a commit

    Args:
        None

    Returns:
        A string of the release tag for the current commit

    Raises:
        None

    When running within a docker container will return errors
    """
    return subprocess.check_output(['git',
                                    'describe',
                                    '--tags']).decode('utf-8').rstrip()


# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'


# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.doctest',
              'sphinx.ext.coverage',
              'sphinxcontrib.httpdomain']
# sphinxcontrib.autohttp.flask and sphinxcontrib.autohttp.flaskqref removed
# as per bug mentioned in header

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'PyIoT'
copyright = '2017-2018 Innocorps Research Corporation, see LICENSE'
author = 'see AUTHORS'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#

# if get_git_branch_name() is 'master':
#    version = get_git_release_tag()
#    release = get_git_release_tag() + ' ' + 'master'
# else:
#    version = get_git_revision_short_hash() + ' ' + get_git_branch_name()
#    release = get_git_revision_short_hash() + ' ' + get_git_branch_name()

# For building within docker containers look at environment variables
try:
    SPHINX_GIT_REV_SHORT = os.environ['SPHINX_GIT_REV_SHORT']
    version = SPHINX_GIT_REV_SHORT
    release = SPHINX_GIT_REV_SHORT
except KeyError as e:
    print(e)


# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False


# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
import sphinx_rtd_theme
html_theme = 'sphinx_rtd_theme'
#html_theme = 'alabaster'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# This is required for the alabaster theme
# refs: http://alabaster.readthedocs.io/en/latest/installation.html#sidebars
html_sidebars = {
    '**': [
        'about.html',
        'navigation.html',
        'relations.html',  # needs 'show_related': True theme option to display
        'searchbox.html',
        'donate.html',
    ]
}


# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'PyIoT Backenddoc'


# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',

    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'sphinx_backend.tex', 'sphinx\\_backend Documentation',
     'cschentag', 'manual'),
]


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'sphinx_backend', 'sphinx_backend Documentation',
     [author], 1)
]


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'sphinx_backend', 'sphinx_backend Documentation',
     author, 'sphinx_backend', 'One line description of project.',
     'Miscellaneous'),
]