---
layout: page
title: Jobs
permalink: /jobs/
---

<table>
    <colgroup>
        <col width="10%" />
        <col width="10%" />
        <col width="20%" />
        <col width="50%" />
    </colgroup>
    <thead>
        <tr class="header">
            <th>Date</th>
            <th>Site</th>
            <th>Company</th>
            <th>Title</th>
        </tr>
    </thead>
    <tbody>
    {% for job in site.data %}
        {% assign job_site = job[0] %}
        {% assign jobs = job[1] %}
        {% for job in jobs %}
            <tr>
            <td markdown="span">{{ job.posted | date: "%d %b" }}</td>
            <td markdown="span">{{ job_site | capitalize }}</td>
            <td markdown="span">{{ job.company }}</td>
            <td markdown="span">[{{ job.title }}]({{ job.url }})</td>
            </tr>
        {% endfor %}
    {% endfor %}
    </tbody>
</table>
