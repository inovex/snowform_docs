.. SnowTF documentation master file, created by
   sphinx-quickstart on Tue Jul  1 10:19:37 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

❄ Introduction
================

SnowTF is a modular snowflake template based on `official Snowflake Terraform provider`_.
It enables developers to quickly set up a new snowflake account following best practices and guidelines.

The architecture of SnowTF template is specifically designed to support smaller teams or individual administrators managing a Snowflake account.
By prioritizing transparency and modularity, the system enhances clarity and facilitates faster learning and understanding of the underlying entities.
The architecture is intentionally straightforward, making it easy to customize and extend to meet specific organizational requirements.

.. _official Snowflake Terraform provider: https://registry.terraform.io/providers/snowflakedb/snowflake/latest/docs

Differences to SnowDDL
----------------------

`SnowDDL`_ is a standalone tool that can be used to manage snowflake accounts.

.. _SnowDDL: https://docs.snowddl.com/

Why is SnowDDL better?
^^^^^^^^^^^^^^^^^^^^^^

* Stateless operation: SnowDDL queries the Snowflake account directly to determine the current state, ensuring synchronization with any manual changes.
* Offers a more opinionated and highly configurable approach, making it well-suited for managing large Snowflake accounts and supporting larger teams.
* Provides a predefined, fine-grained `role hierarchy`_ to facilitate granular access control and permission management.
* During the setup of a large account, all configuration options must be reviewed and explicitly defined, ensuring that long-term architectural decisions are considered up front.

.. _role hierarchy: https://docs.snowddl.com/guides/role-hierarchy#rationale

Why is SnowTF better?
^^^^^^^^^^^^^^^^^^^^^

* Built on the `official Snowflake Terraform provider`_, ensuring reliability and ongoing support.
* Deployment logic and mechanisms are delegated to the official provider, leveraging existing team expertise with Terraform.
* Lightweight architecture enables rapid onboarding and ease of use.
* All resources, including deployment users, are defined declaratively in Terraform, providing full transparency and auditability.
* Fully compatible with `KICS`_, other security tools, and the broader Terraform ecosystem.
* Flexible design tailored for specialized and smaller teams.
* Supports incremental adoption and decommissioning, allowing components to be added, removed, or replaced in a controlled and gradual manner.
* Follows only the official Snowflake best practices. For Example SnowDDL enforces a `convention for object identifiers`_, while we only follow the `Snowflake identifier requirements`_.

.. _KICS: https://kics.io/
.. _official Snowflake Terraform provider: https://registry.terraform.io/providers/snowflakedb/snowflake/latest/docs
.. _convention for object identifiers: https://docs.snowddl.com/guides/object-identifiers
.. _Snowflake identifier requirements: https://docs.snowflake.com/en/sql-reference/identifiers-syntax

Similarities and Differences
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* For RBAC SnowDDL uses a strict `3 tier system`_: access, business, and user roles. That means every user has a dedicated user role.
  In SnowTF we follow the `simplified recommendation with access and functional roles`_ (analog to first two tiers of SnowDDL system), but skip the individual user roles.
  As a replacement, admins can rely on custom roles usually managed externally by an IAM system.
  This can be freely combined with any additional user, team, use case roles that are freely definable and managed by the developers.
  This way we ensure the flexibility of our template and give developers the freedom to extend the RBAC system as they see fit.

* SnowDDL doesn't use the native Snowflake secondary roles feature as it is redundant with the tier 3 user roles layer.
  SnowTF does not enforce the third tier of user roles and the secondary roles feature is enabled by default as per official Snowflake configuration.
  We made this decision for SnowTF as we want to make our users aware of the roles they are assigned and are currently using.
  That way the RBAC system is more transparent and the non-technical users have a better intuition of what is needed when onboarding new users or communicating eventual issues.
  However this is only the default behaviour and the user roles can easily be implemented as additional roles layer if needed.
  For enterprice ettings we recommend using the established IAM system for managing the "third tier" of user or team roles for better security and easier auditing.

* SnowDDL: ``Unused roles for non-existent schemas, warehouses, shares, users are dropped automatically. It helps to reduce amount of "orphan" roles in account.``
  SnowTF does not introduce any automation! No entities are added or deleted automatically uness so declaratively specifified by a developer.
  Instead we focus on not introducing any unnecessary or unused entities into the system.
  The only exception where SnowTF might introduce unused entities is with the access roles module (TODO add link) where all the access roles are created for specified databases and schemas.

TODOs
-----
* which grants are included in SnowTF access_roles? https://docs.snowddl.com/basic/yaml-configs/permission-model

  * We need to extend the grants to all relevant permissions and make it configurable

* Create deploy/admin user https://docs.snowddl.com/guides/other-guides/admin

  * prepare tutorial with accountadmin deploy/admin user that can take care of everything with the first tf apply
  * we want it as the per default we want to set up the security measures as well which are transparent and easier to audit

* research https://docs.snowddl.com/guides/other-guides/ownership
* Exlplizitely write that our dependencies are managed in terraform VS SnowDDL own mechanism https://docs.snowddl.com/guides/other-guides/dependency-management

.. _3 tier system: https://docs.snowddl.com/guides/role-hierarchy#general-overview
.. _simplified recommendation with access and functional roles: https://docs.snowflake.com/en/user-guide/security-access-control-overview#roles

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   self
   getting_started
   limitations

