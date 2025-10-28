-- Create sequence {{ sequence.owner }}.{{ sequence.name }}
CREATE SEQUENCE {{ sequence.owner }}.{{ sequence.name }}
    START WITH {{ sequence.start_with }}
    INCREMENT BY {{ sequence.increment_by }}
{%- if sequence.min_value is not none %}
    MINVALUE {{ sequence.min_value }}
{%- else %}
    NOMINVALUE
{%- endif %}
{%- if sequence.max_value is not none %}
    MAXVALUE {{ sequence.max_value }}
{%- else %}
    NOMAXVALUE
{%- endif %}
    CACHE {{ sequence.cache_size }}
{%- if sequence.cycle %}
    CYCLE
{%- else %}
    NOCYCLE
{%- endif %};

{%- if sequence.comment %}

COMMENT ON SEQUENCE {{ sequence.owner }}.{{ sequence.name }} IS '{{ sequence.comment }}';
{%- endif %}