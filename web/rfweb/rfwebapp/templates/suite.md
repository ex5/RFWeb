||Suite name||Suite Version||Suite Documentation||
|{{ suite.name }} |{{ suite.versions }} |{{ suite.doc }} |
{% if suite.inits %}|Arguments||Documentation||
{% for init in suite.inits %} |{{ init.args }} |{{ init.doc }} |
{% endfor %}{% endif %}
||Variables||
||Name||Value||Comment||
{% for vr in suite.variables %}|{{ vr.name }} |{{ vr.value }} |{{ vr.comment }} |
{% endfor %}
||Test Cases||
||Test case||Documentation||
{% for tc in suite.tests %}|{{ tc.name }} |{{ tc.doc }} |
{% endfor %}
||Keywords||
||Keyword||Arguments||Documentation||
{% for kw in suite.keywords %}|{{ kw.name }} |{{ kw.args }} |{{ kw.doc }} |
{% endfor %}
