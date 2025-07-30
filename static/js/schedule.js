// Schedule calendar initialization using FullCalendar
// Requires a div with id 'scheduleCalendar' and a data-events attribute

function initScheduleCalendar() {
  var calendarEl = document.getElementById('scheduleCalendar');
  if (!calendarEl) return;

  var eventsData = [];
  try {
    eventsData = JSON.parse(calendarEl.dataset.events || '[]');
  } catch (e) {
    console.error('Invalid schedule event data', e);
  }

  var calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: 'timeGridWeek',
    allDaySlot: false,
    headerToolbar: {
      left: 'prev,next today',
      center: 'title',
      right: 'timeGridWeek,timeGridDay'
    },
    height: 'auto',
    slotMinTime: '07:00:00',
    slotMaxTime: '19:00:00',
    events: eventsData
  });

  calendar.render();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initScheduleCalendar);
} else {
  initScheduleCalendar();
}
