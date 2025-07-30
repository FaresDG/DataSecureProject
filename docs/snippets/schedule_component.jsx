import React, { useRef, useEffect } from 'react';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
// Tailwind CSS classes are used for spacing and layout.
import './schedule.css';

export default function Schedule({ events, onEventAdd, onEventChange }) {
  const calendarRef = useRef(null);

  useEffect(() => {
    let calendarApi = calendarRef.current.getApi();
    calendarApi.render();
  }, []);

  return (
    <div className="schedule-container p-4 bg-white rounded shadow">
      <FullCalendar
        ref={calendarRef}
        plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
        initialView="timeGridWeek"
        headerToolbar={{
          left: 'prev,next today',
          center: 'title',
          right: 'dayGridMonth,timeGridWeek,timeGridDay'
        }}
        events={events}
        nowIndicator={true}
        editable={true}
        selectable={true}
        eventAdd={onEventAdd}
        eventChange={onEventChange}
        height="auto"
      />
    </div>
  );
}
