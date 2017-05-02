---
layout: page
title: Jobs
permalink: /jobs/
---

<ul>
  {% for job in site.data %}
    {% assign job_site = job[0] %}
    {% assign jobs = job[1] %}
    {% for job in jobs %}
    <li>
      <a href="{{ job.url }}">
        {{ job_site }}: {{ job.company }} - {{ job.title }}
      </a>
    </li>
    {% endfor %}
  {% endfor %}
</ul>
