||Suite name||Suite Version||Suite Documentation||
| {{ suite.name|safe|escape }} | {{ suite.versions|safe|escape }} | {{ suite.doc|safe|escape }} |
{% if suite.inits %}|Arguments||Documentation||
{% for init in suite.inits %} | {{ init.args|safe|escape }} | {{ init.doc|safe|escape }} |
{% endfor %}{% endif %}
||Variables||
||Name||Value||Comment||
{% for vr in suite.variables %}| {{ vr.name|safe|escape }} | {{ vr.value|safe|escape }} | {{ vr.comment|safe|escape }} |
{% endfor %}
||Test Cases||
||Test case||Documentation||
{% for tc in suite.tests %}| {{ tc.name|safe|escape }} | {{ tc.doc|safe|escape }} |
{% endfor %}
||Keywords||
||Keyword||Arguments||Documentation||
{% for kw in suite.keywords %}| {{ kw.name|safe|escape }} | {{ kw.args|safe|escape }} | {{ kw.doc|safe|escape }} |
{% endfor %}
