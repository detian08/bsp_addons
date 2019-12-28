=================
Automated Actions
=================

.. |badge2| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-Smile_SA%2Fodoo_addons-lightgray.png?logo=github
    :target: https://github.com/Smile-SA/odoo_addons/tree/11.0/smile_base_automation
    :alt: Smile-SA/odoo_addons

|badge2| |badge3|

This module extends base_automation.

To be able to track logs of automated actions execution, make sure you give access rights to the user by adding him to the rule ``Smile Logs / User`` as follow:

#. Go to ``Settings > Users & companies > Users`` menu and select the user.
#. In ``Access Rights > Others`` check the rule ``Smile Logs / User``.

**Table of contents**

.. contents::
   :local:

Features
========

    * Extend automated actions to:
        * Trigger on other methods
        * Limit executions per record
        * Log executions for actions not on timed condition
        * Raise customized exceptions
        * Categorize them
    * Extend server actions to:
        * Force execution even if records list is empty
        * Execute in asynchronous mode

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/Smile-SA/odoo_addons/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed
`feedback <https://github.com/Smile-SA/odoo_addons/issues/new?body=module:%20smile_base_automation%0Aversion:%2011.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Do not contact contributors directly about support or help with technical issues.

Credits
=======

Authors
~~~~~~~

* Smile SA

Contributors
~~~~~~~~~~~~

* Corentin Pouhet-Brunerie

Maintainers
~~~~~~~~~~~

This module is maintained by the Smile SA.

Since 1991 Smile has been a pioneer of technology and also the European expert in open source solutions.

.. image:: https://avatars0.githubusercontent.com/u/572339?s=200&v=4
   :alt: Smile SA
   :target: http://smile.fr

This module is part of the `odoo-addons <https://github.com/Smile-SA/odoo_addons>`_ project on GitHub.

You are welcome to contribute.
