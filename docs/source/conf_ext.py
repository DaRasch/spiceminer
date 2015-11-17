# -*- coding: utf-8 -*-

# -- sphinx.ext.autodoc ---------------------------------------------------

autoclass_content = 'class'
autodoc_member_order = 'bysource'
autodoc_default_flags = []
autodoc_docstring_signature = True
autodoc_mock_imports = []#['spiceminer._spicewrapper']

# -- sphinx.ext.napoleon --------------------------------------------------

napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_include_special_with_doc = False
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = False
napoleon_use_rtype = False

# -- numpydoc -------------------------------------------------------------

# Whether to produce plot:: directives for Examples sections that contain
# import matplotlib.
numpydoc_use_plots = False

# Whether to show all members of a class in the Methods and Attributes sections
# automatically.
numpydoc_show_class_members = True


# Whether to create a Sphinx table of contents for the lists of class methods
# and attributes. If a table of contents is made, Sphinx expects each entry to
# have a separate page.
numpydoc_class_members_toctree = False

# Whether to insert an edit link after docstrings.
# (DEPRECATED – edit your HTML template instead)
numpydoc_edit_link = False
