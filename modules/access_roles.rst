Access Roles
============

`snowform_access_roles`_ creates three access roles for every schema you list, following Snowflake's `recommendation for access roles`_.
Your functional roles, like a consumer or developer role, then get one of these roles instead of individual privileges.

.. _snowform_access_roles: https://github.com/inovex/snowform_access_roles
.. _recommendation for access roles: https://docs.snowflake.com/en/user-guide/security-access-control-considerations#aligning-object-access-with-business-functions


Roles and Hierarchy
-------------------

For a database ``SALES`` and a schema ``RAW`` you get:

* ``SALES_RAW_R`` reads everything in the schema.
* ``SALES_RAW_RW`` also writes to tables and stages and operates tasks and dynamic tables.
* ``SALES_RAW_FULL`` also gets all privileges on the schema itself, so it can create, change and drop objects.

The roles `inherit from each other <https://github.com/inovex/snowform_access_roles/blob/0.0.2/role_hierarchy.tf>`__: ``R`` is granted to ``RW``, and ``RW`` to ``FULL``.
So ``FULL`` has all read and write privileges without granting them twice.
All three roles are also granted to ``SYSADMIN``, so the system administrator can always reach every object.


Privileges
----------

All three roles get ``USAGE`` on the database and the schema.
The read and write privileges are granted on all existing objects and on future objects, so new tables get the right access without another deploy.
The table below follows the `read privileges <https://github.com/inovex/snowform_access_roles/blob/0.0.2/role_privileges_r.tf#L5-L46>`__ and `write privileges <https://github.com/inovex/snowform_access_roles/blob/0.0.2/role_privileges_rw.tf#L5-L22>`__ defined in the module.

.. list-table::
   :header-rows: 1

   * - Object type
     - ``R``
     - ``RW`` (on top of ``R``)
   * - Tables
     - SELECT, REFERENCES
     - INSERT, UPDATE, DELETE, TRUNCATE
   * - Views, streams
     - SELECT
     -
   * - Materialized views
     - SELECT, REFERENCES
     -
   * - Dynamic tables
     - SELECT, MONITOR
     - OPERATE
   * - Stages
     - USAGE, READ
     - WRITE
   * - File formats, procedures, functions
     - USAGE
     -
   * - Tasks
     - MONITOR
     - OPERATE

``FULL`` gets `ALL PRIVILEGES <https://github.com/inovex/snowform_access_roles/blob/0.0.2/role_privileges_full.tf#L7>`__ on the schema.
That covers the ``CREATE`` privileges for every object type, plus ``MODIFY`` and ``MONITOR`` on the schema.

The grants on all existing objects use ``always_apply``, so every plan shows them as changes.
That is expected: running them again gives objects created outside Terraform the same access.


Usage
-----

.. code-block:: hcl

   module "access_roles" {
     source  = "github.com/inovex/snowform_access_roles.git?ref=0.0.2"
     db      = snowflake_database.sales
     schemas = [
       { name = "RAW" },
       { name = "EXPORT" },
     ]

     providers = {
       snowflake.useradmin     = snowflake.useradmin
       snowflake.sysadmin      = snowflake.sysadmin
       snowflake.securityadmin = snowflake.securityadmin
     }
     depends_on = [snowflake_schema.raw, snowflake_schema.export]
   }

   # Give a functional role read access to RAW
   resource "snowflake_grant_account_role" "analyst_reads_raw" {
     provider         = snowflake.securityadmin
     role_name        = module.access_roles.r["RAW"].name
     parent_role_name = snowflake_account_role.analyst.name
   }

The module does not create the database or the schemas.
Create them first and list them in ``depends_on``.


Inputs and Outputs
------------------

.. list-table::
   :header-rows: 1

   * - Name
     - Description
   * - ``db`` (input)
     - The database, as an object with a ``name``. Passing the ``snowflake_database`` resource works.
   * - ``schemas`` (input)
     - List of ``{ name = "..." }``. One set of roles per schema.
   * - ``r``, ``rw``, ``full`` (outputs)
     - Maps from schema name to the ``snowflake_account_role`` resource.

It needs the ``useradmin`` provider for the roles, ``sysadmin`` for the privileges and ``securityadmin`` for the hierarchy.


Compared to SnowDDL
-------------------

SnowDDL's `permission model`_ has similar read and write schema roles, plus an owner role that owns every object in the schema through future ``OWNERSHIP`` grants.
SnowForm has no owner role.
Objects are owned by the role that created them, usually ``SYSADMIN``, and ``FULL`` gets the privileges to create and manage them.

SnowDDL also lets you change the privileges per object type in YAML.
In SnowForm they are fixed in the module for now.
Making them configurable is on the :ref:`roadmap <roadmap>`.

.. _permission model: https://docs.snowddl.com/basic/yaml-configs/permission-model
