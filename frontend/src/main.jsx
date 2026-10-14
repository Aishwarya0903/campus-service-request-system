import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';

const API =
  import.meta.env.VITE_API_URL ||
  'http://localhost:8000';

const DEMO_PASSWORD = 'winter@123';

const SERVICES = [
  {
    key: 'Electrical',
    icon: '⚡',
    title: 'Electrical',
    description:
      'Power, lighting, fans, AC units, switches and electrical maintenance.'
  },
  {
    key: 'Plumbing',
    icon: '🔧',
    title: 'Plumbing',
    description:
      'Water supply, leakage, drainage, taps, pipes and washroom issues.'
  },
  {
    key: 'IT/Network',
    icon: '🌐',
    title: 'IT / Network',
    description:
      'Wi-Fi, network connectivity, computers, software and technical issues.'
  },
  {
    key: 'Hostel',
    icon: '🏠',
    title: 'Hostel',
    description:
      'Room maintenance, furniture, common areas and hostel facilities.'
  }
];


/* =========================================================
   API HELPER
========================================================= */

async function call(path, method = 'GET', body) {
  const token = localStorage.getItem('token');

  const response = await fetch(API + path, {
    method,

    headers: {
      ...(body !== undefined
        ? {
            'Content-Type': 'application/json'
          }
        : {}),

      ...(token
        ? {
            Authorization: `Bearer ${token}`
          }
        : {})
    },

    body:
      body !== undefined
        ? JSON.stringify(body)
        : undefined
  });

  if (!response.ok) {
    let data = {};

    try {
      data = await response.json();
    } catch {}

    const error = new Error(
      data.detail ||
      `Request failed (${response.status})`
    );

    error.status = response.status;

    throw error;
  }

  return response.json();
}


function formatDate(value) {
  if (!value) return '—';

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString();
}


/* =========================================================
   PORTAL HEADER / FOOTER
========================================================= */

function PortalTopbar({
  theme,
  setTheme,
  onBrandClick
}) {
  return (
    <div className="portal-topbar">

      <button
        type="button"
        className="center-brand"
        onClick={onBrandClick || (() => {})}
      >
        <div className="brand-mark">
          CS
        </div>

        <div>
          <strong>
            Campus Service Desk
          </strong>

          <span>
            Campus Services Portal
          </span>
        </div>
      </button>

      <button
        type="button"
        className="theme-toggle"
        onClick={() =>
          setTheme(
            theme === 'light'
              ? 'dark'
              : 'light'
          )
        }
      >
        {theme === 'light'
          ? '🌙 Dark'
          : '☀️ Light'}
      </button>

    </div>
  );
}


function PortalFooter() {
  return (
    <footer className="portal-footer">
      <span>
        AI-Powered Campus Service Request System
      </span>

      <span>
        Campus Support Portal
      </span>
    </footer>
  );
}


function PortalSelectionCard({
  icon,
  title,
  description,
  onClick
}) {
  return (
    <button
      type="button"
      className="portal-selection-card"
      onClick={onClick}
    >
      <div className="selection-icon">
        {icon}
      </div>

      <div>
        <h2>{title}</h2>

        <p>
          {description}
        </p>
      </div>

      <span className="portal-arrow">
        →
      </span>
    </button>
  );
}


/* =========================================================
   LOGIN
========================================================= */

