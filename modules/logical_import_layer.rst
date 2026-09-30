Logical Import Layer
====================

`snowform_logical_import_layer`_ puts tables and views from imported databases into your own structure.
You map each source object to a target database, schema and name, for example to collect all product data from several shares in one ``PRODUCTS`` schema.
Consumers then only need access to your databases, and the shares stay an internal detail.

.. _snowform_logical_import_layer: https://github.com/inovex/snowform_logical_import_layer


How It Works
------------

By default the module creates a view for every mapping.
A plain ``CREATE VIEW`` would lose the column comments of the source, so the module deploys a small `Python stored procedure <https://github.com/inovex/snowform_logical_import_layer/blob/0.0.5/create_view_with_comments_procedure.py>`__, ``CREATE_VIEW_WITH_COLUMN_COMMENTS``.
It reads the comments from the source's ``INFORMATION_SCHEMA`` and creates the view with them.
Terraform calls it once per mapping, and `creates all views again <https://github.com/inovex/snowform_logical_import_layer/blob/0.0.5/main.tf#L26-L31>`__ whenever the procedure changes.

With ``resource_type = "dynamic_table"`` you get dynamic tables instead, which store the data and refresh on a schedule.

The roles in ``database_role_grants`` get ``USAGE`` on the target database and on all current and future schemas in it, plus ``SELECT`` on all `current and future views <https://github.com/inovex/snowform_logical_import_layer/blob/0.0.5/main.tf#L90-L123>`__.


Before You Start
----------------

* The source objects and the target databases and schemas have to exist already.
* The procedure is a preview resource in the provider. Enable it on the ``sysadmin`` provider:

  .. code-block:: hcl

     preview_features_enabled = ["snowflake_procedure_python_resource"]

* Put the schema that holds the procedure in the module's ``depends_on``. Otherwise Terraform can try to create the procedure before the schema exists.


Usage
-----

.. code-block:: hcl

   module "logical_import_layer" {
     source = "github.com/inovex/snowform_logical_import_layer.git?ref=0.0.5"

     procedure_database = "COMMON"
     procedure_schema   = "COMMON"

     source_to_target_mappings = {
       "CUSTOMER_LEADS_IMPORTED_DB.SNOWFORM_SCHEMA.CUSTOMER_LEADS" = {
         target_database = "IMPORTED_INOVEX"
         target_schema   = "CUSTOMER_DATA"
         target_name     = "CUSTOMER_LEADS"
       }
     }

     database_role_grants = {
       "IMPORTED_INOVEX" = [snowflake_account_role.consumer.name]
     }

     providers = {
       snowflake.sysadmin      = snowflake.sysadmin
       snowflake.securityadmin = snowflake.securityadmin
     }
     depends_on = [snowflake_schema.common_common_schema]
   }


Inputs
------

.. list-table::
   :header-rows: 1

   * - Name
     - Description
   * - ``procedure_database``, ``procedure_schema``
     - Where the procedure is created. Required.
   * - ``source_to_target_mappings``
     - Map from the fully qualified source (``DB.SCHEMA.OBJECT``) to ``{ target_database, target_schema, target_name }``. Required.
   * - ``database_role_grants``
     - Map from target database to the roles that get read access. Every database needs at least one role. Required.
   * - ``resource_type``
     - ``"view"`` (default) or ``"dynamic_table"``.
   * - ``dynamic_table_warehouse``
     - Warehouse for refreshing dynamic tables. Needed for ``"dynamic_table"``.
   * - ``dynamic_table_lag_duration``
     - Maximum staleness, like ``"5 minutes"`` or ``"2 hours"``.
   * - ``dynamic_table_lag_downstream``
     - Refresh only when downstream dynamic tables refresh. Default ``false``.

The outputs list the procedure name, the created views or dynamic tables, and the granted databases and roles.


Known Limitations
-----------------

* The read grants only cover views. With ``resource_type = "dynamic_table"``, grant ``SELECT`` on the dynamic tables yourself.
* If the procedure fails, it `returns an error message <https://github.com/inovex/snowform_logical_import_layer/blob/0.0.5/create_view_with_comments_procedure.py#L106-L113>`__ instead of raising an error. Terraform then reports success even though the view was not created, so check the views after the first deploy.
