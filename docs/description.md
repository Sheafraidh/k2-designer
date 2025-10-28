# DB Designer #

## Description ##
Simple python application for creating database ER diagrams and generating SQL and various other scripts based on the database model.

## Technical specification ##

### Layout ###
Object browser to the left (a tree view with users, tables, etc.), properties to the right (table name, descriptions, columns, etc.), drawing pane in the middle (with context menu).

### Data structure ###
Domain (for used datatypes, doesn't rely on the schema)
- name
- data type
- comment

Owner
- name
- default tablespace
- temp tablespace
- default index tablespace
- editionable

Table
- owner
- name
- tablespace (default from owner's tablespace)
- comment
- stereotype (business, technical)
- color (based on stereotype, or overriden)
- domain (if used)
- editionable
- columns
    - name
    - data type
    - nullable
    - comment
    - default (can be from existing sequence)
- keys
    - key name
    - column list
- indexes
    - index name
    - index list
    - tablespace
- partitioning
    - partition columns
    - type (range/list)

Sequence
- owner
- name
- attributes

### Actions ###

- Create new project
- Open project
- Save project
- Save project as

Add new domain
Edit domain
Delete domain (delete all references on the columns)

Add new sequence
Edit sequence
Delete sequence

Add new user (schema).
Edit user (using properties).
Delete user (with all objects).

Add and define new table.
Edit table (using properties).
Delete table.

Draw connection between tables (for foreign keys).

Generate window with selection of scripts to generate.

Reverse engineer window with connection specification


### Used libraries ###
Graphics based on Qt6 library.
Database connection using oracledb library (at first).
Templating for the scripts based on jinja2.
Saving the project based on sqlite.


## Additional info ###

Possibility to connect to a database using oracledb library to reverse engineer the data model.

Class design capability oriented and scalable, so I can add other database engines as well, script creation scalable also, as I can define e.g. create table script, drop table script, stored type based on the columns from the table etc.

