# snowtf_docs
Documentation for the SnowTF, a modular terraform based snowflake template


## Introduction:
### What is SnowForm:
SnowForm is a modular snowflake template based on the official Snowflake Terraform provider. It enables developers to quickly set up a new snowflake account following best practices and guidelines.

### For whom we build it:
The architecture of SnowForm is specifically designed to support smaller teams or individual administrators managing a Snowflake account. The architecture is intentionally straightforward, making it easy to customize and extend to meet specific organizational requirements.
By prioritizing transparency and modularity, the system enhances clarity and facilitates faster learning and understanding of the underlying entities.
Building SnowForm on a widely used IaC-techstack (Terraform/OpenTofu) allows engineers and architects to start quickly, without the need for learning additional tools. Furthermore this choice enables teams to integrate the infrastructure of their Snowflake Account easily with that of other cloud-providers like Azure or GCP.

### What we build:
At the centre of our architecture is an access-role module allowing an easy setup of an RBAC-structure. Here we decided to follow the official Snowflake recommendation of access and functional roles, also including Snowflakes secondary role feature. Access roles are built hierarchically from reading to writing and full control on the individual database-level. Each role has usage privileges on the database and schema. Additionally they are granted the corresponding privileges on the objects like tables, procedures etc on the databases. Functional roles aggregate the access roles as a second tier, allowing the definition of 'consumer-' (reader-) and 'developer'-roles.

We then build two additional modules for ingesting data from snowflake shares provided by other accounts. The snowflake_import_listing module setups databases and privileges for imported shares, while the snowflake_logical_import_layers allows structuring those imported databases according to desired business logic.

### How we build it:
Our SnowForm architecture follows a three-layered modular approach, each addressing specific aspects of Snowflake data management:

1. Access Control Foundation - [snowform_access_roles](https://github.com/inovex/snowform_access_roles): <br>
The cornerstone of our architecture implements a sophisticated RBAC system with hierarchical access roles. We create three distinct role types per data layer:
SR (Schema Read) - Basic read access to tables, views, and functions within a specific schema
SRW (Schema Read-Write) - Extends read access with write, update, delete, and truncate privileges on tables
SFULL (Schema Full Control) - Complete administrative control including DDL operations like CREATE, ALTER, DROP
The hierarchy is carefully structured where each higher-level role inherits from the lower ones (SR → SRW → SFULL), all ultimately connecting to SYSADMIN. This design enables flexible privilege assignment while maintaining security boundaries. The module automatically handles both current and future object privileges, ensuring new tables or views inherit appropriate access rights.

2. Data Import Infrastructure - [snowform_import_listing](https://github.com/inovex/snowform_import_listings): <br>
This module streamlines the process of importing external data shares into our Snowflake account. It automates the creation of shared databases from external providers and manages the complex privilege assignment process. The module takes share identifiers (typically in format "PROVIDER_ACCOUNT"."SHARE_GROUP"."SHARE_NAME") and creates corresponding databases while granting IMPORTED PRIVILEGES to specified roles. This approach centralizes share management and ensures consistent access patterns across imported data sources.

3. Logical Data Organization - [snowform_logical_import_layer](https://github.com/inovex/snowform_logical_import_layer):  <br>
This module addresses the challenge of organizing disparate imported data sources into coherent business-aligned structures. It creates a mapping layer that allows teams to consolidate related data from multiple sources into unified logical views or dynamic tables.

4. Example Usage - [snowform_example_usage](https://github.com/inovex/snowform_example_usage):  <br>
While not beeing a modul adding functionality, it examplifies how a Snowflake-Account can be set up using the above modules. 

The module employs a Python-based stored procedure approach to maintain column comments and metadata during the view creation process. This ensures that important data lineage and documentation are preserved when restructuring imported data. Teams can choose between standard views for simpler use cases or dynamic tables for scenarios requiring materialized results with configurable refresh patterns.

# Env setup

```
conda create -n snowtf python=3.12 sphinx
conda activate snowtf
pip install furo
make html
```

- https://www.sphinx-doc.org/en/master/usage/quickstart.html

TODO: copy content from notes
