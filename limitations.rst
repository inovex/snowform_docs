⚠️  Limitations
===============


Objects the provider doesn't support yet
----------------------------------------

The official provider doesn't cover every Snowflake object, and some resources are only available as preview features.
For everything else there's the ``snowflake_execute`` resource: it runs one SQL statement on create and another one on destroy.

.. code-block:: hcl

   resource "snowflake_execute" "grant_create_network_rule" {
     provider = snowflake.sysadmin
     execute  = "GRANT CREATE NETWORK RULE ON SCHEMA COMMON.COMMON TO ROLE SECURITYADMIN"
     revert   = "REVOKE CREATE NETWORK RULE ON SCHEMA COMMON.COMMON FROM ROLE SECURITYADMIN"
   }

The example repository uses it the same way to create a Snowflake-managed MCP server, which has no resource yet.
Keep these cases rare, because ``snowflake_execute`` doesn't detect changes made outside Terraform.
It only runs ``revert`` and then ``execute`` again when the SQL itself changes.
If an object created this way loses grants when it's replaced, add ``replace_triggered_by`` to the grant, so it's granted again too.

For statements over several lines or with results you need to read back, the `Snowflake SQL provider`_ is an alternative.

.. _Snowflake SQL provider: https://registry.terraform.io/providers/aidanmelen/snowsql/latest/docs


Partial application of changes
------------------------------

Snowflake runs DDL statements one by one and commits each of them right away.
If an apply fails halfway, the account is left somewhere between the old and the new configuration.

SnowDDL handles this by `repairing`_ the objects on its next run.
SnowForm relies on Terraform's own mechanism instead: the state records every resource as soon as it's created, also when the apply fails later.
Fix the error and run plan and apply again.
Terraform only creates what's still missing, and replaces resources it marked as tainted because they failed halfway.
You can repeat this as often as needed.

Two things make this work reliably:

* A remote state backend. If the state from the failed run is lost, the next run doesn't know about the objects that were already created, and fails with ``already exists``.
* Explicit ``depends_on`` between resources that Terraform can't link by reference, like a grant on a schema that's created elsewhere. Without it, Terraform can run them in parallel, and the grant fails because the schema doesn't exist yet.

.. _repairing: https://docs.snowddl.com/guides/other-guides/limitations-and-workarounds#partial-application-of-config


Renaming objects
----------------

SnowDDL uses full object names as identifiers, so a rename in its config means dropping the old object and creating a new one, unless you rename it by hand first (see `SnowDDL renaming`_).

In SnowForm, changing the ``name`` of a database, schema, warehouse or role renames it in place with ``ALTER ... RENAME TO``.
Data and ownership stay, and grants that reference the object are revoked and granted again under the new name.

Renaming the Terraform resource itself is a different thing.
If you change the resource address, for example ``snowflake_database.sales`` to ``snowflake_database.revenue``, Terraform would drop the database and create a new one.
Add a ``moved`` block, so it keeps the existing object:

.. code-block:: hcl

   moved {
     from = snowflake_database.sales
     to   = snowflake_database.revenue
   }

The same applies to modules and to ``for_each`` keys, for example when a schema is renamed in the ``schemas`` list of the access roles module.

.. _SnowDDL renaming: https://docs.snowddl.com/guides/other-guides/limitations-and-workarounds#renaming-of-objects


Lowercase identifiers
---------------------

Lowercase and mixed case identifiers work and behave like they do in Snowflake: they have to be quoted everywhere.
We recommend uppercase identifiers, which is also what the modules expect.
