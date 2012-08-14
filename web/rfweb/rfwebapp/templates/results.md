{% if results %}||task||start||finish||uid||status||report||
{% for result in results %}|{{ result.task }} |{{ result.start }} |{{ result.finish }} |{{ result.uid }} |{{ result.status }} |{{ result.results_name }} |
{% endfor %}{% endif %}