function Login({ onLogin }) {
  const [selectedPortal, setSelectedPortal] =
    useState(null);

  const [email, setEmail] =
    useState('');

  const [password, setPassword] =
    useState('');

  const [showPassword, setShowPassword] =
    useState(false);

  const [error, setError] =
    useState('');

  const [loading, setLoading] =
    useState(false);

  const [theme, setTheme] =
    useState(
      localStorage.getItem('theme') ||
      'light'
    );


  useEffect(() => {
    document.documentElement.setAttribute(
      'data-theme',
      theme
    );

    localStorage.setItem(
      'theme',
      theme
    );
  }, [theme]);


  function selectPortal(role) {
    setSelectedPortal(role);
    setError('');

    if (role === 'student') {
      setEmail('22MIS0281');
      setPassword('winter@123');
    }

    if (role === 'staff') {
      setEmail('STFEL001');
      setPassword('elena@123');
    }

    if (role === 'admin') {
      setEmail('ADM001');
      setPassword('admin@123');
    }
  }


  function goBack() {
    setSelectedPortal(null);
    setEmail('');
    setPassword('');
    setError('');
  }


  async function submit(event) {
    event.preventDefault();

    setError('');
    setLoading(true);

    try {
      const result = await call(
        '/auth/login',
        'POST',
        {
          email: email.trim(),
          password,
        portal: selectedPortal
        }
      );

      if (!result.access_token) {
        throw new Error(
          'Login succeeded but no access token was returned.'
        );
      }

      localStorage.setItem(
        'token',
        result.access_token
      );

      /*
       * IMPORTANT:
       * Pass the complete login result directly
       * to App. App will immediately render the
       * correct portal and then load dashboard data.
       */
      await onLogin({
        id: result.id || null,
        name:
          result.name ||
          email.split('@')[0],
        email:
          result.email ||
          email,
        role:
          result.role,
        department:
          result.department || null
      });

    } catch (loginError) {
      console.error(
        'LOGIN ERROR:',
        loginError
      );

      localStorage.removeItem('token');

      setError(
        loginError.message ||
        'Login failed.'
      );

    } finally {
      setLoading(false);
    }
  }


  if (selectedPortal === 'services') {
    return (
      <main className="portal-login-page">

        <PortalTopbar
          theme={theme}
          setTheme={setTheme}
          onBrandClick={goBack}
        />

        <div className="services-page">

          <button
            type="button"
            className="back-portal"
            onClick={goBack}
          >
            ← Back to Campus Portal
          </button>

          <div className="services-heading">

            <span className="portal-label">
              CAMPUS SERVICES
            </span>

            <h1>
              How Can We Help You?
            </h1>

            <p>
              Explore the different service areas
              available across campus.
            </p>

          </div>

          <div className="service-detail-grid">

            {SERVICES.map(service => (
              <article
                className="service-detail-card"
                key={service.key}
              >
                <div className="service-detail-icon">
                  {service.icon}
                </div>

                <h2>
                  {service.title}
                </h2>

                <p>
                  {service.description}
                </p>

                <div className="service-example-list">
                  <span>✓ Campus support</span>
                  <span>✓ Request tracking</span>
                  <span>✓ Staff assignment</span>
                  <span>✓ SLA monitoring</span>
                </div>
              </article>
            ))}

          </div>

          <div className="services-help-box">

            <div className="services-help-icon">
              💡
            </div>

            <div>
              <strong>
                Need to report an issue?
              </strong>

              <p>
                Sign in through the Student Portal
                to submit and track your request.
              </p>
            </div>

            <button
              type="button"
              onClick={() =>
                selectPortal('student')
              }
            >
              Student Portal →
            </button>

          </div>

        </div>

        <PortalFooter />

      </main>
    );
  }


  if (!selectedPortal) {
    return (
      <main className="portal-login-page">

        <PortalTopbar
          theme={theme}
          setTheme={setTheme}
        />

        <div className="portal-home">

          <div className="portal-heading">

            <span className="portal-label">
              CAMPUS PORTAL
            </span>

            <h1>
              Welcome to Campus Services
            </h1>

            <p>
              Select your portal to continue.
            </p>

          </div>

          <div className="portal-selection-grid">

            <PortalSelectionCard
              icon="🎓"
              title="Student"
              description="Submit and track campus service requests."
              onClick={() =>
                selectPortal('student')
              }
            />

            <PortalSelectionCard
              icon="👨‍💼"
              title="Staff"
              description="Manage department service requests and resolutions."
              onClick={() =>
                selectPortal('staff')
              }
            />

            <PortalSelectionCard
              icon="🛡️"
              title="Administrator"
              description="Monitor analytics, users and SLA performance."
              onClick={() =>
                selectPortal('admin')
              }
            />

            <PortalSelectionCard
              icon="🏫"
              title="Campus Services"
              description="Explore electrical, plumbing, IT/network and hostel support."
              onClick={() =>
                setSelectedPortal('services')
              }
            />

          </div>

          <div className="portal-services-strip">

            {SERVICES.map(service => (
              <div key={service.key}>
                <span>
                  {service.icon}
                </span>

                {service.title}
              </div>
            ))}

          </div>

        </div>

        <PortalFooter />

      </main>
    );
  }


  const portalInfo = {
    student: {
      title: 'Student Portal',
      icon: '🎓',
      subtitle:
        'Sign in to access student campus services.'
    },

    staff: {
      title: 'Staff Portal',
      icon: '👨‍💼',
      subtitle:
        'Sign in to manage your department requests.'
    },

    admin: {
      title: 'Administrator Portal',
      icon: '🛡️',
      subtitle:
        'Sign in to access administration controls.'
    }
  };


  const info =
    portalInfo[selectedPortal];


  return (
    <main className="portal-login-page">

      <PortalTopbar
        theme={theme}
        setTheme={setTheme}
        onBrandClick={goBack}
      />

      <div className="portal-login-area">

        <button
          type="button"
          className="back-portal"
          onClick={goBack}
        >
          ← Back to Campus Portal
        </button>

        <section className="portal-login-card">

          <div className="login-portal-icon">
            {info.icon}
          </div>

          <span className="portal-label">
            {selectedPortal.toUpperCase()} PORTAL
          </span>

          <h1>
            {info.title}
          </h1>

          <p className="login-description">
            {info.subtitle}
          </p>

          <form
            onSubmit={submit}
            className="portal-login-form"
          >

            <label>
              {selectedPortal === 'student' ? 'Registration Number' : selectedPortal === 'staff' ? 'Staff ID' : 'Admin ID'}

              <input
                type="text"
                value={email}
                onChange={event =>
                  setEmail(
                    event.target.value
                  )
                }
                placeholder={selectedPortal === 'student' ? 'Enter your registration number' : selectedPortal === 'staff' ? 'Enter your staff ID' : 'Enter your admin ID'}
                required
                disabled={loading}
              />
            </label>


            <label>
              Password

              <div className="password-wrapper">

                <input
                  type={
                    showPassword
                      ? 'text'
                      : 'password'
                  }
                  value={password}
                  onChange={event =>
                    setPassword(
                      event.target.value
                    )
                  }
                  placeholder="Enter your password"
                  required
                  disabled={loading}
                />

                <button
                  type="button"
                  className="password-toggle"
                  onClick={() =>
                    setShowPassword(
                      previous =>
                        !previous
                    )
                  }
                  disabled={loading}
                >
                  {showPassword
                    ? '🙈'
                    : '👁️'}
                </button>

              </div>

            </label>


            <div className="login-options">

              <label className="remember-option">
                <input type="checkbox" />
                Remember me
              </label>

              <button
                type="button"
                className="forgot-button"
              >
                Forgot password?
              </button>

            </div>


            <button
              type="submit"
              className="portal-signin"
              disabled={loading}
            >
              {loading
                ? 'Signing in...'
                : 'Sign In'}
            </button>


            {error && (
              <div className="login-error">
                {error}
              </div>
            )}

          </form>

        </section>

      </div>

      <PortalFooter />

    </main>
  );
}


/* =========================================================
   STUDENT DASHBOARD
========================================================= */

