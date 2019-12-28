============================
Smile Reconciliation By Line
============================

.. |badge2| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-Smile_SA%2Fodoo_addons-lightgray.png?logo=github
    :target: https://github.com/Smile-SA/odoo_addons/tree/11.0/smile_reconcile_by_line
    :alt: Smile-SA/odoo_addons

|badge2| |badge3|


This module helps to reconcile bank statements line by line.

Features :

* Add a button to each statement line, that not reconciled yet
* By clicking on the button, we display the line to reconcile it, in a pop-up window
* We click 'validate' or 'Automatic reconciliation' button, then destroy the validated line

**Table of contents**

.. contents::
   :local:

Usage
=====

1. By opening Bank statements, we can see buttons on transactions that not reconciled yet

.. figure:: static/description/bank_statements.png
   :alt: bank_statements
   :width: 850px

2. We select line to reconcile, and we click the button 'reconcile'
    If there is no debit (or credit) compatible with the line, a 'validate' button will display

.. figure:: static/description/reconcile_button.png
   :alt: reconcile_button
   :width: 850px

3. A progress bar helps us to know how much line stay

.. figure:: static/description/1_3.png
   :alt: 1_3
   :width: 850px

4. After doing all the reconciliations, we get a congrats Emoji

.. figure:: static/description/congrats.png
   :alt: congrats
   :width: 850px


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/Smile-SA/odoo_addons/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/Smile-SA/odoo_addons/issues/new?body=module:%20smile_log%0Aversion:%2011.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Do not contact contributors directly about support or help with technical issues.

GDPR / EU Privacy
=================
This addons does not collect any data and does not set any browser cookies.

Credits
=======

Contributors
------------

* Ismail EL BAKKALI

Maintainer
----------
This module is maintained by the Smile SA.

Since 1991 Smile has been a pioneer of technology and also the European expert in open source solutions.

.. image:: https://avatars0.githubusercontent.com/u/572339?s=200&v=4
   :alt: Smile SA
   :target: http://smile.fr

This module is part of the `odoo-addons <https://github.com/Smile-SA/odoo_addons>`_ project on GitHub.

You are welcome to contribute.

