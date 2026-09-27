🚀 Getting Started
==================

This guide sets up a Snowflake account with SnowForm and deploys it from GitHub Actions.
It follows `snowform_example_usage`_, which runs exactly this setup against a real test account, so you can always look up the complete files there.

.. _snowform_example_usage: https://github.com/inovex/snowform_example_usage


Prerequisites
-------------

* A Snowflake account and a user with ``ACCOUNTADMIN``. You only need it once, to create the deploy user.
* `OpenTofu`_ 1.9 or later, or Terraform 1.7 or later.
* A GitHub repository for your configuration.
* A remote state backend. The example uses a Google Cloud Storage bucket, but any backend with locking works.

.. _OpenTofu: https://opentofu.org/docs/intro/install/


1. Create the deploy user
-------------------------

Terraform runs as a service user that logs in with a key pair.
Everything else, including the roles and users of your team, is created by Terraform later.

Generate an encrypted key pair.
Keep the private key out of git (the example's ``.gitignore`` excludes ``*.p8`` and ``*.pu``):

.. code-block:: sh

   openssl genrsa 2048 | openssl pkcs8 -topk8 -v2 aes256 -inform PEM -out snowflake_deploy.p8
   openssl rsa -in snowflake_deploy.p8 -pubout -out snowflake_deploy.pu

Then create the user in Snowsight.
Paste the public key without the ``BEGIN`` and ``END`` lines:

.. code-block:: sql

   USE ROLE USERADMIN;
   CREATE USER SNOWFLAKE_DEPLOY
     TYPE = SERVICE
     RSA_PUBLIC_KEY = '<contents of snowflake_deploy.pu>'
     COMMENT = 'Terraform deploy user';

   USE ROLE ACCOUNTADMIN;
   GRANT ROLE USERADMIN TO USER SNOWFLAKE_DEPLOY;
   GRANT ROLE SYSADMIN TO USER SNOWFLAKE_DEPLOY;
   GRANT ROLE SECURITYADMIN TO USER SNOWFLAKE_DEPLOY;

The deploy user doesn't need ``ACCOUNTADMIN``.
The few things only ``ACCOUNTADMIN`` can do, like granting access to the ``SNOWFLAKE`` database, are one time steps you run by hand.


2. Configure the providers
--------------------------

SnowForm modules never configure a provider themselves.
They expect three aliased providers, one per system role, so every object is created by the role that should own it:

* ``useradmin`` creates roles and users.
* ``sysadmin`` creates databases, schemas and warehouses, and grants privileges on them.
* ``securityadmin`` builds the role hierarchy and manages policies.

.. code-block:: hcl

   provider "snowflake" {
     alias             = "sysadmin"
     role              = "SYSADMIN"
     organization_name = "<ORG>"
     account_name      = "<ACCOUNT>"
     user              = var.SNOWFLAKE_DEPLOY_USER
     authenticator     = "SNOWFLAKE_JWT"
     private_key            = base64decode(var.SNOWFLAKE_DEPLOY_PRIVATE_KEY_BASE64)
     private_key_passphrase = var.SNOWFLAKE_DEPLOY_PRIVATE_KEY_PASSPHRASE
     warehouse         = "XS_WH"
   }

   # Same block again with alias/role "useradmin"/"USERADMIN" and "securityadmin"/"SECURITYADMIN".

Give the ``securityadmin`` provider a warehouse too, and grant ``SECURITYADMIN`` usage on it.
Some reads, like the one after attaching an authentication policy to a user, fail without one.
Some resources are preview features in the provider and have to be listed in ``preview_features_enabled``.
The module pages say which ones.


3. Set up the state backend
---------------------------

Use a remote backend with locking from the start.
Without locking, two runs can overwrite each other's state, and a lost state makes the next run try to recreate every object.

.. code-block:: hcl

   terraform {
     backend "gcs" {
       bucket = "<your-state-bucket>"
       prefix = "snowflake"
     }
   }

The example repository has a `setup script`_ that creates a versioned, private bucket and lets GitHub Actions use it through Workload Identity Federation, so no cloud keys are stored anywhere.
Its README explains how to restore an older state version.

.. _setup script: https://github.com/inovex/snowform_example_usage/blob/main/scripts/setup_gcp_state_backend.sh


4. Add the modules
------------------

Reference each module by a release tag.
This creates access roles for a ``COMMON`` database with one schema:

.. code-block:: hcl

   module "access_roles" {
     source  = "github.com/inovex/snowform_access_roles.git?ref=0.0.2"
     db      = snowflake_database.common_db
     schemas = [{ name = "COMMON" }]

     providers = {
       snowflake.useradmin     = snowflake.useradmin
       snowflake.sysadmin      = snowflake.sysadmin
       snowflake.securityadmin = snowflake.securityadmin
     }
     depends_on = [snowflake_schema.common_common_schema]
   }

See :doc:`modules/index` for what each module creates and all of its inputs.


5. Deploy from GitHub Actions
-----------------------------

Store the credentials as secrets of a GitHub environment, for example ``staging``:

* ``TF_VAR_SNOWFLAKE_DEPLOY_PRIVATE_KEY_BASE64``: the private key, as ``base64 -i snowflake_deploy.p8 | tr -d '\n'``
* ``TF_VAR_SNOWFLAKE_DEPLOY_PRIVATE_KEY_PASSPHRASE``: the passphrase of the key

Put the user name in the environment variable ``TF_VAR_SNOWFLAKE_DEPLOY_USER``.

The example `workflow`_ runs lint, format check, tests, a KICS security scan, validate and plan on every push.
Only pushes to ``main`` run ``tofu apply``, so every change gets a plan you can review in the pull request first.

.. _workflow: https://github.com/inovex/snowform_example_usage/blob/main/.github/workflows/github_actions.yaml

After the first successful run, the plan of the next run should show no changes except the grants marked ``always_apply``.
Those grants run again on purpose, so objects created since the last run get their privileges too.