function StudentDashboard({
  user,
  tickets,
  notes,
  onServiceSelect,
  onScroll
}) {
  const total = tickets.length;

  const open =
    tickets.filter(ticket =>
      [
        'OPEN',
        'ASSIGNED',
        'IN_PROGRESS',
        'ESCALATED'
      ].includes(ticket.status)
    ).length;

  const resolved =
    tickets.filter(ticket =>
      [
        'RESOLVED',
        'CLOSED'
      ].includes(ticket.status)
    ).length;

  const highRisk =
    tickets.filter(ticket =>
      Number(ticket.risk_score || 0) >= 0.70 &&
      ![
        'RESOLVED',
        'CLOSED'
      ].includes(ticket.status)
    ).length;


  return (
    <>
      <section className="student-welcome">

        <div>

          <span className="portal-label">
            STUDENT PORTAL
          </span>

          <h1>
            Welcome, {user.name}
          </h1>

          <p>
            Submit campus service requests and
            track their progress from one place.
          </p>

        </div>

        <div className="student-profile-card">

          <div className="profile-avatar">
            {user.name?.charAt(0)?.toUpperCase() || 'S'}
          </div>

          <div>

            <strong>
              {user.name}
            </strong>

            <small>
              {user.email}
            </small>

          </div>

        </div>

      </section>


      <section className="student-stat-grid">

        <div className="student-stat-card">
          <span className="stat-icon">🎫</span>

          <div>
            <small>Total Requests</small>
            <strong>{total}</strong>
          </div>
        </div>

        <div className="student-stat-card">
          <span className="stat-icon">🔄</span>

          <div>
            <small>Active Requests</small>
            <strong>{open}</strong>
          </div>
        </div>

        <div className="student-stat-card">
          <span className="stat-icon">✅</span>

          <div>
            <small>Resolved</small>
            <strong>{resolved}</strong>
          </div>
        </div>

        <div className="student-stat-card">
          <span className="stat-icon">⏱️</span>

          <div>
            <small>High SLA Risk</small>
            <strong>{highRisk}</strong>
          </div>
        </div>

      </section>


      <section className="student-services-section">

        <div className="student-section-heading">

          <div>

            <span className="portal-label">
              CAMPUS SUPPORT
            </span>

            <h2>
              What do you need help with?
            </h2>

            <p>
              Select a service to start your request.
            </p>

          </div>

          <button
            type="button"
            className="secondary-action"
            onClick={() =>
              onScroll('service-request')
            }
          >
            View Request Form →
          </button>

        </div>


        <div className="student-service-grid">

          {SERVICES.map(service => (

            <button
              type="button"
              className="student-service-card"
              key={service.key}
              onClick={() =>
                onServiceSelect(
                  service.key
                )
              }
            >

              <div className="student-service-icon">
                {service.icon}
              </div>

              <div className="student-service-content">

                <h3>
                  {service.title}
                </h3>

                <p>
                  {service.description}
                </p>

              </div>

              <span className="service-card-arrow">
                →
              </span>

            </button>

          ))}

        </div>

      </section>


      <section className="student-quick-section">

        <button
          type="button"
          onClick={() =>
            onScroll('my-tickets')
          }
        >
          <span>📋</span>

          <div>
            <strong>My Tickets</strong>
            <small>
              Track your submitted requests
            </small>
          </div>

          <b>→</b>
        </button>


        <button
          type="button"
          onClick={() =>
            window.scrollTo({
              top: 0,
              behavior: 'smooth'
            })
          }
        >
          <span>🔔</span>

          <div>
            <strong>Notifications</strong>

            <small>
              {notes.length} recent update
              {notes.length === 1 ? '' : 's'}
            </small>
          </div>

          <b>→</b>
        </button>

      </section>

    </>
  );
}


/* =========================================================
   STUDENT REQUEST FORM
========================================================= */

function TicketForm({
  reload,
  selectedService,
  onServiceChange
}) {
  const [description, setDescription] =
    useState('');

  const [location, setLocation] =
    useState('');

  const [file, setFile] =
    useState(null);

  const [message, setMessage] =
    useState('');

  const [prediction, setPrediction] =
    useState(null);

  const [submitting, setSubmitting] =
    useState(false);


  async function submit(event) {
    event.preventDefault();

    setMessage('');
    setPrediction(null);
    setSubmitting(true);

    try {

      const ticket =
        await call(
          '/tickets',
          'POST',
          {
            description,
            location
          }
        );


      if (file) {

        const form =
          new FormData();

        form.append(
          'file',
          file
        );

        const response =
          await fetch(
            `${API}/tickets/${ticket.id}/attachment`,
            {
              method: 'POST',

              headers: {
                Authorization:
                  `Bearer ${localStorage.getItem('token')}`
              },

              body: form
            }
          );

        if (!response.ok) {
          let data = {};

          try {
            data =
              await response.json();
          } catch {}

          throw new Error(
            data.detail ||
            'Attachment upload failed'
          );
        }
      }


      setPrediction({
        category:
          ticket.category,

        priority:
          ticket.priority,

        risk_score:
          ticket.risk_score,

        risk_level:
          ticket.risk_level
      });


      setMessage(
        `Ticket #${ticket.id} was submitted successfully.`
      );

      setDescription('');
      setLocation('');
      setFile(null);

      await reload();

    } catch (error) {

      setMessage(
        error.message
      );

    } finally {

      setSubmitting(false);
    }
  }


  return (
    <section
      className="student-request-section"
      id="service-request"
    >

      <div className="request-heading">

        <div>

          <span className="portal-label">
            NEW REQUEST
          </span>

          <h2>
            Submit a Service Request
          </h2>

          <p>
            Tell us what is wrong and our AI system
            will automatically classify the request.
          </p>

        </div>

      </div>


      <form
        className="request"
        onSubmit={submit}
      >

        <label>
          Service Area

          <select
            value={selectedService}
            onChange={event =>
              onServiceChange(
                event.target.value
              )
            }
          >
            <option value="">
              Select a service area
            </option>

            {SERVICES.map(service => (
              <option
                value={service.key}
                key={service.key}
              >
                {service.title}
              </option>
            ))}
          </select>
        </label>


        <label>
          Description

          <textarea
            required
            minLength={10}
            value={description}
            onChange={event =>
              setDescription(
                event.target.value
              )
            }
            placeholder={
              selectedService
                ? `Describe your ${selectedService} issue...`
                : 'Describe your campus issue clearly...'
            }
          />
        </label>


        <label>
          Location

          <input
            required
            value={location}
            onChange={event =>
              setLocation(
                event.target.value
              )
            }
            placeholder="e.g. Hostel Block A, Room 312"
          />
        </label>


        <label>
          Optional Photo

          <input
            type="file"
            accept="image/png,image/jpeg"
            onChange={event =>
              setFile(
                event.target.files?.[0] || null
              )
            }
          />

          {file && (
            <small>
              Selected: {file.name}
            </small>
          )}
        </label>


        <button
          type="submit"
          disabled={submitting}
        >
          {submitting
            ? 'Submitting...'
            : 'Submit Service Request'}
        </button>


        {message && (
          <div className="request-message">
            {message}
          </div>
        )}


        {prediction && (
          <div className="prediction-result">

            <div className="prediction-title">
              🤖 AI Request Analysis
            </div>

            <div className="prediction-grid">

              <div>
                <small>
                  Predicted Category
                </small>

                <strong>
                  {prediction.category}
                </strong>
              </div>

              <div>
                <small>
                  Predicted Priority
                </small>

                <strong>
                  {prediction.priority}
                </strong>
              </div>

              <div>
                <small>
                  SLA Risk
                </small>

                <strong>
                  {Math.round(
                    Number(
                      prediction.risk_score || 0
                    ) * 100
                  )}%
                </strong>
              </div>

            </div>

          </div>
        )}

      </form>

    </section>
  );
}


