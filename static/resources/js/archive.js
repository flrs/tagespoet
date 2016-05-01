var csrftoken = $('meta[name=csrf-token]').attr('content');

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken)
        }
    }
});

$('#archive_date').text(moment('{{ last_poem_date_heading }}').format('Do MMMM YYYY'));

$('#sandbox-container div').datepicker({
    format: "dd.mm.yyyy",
    endDate: "{{ last_poem_date }}",
    startDate: "{{ first_poem_date }}",
    language: "de"
}).on('changeDate', function(ev) {
    ga('send', 'event', 'Archive', 'get', ev.date.toUTCString());
    $.getJSON('/_get_archived_poem', {
            date: ev.date.toUTCString()
        },
        function(data) {
            $('#archive_keywords').fadeOut('fast',
                function() {
                    $('#archive_keywords').html(data.keywords).fadeIn('fast');
                });
            $('#archive_date').fadeOut('fast',
                function() {
                    $('#archive_date').text(moment(data.timestamp).format('Do MMMM YYYY')).fadeIn('fast');
                });
            $('#archive_poem').fadeOut('fast',
                function() {
                    $('#archive_poem').html(data.poem).fadeIn('fast');
                });
        });
});
