.. SnowForm documentation master file, created by
   sphinx-quickstart on Tue Jul  1 10:19:37 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

❄ Introduction
================


What Is SnowForm
----------------

SnowForm is a modular template for Snowflake accounts, built on the `official Snowflake Terraform provider`_.
It helps developers set up a new Snowflake account quickly while following Snowflake's best practices and guidelines.
To set up an account, start with :doc:`getting_started`.

.. _official Snowflake Terraform provider: https://registry.terraform.io/providers/snowflakedb/snowflake/latest/docs


Who It Is For
-------------

SnowForm is made for smaller teams or a single administrator managing a Snowflake account.
The setup is intentionally simple, so you can customize it and extend it for the requirements of your organization.
Every role, grant and database is declared in plain Terraform, and each concern lives in its own module.
This makes it easy to see what every object in the account is for, and quick to learn how the pieces fit together.

SnowForm uses Terraform or `OpenTofu`_, which many engineers and architects already know, so you can start without learning a new tool.
It also lets you manage your Snowflake account next to the infrastructure you run on other cloud providers, like Azure or Google Cloud.

.. _OpenTofu: https://opentofu.org/


What It Contains
----------------

At the center is the :doc:`modules/access_roles` module, which sets up role based access control.
It follows Snowflake's `recommendation of access roles and functional roles`_, and keeps Snowflake's secondary roles enabled.

Access roles form the first tier.
For every schema, the module creates a read, a read-write and a full access role, and each one includes the one below it.
Every access role has usage on its database and schema, plus the matching privileges on the objects in the schema, like tables, views and procedures.

Functional roles form the second tier.
They bundle access roles for a group of users, for example a consumer role that only reads, or a developer role that can also write.
You define them in your own configuration, like the ``CONSUMER_ROLE`` in the example repository.

Two more modules bring in data that other Snowflake accounts share with you.
:doc:`modules/import_listing` creates databases from Snowflake shares and grants roles access to them.
:doc:`modules/logical_import_layer` then maps the tables of these imported databases to views or dynamic tables in your own databases and schemas, grouped by business logic, and keeps their comments.

.. _recommendation of access roles and functional roles: https://docs.snowflake.com/en/user-guide/security-access-control-overview#roles


How It Is Built
---------------

Each module is a small Terraform module in its own repository, and the modules do not depend on each other.
Your configuration pins every module to a released git tag, so an update only happens when you raise the version.
See :doc:`modules/index` for what each module creates and all of its inputs.

The modules never configure a provider.
Instead, you pass them three providers, each logged in with a different Snowflake system role:

* ``useradmin`` creates the roles.
* ``sysadmin`` creates databases, schemas, views and procedures, and grants privileges on them.
* ``securityadmin`` grants roles to other roles.

The role that creates an object owns it, so ownership always stays with these system roles.
Access roles get privileges on objects, but never ownership.

Every module comes with unit tests that plan against a mocked provider, so they run without a Snowflake account.
On every push, CI runs these tests together with ``tflint``, a format check and a `KICS`_ security scan.
Your own configuration is deployed the same way: GitHub Actions plans on every push and applies the changes from ``main``.

.. _KICS: https://kics.io/


Template Outline
----------------

SnowForm consists of these repositories:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Repository
     - Purpose
   * - `snowform_access_roles`_
     - Read, read-write and full access roles for every schema, with grants on current and future objects.
   * - `snowform_import_listing`_
     - Databases created from Snowflake shares, with ``IMPORTED PRIVILEGES`` for the roles you list.
   * - `snowform_logical_import_layer`_
     - Views or dynamic tables that group imported data by business logic and keep its comments.
   * - `snowform_example_usage`_
     - A root configuration that uses the three modules to deploy a real test account from GitHub Actions.

Your own configuration can follow the layout of the example repository, with one file per concern:

.. code-block:: text

   terraform/
   ├── main.tf                              # terraform block and state backend
   ├── provider.tf                          # the useradmin, sysadmin and securityadmin providers
   ├── variables.tf                         # deploy user credentials
   ├── common_db_schema.tf                  # a shared database, schema and warehouse
   ├── access_roles.tf                      # access roles for each schema
   ├── functional_roles.tf                  # roles for groups of users, built from access roles
   ├── import_shares.tf                     # databases from Snowflake shares
   └── import_shares_logical_grouping.tf    # views on the imported data

.. _snowform_access_roles: https://github.com/inovex/snowform_access_roles
.. _snowform_import_listing: https://github.com/inovex/snowform_import_listing
.. _snowform_logical_import_layer: https://github.com/inovex/snowform_logical_import_layer
.. _snowform_example_usage: https://github.com/inovex/snowform_example_usage


Comparison With SnowDDL
-----------------------

If you are deciding between SnowForm and `SnowDDL`_, see :doc:`snowddl_comparison`.

.. _SnowDDL: https://docs.snowddl.com/


.. _roadmap:

Roadmap
-------

* Make the privileges of the access roles configurable per object type, and cover more object types.
* A setup guide where the first apply also defines the deploy user and its security settings, like authentication policies, in Terraform.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   self
   getting_started
   modules/index
   limitations
   snowddl_comparison