/* =========================================================
   STAFF DASHBOARD
========================================================= */

function StaffDashboard({
  tickets,
  user,
  onScroll
}) {
  const total =
    tickets.length;

  const open =
    tickets.filter(ticket =>
      [
        'OPEN',
        'ESCALATED'
      ].includes(ticket.status)
    ).length;

  const assigned =
    tickets.filter(ticket =>
      ticket.status === 'ASSIGNED'
    ).length;

  const inProgress =
    tickets.filter(ticket =>
      ticket.status === 'IN_PROGRESS'
    ).length;

  const resolved =
    tickets.filter(ticket =>
      [
        'RESOLVED',
        'CLOSED'
      ].includes(ticket.status)
    ).length;

  const highRisk =
    tickets.filter(ticket =>
      Number(ticket.risk_score || 0) >= 0.70 &&
      ![
        'RESOLVED',
        'CLOSED'
      ].includes(ticket.status)
    ).length;


  return (
    <section
      className="staff-dashboard"
      id="staff-overview"
    >

      <div className="staff-welcome">

        <div>

          <span className="portal-label">
            STAFF OPERATIONS
          </span>

          <h1>
            Welcome, {user.name}
          </h1>

          <p>
            Manage your department's campus
            service requests and SLA performance.
          </p>

        </div>

        <div className="staff-department">

          <div className="department-icon">
            🏢
          </div>

          <div>
            <small>
              Department
            </small>

            <strong>
              {user.department ||
                'Department Staff'}
            </strong>
          </div>

        </div>

      </div>


      <div className="metrics">

        <article>
          <small>Total Tickets</small>
          <strong>{total}</strong>
        </article>

        <article>
          <small>Open</small>
          <strong>{open}</strong>
        </article>

        <article>
          <small>Assigned</small>
          <strong>{assigned}</strong>
        </article>

        <article>
          <small>In Progress</small>
          <strong>{inProgress}</strong>
        </article>

        <article>
          <small>Resolved</small>
          <strong>{resolved}</strong>
        </article>

        <article>
          <small>High SLA Risk</small>
          <strong>{highRisk}</strong>
        </article>

      </div>


      <section className="analytics-card">

        <div className="staff-card-heading">

          <div>
            <h3>
              Department Overview
            </h3>

            <p className="subtitle">
              Current service request workload.
            </p>
          </div>

          <button
            type="button"
            className="small-action"
            onClick={() =>
              onScroll('staff-tickets')
            }
          >
            View Tickets →
          </button>

        </div>

        <div className="metrics">

          <article>
            <small>
              Active
            </small>

            <strong>
              {open +
                assigned +
                inProgress}
            </strong>
          </article>

          <article>
            <small>
              High Risk
            </small>

            <strong>
              {highRisk}
            </strong>
          </article>

          <article>
            <small>
              Completed
            </small>

            <strong>
              {resolved}
            </strong>
          </article>

        </div>

      </section>

    </section>
  );
}


/* =========================================================
   TICKET TABLE
========================================================= */

