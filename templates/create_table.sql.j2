-- Create table {{ table.owner }}.{{ table.name }}
CREATE TABLE {{ table.owner }}.{{ table.name }} (
{%- for column in table.columns %}
    {{ column.name }} {{ column.data_type }}{% if not column.nullable %} NOT NULL{% endif %}{% if column.default %} DEFAULT {{ column.default }}{% endif %}{% if not loop.last %},{% endif %}
{%- endfor %}
){% if table.tablespace %} TABLESPACE {{ table.tablespace }}{% endif %};

{%- if table.comment %}

COMMENT ON TABLE {{ table.owner }}.{{ table.name }} IS '{{ table.comment }}';
{%- endif %}

{%- for column in table.columns %}
{%- if column.comment %}
COMMENT ON COLUMN {{ table.owner }}.{{ table.name }}.{{ column.name }} IS '{{ column.comment }}';
{%- endif %}
{%- endfor %}

{%- for key in table.keys %}

ALTER TABLE {{ table.owner }}.{{ table.name }} ADD CONSTRAINT {{ key.name }} PRIMARY KEY ({{ key.columns | join(', ') }});
{%- endfor %}

{%- for index in table.indexes %}

CREATE INDEX {{ index.name }} ON {{ table.owner }}.{{ table.name }} ({{ index.columns | join(', ') }}){% if index.tablespace %} TABLESPACE {{ index.tablespace }}{% endif %};
{%- endfor %}