🧩 Modules
==========

SnowForm is a set of small, independent Terraform modules.
Each one does one job, so you can use any of them on its own and replace it later without touching the others.

* :doc:`access_roles` creates the read, read-write and full access roles for your schemas.
* :doc:`import_listing` imports Snowflake shares as databases and gives roles access to them.
* :doc:`logical_import_layer` groups tables from imported shares into your own databases and schemas as views, and keeps their comments.

All modules need the ``snowflakedb/snowflake`` provider 2.x (``>= 2.1.0, < 3.0.0``) and Terraform 1.7 or OpenTofu 1.9 or later.
They take their providers through aliases named after the role they use, see :doc:`../getting_started`.

.. toctree::
   :maxdepth: 1

   access_roles
   import_listing
   logical_import_layer