function TicketTable({
  tickets,
  staff,
  reload,
  user,
  id
}) {
  const [query, setQuery] =
    useState('');

  const [editing, setEditing] =
    useState(null);

  const [statusValue, setStatusValue] =
    useState('');

  const [resolutionNotes, setResolutionNotes] =
    useState('');

  const [saving, setSaving] =
    useState(false);

  const [message, setMessage] =
    useState('');


  const rows =
    tickets.filter(ticket =>
      JSON.stringify(ticket)
        .toLowerCase()
        .includes(
          query.toLowerCase()
        )
    );


  function startEdit(ticket) {
    setEditing(ticket.id);

    setStatusValue(
      ticket.status
    );

    setResolutionNotes(
      ticket.resolution_notes || ''
    );

    setMessage('');
  }


  async function saveUpdate(
    ticketId,
    forcedStatus = null
  ) {
    try {

      setSaving(true);
      setMessage('');

      const payload = {
        status:
          forcedStatus ||
          statusValue,

        resolution_notes:
          resolutionNotes || undefined
      };


      /*
       * Only send assigned_staff_id when
       * a real user ID exists.
       */
      if (
        (user.role === 'STAFF' ||
          user.role === 'ADMIN') &&
        user.id
      ) {
        payload.assigned_staff_id =
          user.id;
      }


      await call(
        `/tickets/${ticketId}`,
        'PATCH',
        payload
      );


      setMessage(
        `Ticket #${ticketId} updated successfully.`
      );

      setEditing(null);

      await reload();

    } catch (error) {

      setMessage(
        error.message
      );

    } finally {

      setSaving(false);
    }
  }


  return (
    <section
      className="table-section"
      id={
        id ||
        (
          staff
            ? 'staff-tickets'
            : 'my-tickets'
        )
      }
    >

      <div className="table-section-heading">

        <div>

          <span className="portal-label">
            {staff
              ? 'DEPARTMENT WORK QUEUE'
              : 'REQUEST HISTORY'}
          </span>

          <h2>
            {staff
              ? 'Department Tickets'
              : 'My Tickets'}
          </h2>

          <p>
            {staff
              ? 'Review and manage service requests assigned to your department.'
              : 'Track the status, priority and SLA risk of your service requests.'}
          </p>

        </div>

        <div className="ticket-count">
          {tickets.length} Ticket
          {tickets.length === 1 ? '' : 's'}
        </div>

      </div>


      <input
        className="search"
        placeholder="Search tickets..."
        value={query}
        onChange={event =>
          setQuery(
            event.target.value
          )
        }
      />


      {message && (
        <p className="table-message">
          {message}
        </p>
      )}


      {rows.length === 0 ? (

        <div className="empty-state">

          <div className="empty-icon">
            🎫
          </div>

          <strong>
            No tickets found
          </strong>

          <p>
            Service requests will appear here.
          </p>

        </div>

      ) : (

        <div className="table">

          <table>

            <thead>

              <tr>

                <th>ID</th>
                <th>Request</th>
                <th>Category</th>
                <th>Priority</th>
                <th>Status</th>
                <th>SLA Risk</th>

                {staff && (
                  <th>
                    Action
                  </th>
                )}

              </tr>

            </thead>


            <tbody>

              {rows.map(ticket => (

                <React.Fragment
                  key={ticket.id}
                >

                  <tr>

                    <td>
                      <strong>
                        #{ticket.id}
                      </strong>
                    </td>


                    <td>

                      <strong>
                        {ticket.description}
                      </strong>

                      <small>
                        📍 {ticket.location}
                      </small>

                      <small>
                        {formatDate(
                          ticket.created_at
                        )}
                      </small>

                    </td>


                    <td>
                      {ticket.category}
                    </td>


                    <td>
                      <span
                        className={
                          `badge ${ticket.priority}`
                        }
                      >
                        {ticket.priority}
                      </span>
                    </td>


                    <td>
                      <span
                        className={
                          `badge ${ticket.status}`
                        }
                      >
                        {ticket.status}
                      </span>
                    </td>


                    <td>

                      <span className="risk-badge">
                        {Math.round(
                          Number(
                            ticket.risk_score || 0
                          ) * 100
                        )}%
                      </span>

                    </td>


                    {staff && (
                      <td>

                        <button
                          type="button"
                          onClick={() =>
                            startEdit(ticket)
                          }
                        >
                          Update
                        </button>

                      </td>
                    )}

                  </tr>


                  {staff &&
                    editing === ticket.id && (

                    <tr>

                      <td colSpan="7">

                        <div className="ticket-editor">

                          <h3>
                            Manage Ticket #
                            {ticket.id}
                          </h3>


                          <p>
                            Assigned Staff:{' '}
                            {ticket.assigned_staff ||
                              'Not assigned'}
                          </p>


                          <button
                            type="button"
                            onClick={() =>
                              saveUpdate(
                                ticket.id,
                                'ASSIGNED'
                              )
                            }
                            disabled={saving}
                          >
                            {saving
                              ? 'Saving...'
                              : 'Assign to Me'}
                          </button>


                          <label>
                            Status

                            <select
                              value={
                                statusValue
                              }
                              onChange={event =>
                                setStatusValue(
                                  event.target.value
                                )
                              }
                            >

                              <option value="OPEN">
                                OPEN
                              </option>

                              <option value="ASSIGNED">
                                ASSIGNED
                              </option>

                              <option value="IN_PROGRESS">
                                IN_PROGRESS
                              </option>

                              <option value="RESOLVED">
                                RESOLVED
                              </option>

                              <option value="CLOSED">
                                CLOSED
                              </option>

                              <option value="ESCALATED">
                                ESCALATED
                              </option>

                            </select>

                          </label>


                          <label>
                            Resolution Notes

                            <textarea
                              rows="4"
                              value={
                                resolutionNotes
                              }
                              onChange={event =>
                                setResolutionNotes(
                                  event.target.value
                                )
                              }
                              placeholder="Enter resolution details..."
                            />

                          </label>


                          <button
                            type="button"
                            onClick={() =>
                              saveUpdate(
                                ticket.id
                              )
                            }
                            disabled={saving}
                          >
                            {saving
                              ? 'Saving...'
                              : 'Save Update'}
                          </button>


                          <button
                            type="button"
                            onClick={() =>
                              setEditing(null)
                            }
                          >
                            Cancel
                          </button>

                        </div>

                      </td>

                    </tr>

                  )}

                </React.Fragment>

              ))}

            </tbody>

          </table>

        </div>

      )}

    </section>
  );
}


/* =========================================================
   ANALYTICS
========================================================= */

function AnalyticsList({
  title,
  entries
}) {
  return (
    <section className="analytics-card">

      <h3>
        {title}
      </h3>

      {entries.length === 0 ? (
        <p>
          No data available.
        </p>
      ) : (
        entries.map(
          ([name, count]) => (
            <div
              className="analytics-row"
              key={name}
            >
              <span>
                {name}
              </span>

              <strong>
                {count}
              </strong>
            </div>
          )
        )
      )}

    </section>
  );
}


function AdminAnalytics({
  stats
}) {
  return (
    <section
      className="admin-analytics"
      id="admin-analytics"
    >

      <div className="section-heading">

        <div>

          <span className="portal-label">
            ADMINISTRATION
          </span>

          <h2>
            Analytics Overview
          </h2>

        </div>

      </div>


      {!stats ? (

        <div className="analytics-card">

          <h3>
            Analytics data unavailable
          </h3>

          <p>
            Analytics could not be loaded.
          </p>

        </div>

      ) : (

        <>

          <div className="metrics">

            <article>
              <small>Total Tickets</small>
              <strong>
                {stats.total ?? 0}
              </strong>
            </article>

            <article>
              <small>Open Tickets</small>
              <strong>
                {stats.open ?? 0}
              </strong>
            </article>

            <article>
              <small>Resolved Tickets</small>
              <strong>
                {stats.resolved ?? 0}
              </strong>
            </article>

            <article>
              <small>Escalated Tickets</small>
              <strong>
                {stats.escalated ?? 0}
              </strong>
            </article>

            <article>
              <small>SLA Compliance</small>
              <strong>
                {stats.sla_compliance_rate ?? 0}%
              </strong>
            </article>

            <article>
              <small>Avg. Resolution</small>
              <strong>
                {stats.average_resolution_hours ?? 0}h
              </strong>
            </article>

          </div>


          <div className="analytics-grid">

            <AnalyticsList
              title="Tickets by Category"
              entries={Object.entries(
                stats.by_category || {}
              )}
            />

            <AnalyticsList
              title="Tickets by Priority"
              entries={Object.entries(
                stats.by_priority || {}
              )}
            />

            <AnalyticsList
              title="Tickets by Status"
              entries={Object.entries(
                stats.by_status || {}
              )}
            />

            <AnalyticsList
              title="Department Workload"
              entries={Object.entries(
                stats.department_workload || {}
              )}
            />

          </div>


          <section className="analytics-card">

            <h3>
              High SLA Risk Tickets
            </h3>

            {stats.high_risk?.length ? (

              <div className="table">

                <table>

                  <thead>

                    <tr>
                      <th>ID</th>
                      <th>Category</th>
                      <th>Priority</th>
                      <th>Status</th>
                      <th>Risk</th>
                    </tr>

                  </thead>

                  <tbody>

                    {stats.high_risk.map(
                      ticket => (

                        <tr
                          key={ticket.id}
                        >

                          <td>
                            #{ticket.id}
                          </td>

                          <td>
                            {ticket.category}
                          </td>

                          <td>
                            {ticket.priority}
                          </td>

                          <td>
                            {ticket.status}
                          </td>

                          <td>
                            {Math.round(
                              Number(
                                ticket.risk_score || 0
                              ) * 100
                            )}%
                          </td>

                        </tr>

                      )
                    )}

                  </tbody>

                </table>

              </div>

            ) : (
              <p>
                No high-risk tickets currently.
              </p>
            )}

          </section>

        </>

      )}

    </section>
  );
}


