function genCalendar(id, path) {
   $(document).ready(function () {
       var calendar = $(`#${id}`).fullCalendar({
           header: {
               left: 'prev,next today',
               center: 'title',
               right: 'month,agendaWeek,agendaDay'
           },
           events: `${path}`,
           selectable: true,
           selectHelper: false,
           editable: false,
           eventLimit: true,
           lang: 'ru',
           themeSystem: 'bootstrap5',
       });
   });
}