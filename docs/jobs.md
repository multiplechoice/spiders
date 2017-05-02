---
layout: page
title: Jobs
permalink: /jobs/
---
<!-- jQuery (necessary for Bootstrap's JavaScript plugins) -->
<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.4/jquery.min.js"></script>

<!-- Latest compiled and minified CSS -->
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">

<!-- Optional theme -->
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap-theme.min.css" integrity="sha384-rHyoN1iRsVXV4nD0JutlnGaslCJuC7uwjduW9SVrLvRYooPp2bWYgmgJQIXwl/Sp" crossorigin="anonymous">

<!-- Latest compiled and minified JavaScript -->
<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js" integrity="sha384-Tc5IQib027qvyjSMfHjOMaLkfuWVxZxUPnCJA7l2mCWNIpG9mGCD8wGNIcPD7Txa" crossorigin="anonymous"></script>

<!-- Table sorting -->
<link rel="stylesheet" type="text/css" href="//cdn.datatables.net/1.10.15/css/jquery.dataTables.css">
<script type="text/javascript" charset="utf8" src="//cdn.datatables.net/1.10.15/js/jquery.dataTables.js"></script>

<table id="jobs" class="display ">
    <colgroup>
        <col width="15%" />
        <col width="10%" />
        <col width="20%" />
        <col width="45%" />
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
            <td markdown="span">{{ job.posted }}</td>
            <td markdown="span">{{ job_site | capitalize }}</td>
            <td markdown="span">{{ job.company }}</td>
            <td markdown="span">[{{ job.title }}]({{ job.url }})</td>
            </tr>
        {% endfor %}
    {% endfor %}
    </tbody>
</table>

<script type="text/javascript">
    $(document).ready(function() {
    $('#jobs').DataTable( {
        "order":    [[ 0, 'desc' ], [ 1, 'asc' ]],
        "paging":   false,
        "info":     false

    } );
} );
</script>