/* =========================================================
   ADMIN SLA
========================================================= */

function AdminSLA({
  rules,
  onReload
}) {
  const [localRules, setLocalRules] =
    useState([]);

  const [saving, setSaving] =
    useState(null);

  const [message, setMessage] =
    useState('');


  useEffect(() => {
    setLocalRules(
      Array.isArray(rules)
        ? rules
        : []
    );
  }, [rules]);


  function updateField(
    index,
    field,
    value
  ) {
    setLocalRules(
      previous =>
        previous.map(
          (rule, currentIndex) =>
            currentIndex === index
              ? {
                  ...rule,
                  [field]: value
                }
              : rule
        )
    );
  }


  async function saveRule(
    rule,
    index
  ) {
    try {

      setSaving(index);
      setMessage('');

      await call(
        `/sla/rules/${encodeURIComponent(
          rule.category
        )}`,
        'PUT',
        {
          hours:
            Number(rule.hours),

          risk_threshold:
            Number(rule.risk_threshold),

          grace_hours:
            Number(rule.grace_hours)
        }
      );

      setMessage(
        `${rule.category} SLA rule updated successfully.`
      );

      await onReload();

    } catch (error) {

      setMessage(
        error.message
      );

    } finally {

      setSaving(null);
    }
  }


  return (
    <section
      className="analytics-card"
      id="admin-sla"
    >

      <h2>
        SLA Configuration
      </h2>

      <p>
        Configure response time, risk threshold
        and escalation grace period.
      </p>


      {message && (
        <p>
          {message}
        </p>
      )}


      {localRules.length === 0 ? (

        <p>
          No SLA rules available.
        </p>

      ) : (

        <div className="table">

          <table>

            <thead>

              <tr>
                <th>Category</th>
                <th>SLA Hours</th>
                <th>Risk Threshold</th>
                <th>Grace Hours</th>
                <th>Action</th>
              </tr>

            </thead>


            <tbody>

              {localRules.map(
                (rule, index) => (

                  <tr
                    key={rule.category}
                  >

                    <td>
                      <strong>
                        {rule.category}
                      </strong>
                    </td>

                    <td>

                      <input
                        type="number"
                        min="1"
                        value={
                          rule.hours
                        }
                        onChange={event =>
                          updateField(
                            index,
                            'hours',
                            event.target.value
                          )
                        }
                      />

                    </td>

                    <td>

                      <input
                        type="number"
                        min="0"
                        max="1"
                        step="0.01"
                        value={
                          rule.risk_threshold
                        }
                        onChange={event =>
                          updateField(
                            index,
                            'risk_threshold',
                            event.target.value
                          )
                        }
                      />

                    </td>

                    <td>

                      <input
                        type="number"
                        min="0"
                        value={
                          rule.grace_hours
                        }
                        onChange={event =>
                          updateField(
                            index,
                            'grace_hours',
                            event.target.value
                          )
                        }
                      />

                    </td>

                    <td>

                      <button
                        type="button"
                        disabled={
                          saving === index
                        }
                        onClick={() =>
                          saveRule(
                            rule,
                            index
                          )
                        }
                      >
                        {saving === index
                          ? 'Saving...'
                          : 'Save'}
                      </button>

                    </td>

                  </tr>

                )
              )}

            </tbody>

          </table>

        </div>

      )}

    </section>
  );
}


/* =========================================================
   ADMIN USER MANAGEMENT
========================================================= */

