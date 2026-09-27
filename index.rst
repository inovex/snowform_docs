.. SnowForm documentation master file, created by
   sphinx-quickstart on Tue Jul  1 10:19:37 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

❄ Introduction
================

SnowForm is a modular template for Snowflake accounts, built on the `official Snowflake Terraform provider`_.
It helps you set up a new account quickly while following Snowflake's best practices.

It is made for smaller teams or a single administrator managing a Snowflake account.
The setup is intentionally simple and transparent, so it is easy to understand what every object is for, and easy to extend for your own requirements.

Each part is a separate Terraform module, see :doc:`modules/index`.
To set up an account, start with :doc:`getting_started`.

.. _official Snowflake Terraform provider: https://registry.terraform.io/providers/snowflakedb/snowflake/latest/docs

Differences to SnowDDL
----------------------

`SnowDDL`_ is a standalone tool for managing Snowflake accounts.

.. _SnowDDL: https://docs.snowddl.com/

Where SnowDDL Is Stronger
^^^^^^^^^^^^^^^^^^^^^^^^^

* It is stateless. SnowDDL reads the current state directly from the account, so it always sees manual changes.
* It is more opinionated and very configurable, which suits large accounts and larger teams.
* It comes with a predefined, fine grained `role hierarchy`_.
* Setting up a large account makes you review and define every option explicitly, so long term decisions are made up front.

.. _role hierarchy: https://docs.snowddl.com/guides/role-hierarchy#rationale

Where SnowForm Is Stronger
^^^^^^^^^^^^^^^^^^^^^^^^^^

* It is built on the `official Snowflake Terraform provider`_, which is maintained and supported by Snowflake.
* The deployment itself is left to the provider and Terraform, so teams can use the Terraform experience they already have.
* It is lightweight, so getting started is quick.
* Everything after the initial deploy user is defined in Terraform, which makes the account transparent and easy to audit.
* It works with `KICS`_, other security scanners and the rest of the Terraform ecosystem.
* You can adopt it step by step, and add, remove or replace modules one at a time.
* It only follows Snowflake's own best practices. For example, SnowDDL enforces a `convention for object identifiers`_, while SnowForm only follows the `Snowflake identifier requirements`_.

.. _KICS: https://kics.io/
.. _convention for object identifiers: https://docs.snowddl.com/guides/object-identifiers
.. _Snowflake identifier requirements: https://docs.snowflake.com/en/sql-reference/identifiers-syntax

Role Hierarchy
^^^^^^^^^^^^^^

SnowDDL uses a strict `3 tier system`_ of access, business and user roles, so every user has a dedicated user role.
SnowForm follows Snowflake's `simplified recommendation with access and functional roles`_, which matches SnowDDL's first two tiers, and skips the user roles.
Instead, you can use roles managed by an external IAM system, and combine them with any user, team or use case roles your developers define.

SnowDDL does not use Snowflake's secondary roles, since its user roles make them redundant.
In SnowForm, secondary roles stay enabled, which is Snowflake's default.
That way users see which roles they have and which one they are using, which helps when onboarding people or tracking down access problems.
If you need user roles, you can add them as another layer.
In enterprise settings we recommend managing that layer in your IAM system, for better security and easier audits.

No Automatic Cleanup
^^^^^^^^^^^^^^^^^^^^

SnowDDL drops unused roles for schemas, warehouses, shares and users that no longer exist, to avoid orphaned roles.
SnowForm does not add or remove anything automatically: every object exists because someone declared it.
Instead, it tries not to create objects you do not need.
The one exception is the :doc:`modules/access_roles` module, which creates all three access roles for every schema, whether you use them or not.

Object Ownership
^^^^^^^^^^^^^^^^

SnowDDL makes a schema owner role the `owner of every object`_ in its schema, through future ownership grants.
In SnowForm, the role that creates an object owns it, following the provider it is created with:

* ``SYSADMIN`` owns databases, schemas, warehouses, views and procedures.
* ``USERADMIN`` owns the access roles and service users.
* ``SECURITYADMIN`` owns functional roles and authentication policies created with the ``securityadmin`` provider.

The access roles get privileges on the objects, but never ownership.
So ownership stays with the system roles, and nothing depends on a role that a module could remove.

.. _owner of every object: https://docs.snowddl.com/guides/other-guides/ownership

Dependencies Between Objects
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

SnowDDL `resolves dependencies`_ with a fixed order, for example all tables before all views, and needs explicit dependencies only between objects of the same type.
SnowForm leaves this to Terraform.
It builds a dependency graph from the references between resources, creates objects in that order, and runs independent ones in parallel.
When one resource needs another without referencing it, like a grant on a schema that is created in another file, add ``depends_on``.

.. _resolves dependencies: https://docs.snowddl.com/guides/other-guides/dependency-management

.. _roadmap:

Roadmap
-------

* Make the privileges of the access roles configurable per object type, and cover more object types.
* A setup guide where the first apply also defines the deploy user and its security settings, like authentication policies, in Terraform.

.. _3 tier system: https://docs.snowddl.com/guides/role-hierarchy#general-overview
.. _simplified recommendation with access and functional roles: https://docs.snowflake.com/en/user-guide/security-access-control-overview#roles

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   self
   getting_started
   modules/index
   limitations