function AdminUsers({
  users,
  onReload,
  currentUser
}) {
  const [localUsers, setLocalUsers] =
    useState([]);

  const [saving, setSaving] =
    useState(null);

  const [message, setMessage] =
    useState('');

  const [search, setSearch] =
    useState('');


  useEffect(() => {
    setLocalUsers(
      Array.isArray(users)
        ? users
        : []
    );
  }, [users]);


  function updateField(
    id,
    field,
    value
  ) {
    setLocalUsers(
      previous =>
        previous.map(
          item =>
            item.id === id
              ? {
                  ...item,
                  [field]: value
                }
              : item
        )
    );
  }


  async function saveUser(user) {
    try {

      setSaving(user.id);
      setMessage('');

      await call(
        `/admin/users/${user.id}`,
        'PATCH',
        {
          name:
            user.name,

          role:
            user.role,

          department:
            user.department || null,

          active:
            user.active
        }
      );

      setMessage(
        `${user.name}'s account was updated successfully.`
      );

      await onReload();

    } catch (error) {

      setMessage(
        error.message
      );

    } finally {

      setSaving(null);
    }
  }


  const filteredUsers =
    localUsers.filter(
      item =>
        `${item.name} ${item.email} ${item.role} ${item.department || ''}`
          .toLowerCase()
          .includes(
            search.toLowerCase()
          )
    );


  return (
    <section
      className="analytics-card"
      id="admin-users"
    >

      <div className="section-heading">

        <div>

          <h2>
            User Management
          </h2>

          <p>
            Manage campus accounts, roles,
            departments and account status.
          </p>

        </div>

        <strong>
          {localUsers.length} Users
        </strong>

      </div>


      <input
        className="search"
        placeholder="Search users..."
        value={search}
        onChange={event =>
          setSearch(
            event.target.value
          )
        }
      />


      {message && (
        <p>
          {message}
        </p>
      )}


      {filteredUsers.length === 0 ? (

        <p>
          No users found.
        </p>

      ) : (

        <div className="table">

          <table>

            <thead>

              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Role</th>
                <th>Department</th>
                <th>Status</th>
                <th>Action</th>
              </tr>

            </thead>


            <tbody>

              {filteredUsers.map(
                item => (

                  <tr
                    key={item.id}
                  >

                    <td>

                      <strong>
                        {item.name}
                      </strong>

                      {item.id ===
                        currentUser.id && (
                        <small>
                          Current account
                        </small>
                      )}

                    </td>


                    <td>
                      {item.email}
                    </td>


                    <td>

                      <select
                        value={
                          item.role
                        }
                        onChange={event =>
                          updateField(
                            item.id,
                            'role',
                            event.target.value
                          )
                        }
                      >

                        <option value="STUDENT">
                          STUDENT
                        </option>

                        <option value="STAFF">
                          STAFF
                        </option>

                        <option value="ADMIN">
                          ADMIN
                        </option>

                      </select>

                    </td>


                    <td>

                      <select
                        value={
                          item.department || ''
                        }
                        onChange={event =>
                          updateField(
                            item.id,
                            'department',
                            event.target.value ||
                              null
                          )
                        }
                      >

                        <option value="">
                          No Department
                        </option>

                        <option value="Electrical">
                          Electrical
                        </option>

                        <option value="Plumbing">
                          Plumbing
                        </option>

                        <option value="IT/Network">
                          IT/Network
                        </option>

                        <option value="Hostel">
                          Hostel
                        </option>

                      </select>

                    </td>


                    <td>

                      <select
                        value={
                          item.active
                            ? 'ACTIVE'
                            : 'INACTIVE'
                        }
                        disabled={
                          item.id ===
                          currentUser.id
                        }
                        onChange={event =>
                          updateField(
                            item.id,
                            'active',
                            event.target.value ===
                              'ACTIVE'
                          )
                        }
                      >

                        <option value="ACTIVE">
                          ACTIVE
                        </option>

                        <option value="INACTIVE">
                          INACTIVE
                        </option>

                      </select>

                    </td>


                    <td>

                      <button
                        type="button"
                        disabled={
                          saving ===
                          item.id
                        }
                        onClick={() =>
                          saveUser(
                            item
                          )
                        }
                      >
                        {saving === item.id
                          ? 'Saving...'
                          : 'Save'}
                      </button>

                    </td>

                  </tr>

                )
              )}

            </tbody>

          </table>

        </div>

      )}

    </section>
  );
}


/* =========================================================
   APP
========================================================= */

function App() {
  const [user, setUser] =
    useState(null);

  const [tickets, setTickets] =
    useState([]);

  const [notes, setNotes] =
    useState([]);

  const [stats, setStats] =
    useState(null);

  const [slaRules, setSlaRules] =
    useState([]);

  const [users, setUsers] =
    useState([]);

  const [selectedService, setSelectedService] =
    useState('');

  const [theme, setTheme] =
    useState(
      localStorage.getItem('theme') ||
      'light'
    );


  useEffect(() => {

    document.documentElement.setAttribute(
      'data-theme',
      theme
    );

    localStorage.setItem(
      'theme',
      theme
    );

  }, [theme]);


  /*
   * =======================================================
   * LOAD DASHBOARD DATA
   *
   * userOverride is essential immediately after login
   * because React state updates are asynchronous.
   * =======================================================
   */

  async function reload(userOverride = null) {

    const token =
      localStorage.getItem('token');

    if (!token) {
      return;
    }


    let currentUser =
      userOverride ||
      user;


    /*
     * Get complete user information.
     *
     * If this fails, KEEP the authenticated user.
     */
    try {

      const profile =
        await call('/users/me');

      currentUser = {
        ...(currentUser || {}),
        ...profile
      };

      setUser(currentUser);

    } catch (error) {

      console.error(
        'Profile loading failed:',
        error
      );

      /*
       * DO NOT LOG OUT.
       *
       * Login has already succeeded.
       */
    }


    if (!currentUser) {
      return;
    }


    /*
     * =====================================================
     * TICKETS
     * =====================================================
     */

    try {

      const data =
        await call('/tickets');

      setTickets(
        Array.isArray(data)
          ? data
          : []
      );

    } catch (error) {

      console.error(
        'Ticket loading failed:',
        error
      );

    }


    /*
     * =====================================================
     * NOTIFICATIONS
     * =====================================================
     */

    try {

      const data =
        await call('/notifications');

      setNotes(
        Array.isArray(data)
          ? data
          : []
      );

    } catch (error) {

      console.error(
        'Notification loading failed:',
        error
      );

    }


    /*
     * =====================================================
     * ADMIN DATA
     * =====================================================
     */

    if (
      currentUser.role ===
      'ADMIN'
    ) {

      try {

        const data =
          await call(
            '/analytics/overview'
          );

        setStats(data);

      } catch (error) {

        console.error(
          'Analytics loading failed:',
          error
        );

        setStats(null);
      }


      try {

        const data =
          await call(
            '/sla/rules'
          );

        setSlaRules(
          Array.isArray(data)
            ? data
            : []
        );

      } catch (error) {

        console.error(
          'SLA loading failed:',
          error
        );

        setSlaRules([]);
      }


      try {

        const data =
          await call(
            '/admin/users'
          );

        setUsers(
          Array.isArray(data)
            ? data
            : []
        );

      } catch (error) {

        console.error(
          'Admin users loading failed:',
          error
        );

        setUsers([]);
      }

    }
  }


  /*
   * =======================================================
   * LOGIN
   *
   * THIS IS THE IMPORTANT FIX.
   * =======================================================
   */

  async function handleLogin(loginUser) {

    /*
     * Establish the authenticated user immediately.
     */
    setUser(loginUser);

    /*
     * Immediately load all dashboard data.
     *
     * Pass loginUser explicitly because setUser()
     * does not update synchronously.
     */
    await reload(loginUser);
  }


  /*
   * =======================================================
   * RESTORE EXISTING SESSION
   * =======================================================
   */

  useEffect(() => {

    const token =
      localStorage.getItem('token');

    if (!token) {
      return;
    }


    async function restore() {

      try {

        const profile =
          await call(
            '/users/me'
          );

        setUser(profile);

        await reload(profile);

      } catch (error) {

        console.error(
          'Session restore failed:',
          error
        );

        /*
         * Only remove the token when the initial
         * session itself is invalid.
         */
        if (
          error.status === 401 ||
          error.status === 403
        ) {
          localStorage.removeItem(
            'token'
          );

          setUser(null);
        }

      }
    }


    restore();

  }, []);


  if (!user) {

    return (
      <Login
        onLogin={
          handleLogin
        }
      />
    );
  }


  const isStudent =
    user.role === 'STUDENT';

  const isStaff =
    user.role === 'STAFF';

  const isAdmin =
    user.role === 'ADMIN';


  function logout() {

    localStorage.removeItem(
      'token'
    );

    setUser(null);
    setTickets([]);
    setNotes([]);
    setStats(null);
    setSlaRules([]);
    setUsers([]);
  }


  function scrollTo(id) {

    document
      .getElementById(id)
      ?.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
  }


  function chooseService(service) {

    setSelectedService(
      service
    );

    setTimeout(
      () =>
        scrollTo(
          'service-request'
        ),
      50
    );
  }


  return (
    <main>

      <header>

        <div>

          <h1>
            Campus Service Desk
          </h1>

          <span>
            {isStudent
              ? 'Student Portal'
              : isStaff
                ? 'Staff Dashboard'
                : 'Campus Admin'}
            {' · '}
            {user.name}
          </span>

        </div>


        <div className="header-actions">

          <button
            type="button"
            className="theme-toggle"
            onClick={() =>
              setTheme(
                theme === 'light'
                  ? 'dark'
                  : 'light'
              )
            }
          >
            {theme === 'light'
              ? '🌙 Dark'
              : '☀️ Light'}
          </button>


          <button
            type="button"
            onClick={logout}
          >
            Log out
          </button>

        </div>

      </header>


      <div className="layout">

        <aside>

          <div className="notification-title">

            <div>

              <h3>
                Notifications
              </h3>

              <small>
                Recent service updates
              </small>

            </div>

            <span className="notification-count">
              {notes.length}
            </span>

          </div>


          {notes.length === 0 ? (

            <div className="notification-empty">

              <div className="portal-icon">
                🔔
              </div>

              <strong>
                No notifications
              </strong>

              <p>
                Updates will appear here.
              </p>

            </div>

          ) : (

            <div className="notification-list">

              {notes.slice(0, 8).map(
                notification => (

                  <article
                    className="notification-item"
                    key={notification.id}
                  >

                    <div className="notification-item-icon">
                      🔔
                    </div>

                    <div>

                      <strong>
                        Service Update
                      </strong>

                      <p>
                        {notification.message}
                      </p>

                      <small>
                        {formatDate(
                          notification.created_at
                        )}
                      </small>

                    </div>

                  </article>

                )
              )}

            </div>

          )}

        </aside>


        <div className="content">


          {/* =================================================
             STUDENT
          ================================================= */}

          {isStudent && (
            <>

              <StudentDashboard
                user={user}
                tickets={tickets}
                notes={notes}
                onServiceSelect={
                  chooseService
                }
                onScroll={
                  scrollTo
                }
              />


              <TicketForm
                reload={
                  () =>
                    reload(user)
                }
                selectedService={
                  selectedService
                }
                onServiceChange={
                  setSelectedService
                }
              />


              <TicketTable
                tickets={tickets}
                staff={false}
                reload={
                  () =>
                    reload(user)
                }
                user={user}
              />

            </>
          )}


          {/* =================================================
             STAFF
          ================================================= */}

          {isStaff && (
            <>

              <StaffDashboard
                tickets={tickets}
                user={user}
                onScroll={scrollTo}
              />


              <TicketTable
                tickets={tickets}
                staff={true}
                reload={
                  () =>
                    reload(user)
                }
                user={user}
              />

            </>
          )}


          {/* =================================================
             ADMIN
          ================================================= */}

          {isAdmin && (
            <>

              <section className="portal-section">

                <div className="section-heading">

                  <div>

                    <span className="portal-label">
                      ADMINISTRATION
                    </span>

                    <h2>
                      Administration
                    </h2>

                    <p>
                      Monitor service requests,
                      SLA performance and campus workload.
                    </p>

                  </div>

                </div>


                <div className="portal-grid">

                  <div
                    className="portal-card clickable-card"
                    onClick={() =>
                      scrollTo(
                        'admin-analytics'
                      )
                    }
                  >
                    <div className="portal-icon">
                      📊
                    </div>

                    <h3>
                      Analytics
                    </h3>

                    <p>
                      View ticket volume,
                      resolution and SLA statistics.
                    </p>
                  </div>


                  <div
                    className="portal-card clickable-card"
                    onClick={() =>
                      scrollTo(
                        'admin-tickets'
                      )
                    }
                  >
                    <div className="portal-icon">
                      🎫
                    </div>

                    <h3>
                      Ticket Management
                    </h3>

                    <p>
                      Monitor and manage campus
                      service requests.
                    </p>
                  </div>


                  <div
                    className="portal-card clickable-card"
                    onClick={() =>
                      scrollTo(
                        'admin-sla'
                      )
                    }
                  >
                    <div className="portal-icon">
                      ⏱️
                    </div>

                    <h3>
                      SLA Management
                    </h3>

                    <p>
                      Configure response time,
                      thresholds and escalation.
                    </p>
                  </div>


                  <div
                    className="portal-card clickable-card"
                    onClick={() =>
                      scrollTo(
                        'admin-users'
                      )
                    }
                  >
                    <div className="portal-icon">
                      👥
                    </div>

                    <h3>
                      User Management
                    </h3>

                    <p>
                      Manage accounts, roles,
                      departments and status.
                    </p>
                  </div>

                </div>

              </section>


              <AdminAnalytics
                stats={stats}
              />


              <AdminSLA
                rules={slaRules}
                onReload={
                  () =>
                    reload(user)
                }
              />


              <AdminUsers
                users={users}
                onReload={
                  () =>
                    reload(user)
                }
                currentUser={user}
              />


              <TicketTable
                id="admin-tickets"
                tickets={tickets}
                staff={true}
                reload={
                  () =>
                    reload(user)
                }
                user={user}
              />

            </>
          )}

        </div>

      </div>

    </main>
  );
}


/* =========================================================
   ROOT
========================================================= */

createRoot(
  document.getElementById('root')
).render(
  <App />
);


