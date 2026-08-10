import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';

const API_BASE = process.env.REACT_APP_API_URL || 'http://127.0.0.1/nodejs_projects/kbd_simple_boarding/api';
const LOGIN_URL = `${API_BASE}/login.php`;
const LOCATIONS_URL = `${API_BASE}/location.php`;
const EMPLOYEES_URL = `${API_BASE}/employee.php`;
const JOBS_URL = `${API_BASE}/job.php`;
const ROLES_URL = `${API_BASE}/role.php`;
const FUNCTIONS_URL = `${API_BASE}/function.php`;

const menuButtons = [
  { id: 'overview', label: 'Übersicht' },
  { id: 'newbies', label: 'Newbies' },
  { id: 'locations', label: 'Standorte' },
  { id: 'employees', label: 'Mitarbeiter' },
  { id: 'jobs', label: 'Jobs' },
  { id: 'roles', label: 'Rollen' },
  { id: 'functions', label: 'Funktionen' },
  { id: 'processes', label: 'Abläufe' },
];

const sectionContent = {
  overview: { title: 'Übersicht', text: 'Willkommen in der Übersicht.' },
  newbies: { title: 'Newbies', text: 'Hier erscheinen die Newbie-Daten.' },
  locations: { title: 'Standorte', text: 'Hier werden die Standorte verwaltet.' },
  employees: { title: 'Mitarbeiter', text: 'Hier werden die Mitarbeiter verwaltet.' },
  jobs: { title: 'Jobs', text: 'Hier werden die Jobs dargestellt.' },
  roles: { title: 'Rollen', text: 'Hier können Rollen verwaltet werden.' },
  functions: { title: 'Funktionen', text: 'Hier werden Funktionen angezeigt.' },
  processes: { title: 'Abläufe', text: 'Hier erscheinen die Abläufe.' },
};

const findLabel = (list, id, key) => {
  const item = list.find((row) => String(row.id) === String(id));
  return item ? item[key] : id;
};

function App() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [selectedMenu, setSelectedMenu] = useState('overview');
  const [error, setError] = useState('');
  const [userRole, setUserRole] = useState(null);
  const [loggedUser, setLoggedUser] = useState(null);

  const [locations, setLocations] = useState([]);
  const [locationsLoading, setLocationsLoading] = useState(false);
  const [detailMode, setDetailMode] = useState(null); // 'edit' | 'new' | null
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [detailLocationValue, setDetailLocationValue] = useState('');
  const [detailMessage, setDetailMessage] = useState('');

  const [employees, setEmployees] = useState([]);
  const [employeesLoading, setEmployeesLoading] = useState(false);
  const [employeeDetailMode, setEmployeeDetailMode] = useState(null); // 'edit' | 'new' | null
  const [selectedEmployee, setSelectedEmployee] = useState(null);
  const [employeeDetail, setEmployeeDetail] = useState({
    id: '',
    first_name: '',
    last_name: '',
    email: '',
    department: '',
    username: '',
    password: '',
    location_id: '0',
    job_id: '0',
    role_id: '0',
    function_id: '0',
  });
  const [employeeMessage, setEmployeeMessage] = useState('');
  const [jobs, setJobs] = useState([]);
  const [roles, setRoles] = useState([]);
  const [functions, setFunctions] = useState([]);

  const visibleMenu = useMemo(() => {
    if (userRole === 1) return menuButtons;
    if (userRole === 2) return menuButtons.filter((btn) => btn.id !== 'processes');
    if (userRole === 3) return menuButtons.filter((btn) => btn.id === 'overview');
    return [];
  }, [userRole]);

  useEffect(() => {
    if (isLoggedIn) {
      if (selectedMenu === 'locations') {
        loadLocations();
      }

      if (selectedMenu === 'employees') {
        loadLocations();
        loadEmployees();
        loadJobs();
        loadRoles();
        loadFunctions();
      }
    }
  }, [isLoggedIn, selectedMenu]);

  const loadLocations = async () => {
    setLocationsLoading(true);
    setDetailMessage('');

    try {
      const response = await fetch(LOCATIONS_URL, {
        method: 'GET',
        headers: {
          Accept: 'application/json',
        },
      });

      const data = await response.json();

      if (data.success) {
        setLocations(data.locations || []);
      } else {
        setDetailMessage(data.message || 'Fehler beim Laden der Standorte.');
      }
    } catch (err) {
      setDetailMessage('Fehler beim Laden der Standorte.');
    } finally {
      setLocationsLoading(false);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch(LOGIN_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username,
          password,
        }),
      });

      const data = await response.json();

      if (data.success) {
        setUserRole(data.user.role_id);
        setLoggedUser({
          username: data.user.username,
          role_id: data.user.role_id,
        });
        setIsLoggedIn(true);
        setError('');
        setSelectedMenu('overview');
      } else {
        setError(data.message || 'Login fehlgeschlagen.');
      }
    } catch (err) {
      setError('Server-Fehler. Prüfe PHP/MySQL und die API-URL.');
    }
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setUserRole(null);
    setUsername('');
    setPassword('');
    setError('');
    setLocations([]);
    setEmployees([]);
    setLocationsLoading(false);
    setEmployeesLoading(false);
    setDetailMode(null);
    setSelectedLocation(null);
    setDetailLocationValue('');
    setDetailMessage('');
    setEmployeeDetailMode(null);
    setSelectedEmployee(null);
    setEmployeeDetail({
      id: '',
      first_name: '',
      last_name: '',
      email: '',
      department: '',
      username: '',
      password: '',
      location_id: '0',
      job_id: '0',
      role_id: '0',
      function_id: '0',
    });
    setEmployeeMessage('');
    setJobs([]);
    setRoles([]);
    setFunctions([]);
  };

  const handleStartNewLocation = () => {
    setDetailMode('new');
    setSelectedLocation(null);
    setDetailLocationValue('');
    setDetailMessage('');
  };

  const handleEditLocation = (location) => {
    setDetailMode('edit');
    setSelectedLocation(location);
    setDetailLocationValue(location.location || '');
    setDetailMessage('');
  };

  const handleSaveLocation = async (e) => {
    e.preventDefault();

    const trimmedValue = detailLocationValue.trim();

    if (!trimmedValue) {
      setDetailMessage('Bitte einen Standort eingeben.');
      return;
    }

    try {
      if (detailMode === 'edit' && selectedLocation) {
        const response = await fetch(LOCATIONS_URL, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            id: selectedLocation.id,
            location: trimmedValue,
          }),
        });

        const data = await response.json();

        if (data.success) {
          setLocations((prev) =>
            prev.map((item) =>
              item.id === selectedLocation.id
                ? { ...item, location: trimmedValue }
                : item
            )
          );
          setDetailMessage('Änderungen gespeichert.');
          setDetailMode(null);
          setSelectedLocation(null);
          setDetailLocationValue('');
        } else {
          setDetailMessage(data.message || 'Speichern fehlgeschlagen.');
        }
      } else {
        const response = await fetch(LOCATIONS_URL, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            location: trimmedValue,
          }),
        });

        const data = await response.json();

        if (data.success) {
          setLocations((prev) => [
            ...prev,
            {
              id: data.location.id,
              location: data.location.location,
            },
          ]);
          setDetailMessage('Neuer Standort angelegt.');
          setDetailMode(null);
          setSelectedLocation(null);
          setDetailLocationValue('');
        } else {
          setDetailMessage(data.message || 'Anlegen fehlgeschlagen.');
        }
      }
    } catch (err) {
      setDetailMessage('Serverfehler beim Speichern.');
    }
  };

  const handleDeleteLocation = async (locationId) => {
    const confirmed = window.confirm('Diesen Standort wirklich löschen?');

    if (!confirmed) {
      return;
    }

    try {
      const response = await fetch(LOCATIONS_URL, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          id: locationId,
        }),
      });

      const data = await response.json();

      if (data.success) {
        setLocations((prev) => prev.filter((item) => item.id !== locationId));

        if (selectedLocation?.id === locationId) {
          setDetailMode(null);
          setSelectedLocation(null);
          setDetailLocationValue('');
        }

        setDetailMessage('Standort gelöscht.');
      } else {
        setDetailMessage(data.message || 'Löschen fehlgeschlagen.');
      }
    } catch (err) {
      setDetailMessage('Serverfehler beim Löschen.');
    }
  };

  const loadEmployees = async () => {
    setEmployeesLoading(true);
    setEmployeeMessage('');

    try {
      const response = await fetch(EMPLOYEES_URL, {
        method: 'GET',
        headers: {
          Accept: 'application/json',
        },
      });

      const data = await response.json();

      if (data.success) {
        setEmployees(data.employees || []);
      } else {
        setEmployeeMessage(data.message || 'Fehler beim Laden der Mitarbeiter.');
      }
    } catch (err) {
      setEmployeeMessage('Fehler beim Laden der Mitarbeiter.');
    } finally {
      setEmployeesLoading(false);
    }
  };

  const loadJobs = async () => {
    try {
      const response = await fetch(JOBS_URL, {
        method: 'GET',
        headers: {
          Accept: 'application/json',
        },
      });

      const data = await response.json();

      if (data.success) {
        setJobs(data.jobs || []);
      }
    } catch (err) {
      // ignore for now
    }
  };

  const loadRoles = async () => {
    try {
      const response = await fetch(ROLES_URL, {
        method: 'GET',
        headers: {
          Accept: 'application/json',
        },
      });

      const data = await response.json();

      if (data.success) {
        setRoles(data.roles || []);
      }
    } catch (err) {
      // ignore for now
    }
  };

  const loadFunctions = async () => {
    try {
      const response = await fetch(FUNCTIONS_URL, {
        method: 'GET',
        headers: {
          Accept: 'application/json',
        },
      });

      const data = await response.json();

      if (data.success) {
        setFunctions(data.functions || []);
      }
    } catch (err) {
      // ignore for now
    }
  };

  const handleStartNewEmployee = () => {
    setEmployeeDetailMode('new');
    setSelectedEmployee(null);
    setEmployeeDetail({
      id: '',
      first_name: '',
      last_name: '',
      email: '',
      department: '',
      username: '',
      password: '',
      location_id: '0',
      job_id: '0',
      role_id: '0',
      function_id: '0',
    });
    setEmployeeMessage('');
  };

  const handleEditEmployee = (employee) => {
    setEmployeeDetailMode('edit');
    setSelectedEmployee(employee);
    setEmployeeDetail({
      id: employee.id,
      first_name: employee.first_name || '',
      last_name: employee.last_name || '',
      email: employee.email || '',
      department: employee.department || '',
      username: employee.username || '',
      password: employee.password || '',
      location_id: String(employee.location_id || '0'),
      job_id: String(employee.job_id || '0'),
      role_id: String(employee.role_id || '0'),
      function_id: String(employee.function_id || '0'),
    });
    setEmployeeMessage('');
  };

  const handleSaveEmployee = async (e) => {
    if (e && e.preventDefault) {
      e.preventDefault();
    }

    const trimmedFirstName = employeeDetail.first_name.trim();
    const trimmedLastName = employeeDetail.last_name.trim();

    if (!trimmedFirstName || !trimmedLastName) {
      setEmployeeMessage('Bitte Vorname und Nachname eingeben.');
      return;
    }

    const payload = {
      id: employeeDetail.id,
      first_name: trimmedFirstName,
      last_name: trimmedLastName,
      email: employeeDetail.email.trim(),
      department: employeeDetail.department.trim(),
      username: employeeDetail.username.trim(),
      password: employeeDetail.password,
      location_id: Number(employeeDetail.location_id),
      job_id: Number(employeeDetail.job_id),
      role_id: Number(employeeDetail.role_id),
      function_id: Number(employeeDetail.function_id),
    };

    try {
      const response = await fetch(EMPLOYEES_URL, {
        method: employeeDetailMode === 'edit' ? 'PUT' : 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (data.success) {
        if (employeeDetailMode === 'edit') {
          setEmployees((prev) =>
            prev.map((item) =>
              String(item.id) === String(payload.id)
                ? { ...item, ...payload }
                : item
            )
          );
          setEmployeeMessage('Änderungen gespeichert.');
        } else {
          const newEmployee = data.employee || { ...payload, id: data.id || Date.now() };
          setEmployees((prev) => [...prev, newEmployee]);
          setEmployeeMessage('Neuen Mitarbeiter gespeichert.');
        }

        setEmployeeDetailMode(null);
        setSelectedEmployee(null);
        setEmployeeDetail({
          id: '',
          first_name: '',
          last_name: '',
          email: '',
          department: '',
          username: '',
          password: '',
          location_id: '0',
          job_id: '0',
          role_id: '0',
          function_id: '0',
        });
      } else {
        setEmployeeMessage(data.message || 'Speichern fehlgeschlagen.');
      }
    } catch (err) {
      setEmployeeMessage('Serverfehler beim Speichern.');
    }
  };

  const handleDeleteEmployee = async (employeeId) => {
    const confirmed = window.confirm('Diesen Mitarbeiter wirklich löschen?');

    if (!confirmed) {
      return;
    }

    try {
      const response = await fetch(EMPLOYEES_URL, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          id: employeeId,
        }),
      });

      const data = await response.json();

      if (data.success) {
        setEmployees((prev) => prev.filter((item) => String(item.id) !== String(employeeId)));

        if (String(selectedEmployee?.id) === String(employeeId)) {
          setEmployeeDetailMode(null);
          setSelectedEmployee(null);
          setEmployeeDetail({
            id: '',
            first_name: '',
            last_name: '',
            email: '',
            department: '',
            username: '',
            password: '',
            location_id: '0',
            job_id: '0',
            role_id: '0',
            function_id: '0',
          });
        }

        setEmployeeMessage('Mitarbeiter gelöscht.');
      } else {
        setEmployeeMessage(data.message || 'Löschen fehlgeschlagen.');
      }
    } catch (err) {
      setEmployeeMessage('Serverfehler beim Löschen.');
    }
  };

  const activeSection = sectionContent[selectedMenu] || sectionContent.overview;

  return (
    <div className="app-shell">
      <header className="header">
        <div className="header-left">
          <h1>KBD – SimpleBoarding</h1>
        </div>

        <div className="header-right">
          {isLoggedIn && loggedUser && (
            <span className="user-info">
              {loggedUser.username} ({loggedUser.role_id})
            </span>
          )}

          {isLoggedIn && (
            <button className="logout-button" onClick={handleLogout}>
              Logout
            </button>
          )}

          <img src="/favicon.ico" alt="Logo" className="header-logo" />
        </div>
      </header>

      <main className="main">
        {isLoggedIn && (
          <>
            <aside className="menu">
              {visibleMenu.map((btn) => (
                <button
                  key={btn.id}
                  className={`menu-button ${selectedMenu === btn.id ? 'active' : ''}`}
                  onClick={() => setSelectedMenu(btn.id)}
                >
                  {btn.label}
                </button>
              ))}
            </aside>

            <section className="data">
              {selectedMenu === 'locations' ? (
                <div className="locations-panel">
                  <h1>Standorte</h1>
                  <p>Hier werden die Standorte verwaltet.</p>

                  <button className="add-location-button" onClick={handleStartNewLocation}>
                    Neuen Standort anlegen
                  </button>

                  {locationsLoading ? (
                    <p>Lade Standorte...</p>
                  ) : locations.length === 0 ? (
                    <p>Keine Standorte gefunden.</p>
                  ) : (
                    <table className="locations-table">
                      <thead>
                        <tr>
                          <th>ID</th>
                          <th>Standort</th>
                          <th className="location-table-row-action">Aktionen</th>
                        </tr>
                      </thead>
                      <tbody>
                        {locations.map((item) => (
                          <tr key={item.id}>
                            <td>{item.id}</td>
                            <td>{item.location}</td>
                            <td className="location-table-row-action">
                              <button
                                className="edit-location-button"
                                onClick={() => handleEditLocation(item)}
                              >
                                Edit
                              </button>
                              <button
                                className="delete-location-button"
                                onClick={() => handleDeleteLocation(item.id)}
                              >
                                -
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}
                </div>
              ) : selectedMenu === 'employees' ? (
                <div className="locations-panel">
                  <h1>Mitarbeiter</h1>
                  <p>Verwalten Sie Ihre Mitarbeiter hier.</p>

                  <button className="add-location-button" onClick={handleStartNewEmployee}>
                    Neuen Mitarbeiter anlegen
                  </button>

                  {employeesLoading ? (
                    <p>Lade Mitarbeiter...</p>
                  ) : employees.length === 0 ? (
                    <p>Keine Mitarbeiter gefunden.</p>
                  ) : (
                    <table className="locations-table">
                      <thead>
                        <tr>
                          <th>Vorname</th>
                          <th>Nachname</th>
                          <th>Abteilung</th>
                          <th>Standort</th>
                          <th>Job</th>
                          <th>Rolle</th>
                          <th>Funktion</th>
                          <th className="location-table-row-action">Aktionen</th>
                        </tr>
                      </thead>
                      <tbody>
                        {employees.map((item) => (
                          <tr key={item.id}>
                            <td>{item.first_name}</td>
                            <td>{item.last_name}</td>
                            <td>{item.department}</td>
                            <td>{findLabel(locations, item.location_id, 'location')}</td>
                            <td>{findLabel(jobs, item.job_id, 'job')}</td>
                            <td>{findLabel(roles, item.role_id, 'role')}</td>
                            <td>{findLabel(functions, item.function_id, 'function')}</td>
                            <td className="location-table-row-action">
                              <button
                                className="edit-location-button"
                                onClick={() => handleEditEmployee(item)}
                              >
                                Edit
                              </button>
                              <button
                                className="delete-location-button"
                                onClick={() => handleDeleteEmployee(item.id)}
                              >
                                -
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}
                </div>
              ) : (
                <>
                  <h2>{activeSection.title}</h2>
                  <p>{activeSection.text}</p>
                </>
              )}
            </section>

            <aside className="details">
              {selectedMenu === 'locations' ? (
                <div className="location-form">
                  {detailMode === 'edit' ? (
                    <>
                      <h3>Standort bearbeiten</h3>
                      <label className="form-label">ID: {selectedLocation?.id}</label>

                      <label className="form-label" htmlFor="location-name">
                        Standort:
                      </label>
                      <input
                        id="location-name"
                        type="text"
                        value={detailLocationValue}
                        onChange={(e) => setDetailLocationValue(e.target.value)}
                      />

                      <button className="save-location-button" onClick={handleSaveLocation}>
                        Änderungen speichern
                      </button>
                    </>
                  ) : detailMode === 'new' ? (
                    <>
                      <h3>Neuen Standort anlegen</h3>
                      <label className="form-label" htmlFor="location-name">
                        Standort:
                      </label>
                      <input
                        id="location-name"
                        type="text"
                        value={detailLocationValue}
                        onChange={(e) => setDetailLocationValue(e.target.value)}
                      />

                      <button className="save-location-button" onClick={handleSaveLocation}>
                        Neuen Standort speichern
                      </button>
                    </>
                  ) : (
                    <>
                      <h3>Details</h3>
                      <p>Wähle einen Standort oder lege einen neuen an.</p>
                    </>
                  )}

                  {detailMessage && <p className="detail-message">{detailMessage}</p>}
                </div>
              ) : selectedMenu === 'employees' ? (
                <div className="location-form">
                  {employeeDetailMode === 'edit' ? (
                    <>
                      <h3>Mitarbeiter bearbeiten</h3>
                      <label className="form-label">ID: {employeeDetail.id}</label>

                      <label className="form-label" htmlFor="employee-first-name">
                        Vorname:
                      </label>
                      <input
                        id="employee-first-name"
                        type="text"
                        value={employeeDetail.first_name}
                        onChange={(e) =>
                          setEmployeeDetail((prev) => ({ ...prev, first_name: e.target.value }))
                        }
                      />

                      <label className="form-label" htmlFor="employee-last-name">
                        Nachname:
                      </label>
                      <input
                        id="employee-last-name"
                        type="text"
                        value={employeeDetail.last_name}
                        onChange={(e) =>
                          setEmployeeDetail((prev) => ({ ...prev, last_name: e.target.value }))
                        }
                      />

                      <label className="form-label" htmlFor="employee-email">
                        E-Mail:
                      </label>
                      <input
                        id="employee-email"
                        type="email"
                        value={employeeDetail.email}
                        onChange={(e) =>
                          setEmployeeDetail((prev) => ({ ...prev, email: e.target.value }))
                        }
                      />

                      <label className="form-label" htmlFor="employee-department">
                        Abteilung:
                      </label>
                      <input
                        id="employee-department"
                        type="text"
                        value={employeeDetail.department}
                        onChange={(e) =>
                          setEmployeeDetail((prev) => ({ ...prev, department: e.target.value }))
                        }
                      />

                      <label className="form-label" htmlFor="employee-username">
                        Benutzername:
                      </label>
                      <input
                        id="employee-username"
                        type="text"
                        value={employeeDetail.username}
                        onChange={(e) =>
                          setEmployeeDetail((prev) => ({ ...prev, username: e.target.value }))
                        }
                      />

                      <label className="form-label" htmlFor="employee-password">
                        Passwort:
                      </label>
                      <input
                        id="employee-password"
                        type="password"
                        value={employeeDetail.password}
                        onChange={(e) =>
                          setEmployeeDetail((prev) => ({ ...prev, password: e.target.value }))
                        }
                      />

                      <label className="form-label" htmlFor="employee-location">
                        Standort:
                      </label>
                      <select
                        id="employee-location"
                        value={employeeDetail.location_id}
                        onChange={(e) =>
                          setEmployeeDetail((prev) => ({ ...prev, location_id: e.target.value }))
                        }
                      >
                        <option value="0">Bitte wählen</option>
                        {locations.map((loc) => (
                          <option key={loc.id} value={loc.id}>
                            {loc.location}
                          </option>
                        ))}
                      </select>

                      <label className="form-label" htmlFor="employee-job">
                        Job:
                      </label>
                      <select
                        id="employee-job"
                        value={employeeDetail.job_id}
                        onChange={(e) =>
                          setEmployeeDetail((prev) => ({ ...prev, job_id: e.target.value }))
                        }
                      >
                        <option value="0">Bitte wählen</option>
                        {jobs.map((job) => (
                          <option key={job.id} value={job.id}>
                            {job.job}
                          </option>
                        ))}
                      </select>

                      <label className="form-label" htmlFor="employee-role">
                        Rolle:
                      </label>
                      <select
                        id="employee-role"
                        value={employeeDetail.role_id}
                        onChange={(e) =>
                          setEmployeeDetail((prev) => ({ ...prev, role_id: e.target.value }))
                        }
                      >
                        <option value="0">Bitte wählen</option>
                        {roles.map((role) => (
                          <option key={role.id} value={role.id}>
                            {role.role}
                          </option>
                        ))}
                      </select>

                      <label className="form-label" htmlFor="employee-function">
                        Funktion:
                      </label>
                      <select
                        id="employee-function"
                        value={employeeDetail.function_id}
                        onChange={(e) =>
                          setEmployeeDetail((prev) => ({ ...prev, function_id: e.target.value }))
                        }
                      >
                        <option value="0">Bitte wählen</option>
                        {functions.map((func) => (
                          <option key={func.id} value={func.id}>
                            {func.function}
                          </option>
                        ))}
                      </select>

                      <button className="save-location-button" onClick={handleSaveEmployee}>
                        Änderungen speichern
                      </button>
                    </>
                  ) : employeeDetailMode === 'new' ? (
                    <>
                      <h3>Neuen Mitarbeiter anlegen</h3>
                      <label className="form-label">ID:</label>

                      <label className="form-label" htmlFor="employee-first-name">
                        Vorname:
                      </label>
                      <input
                        id="employee-first-name"
                        type="text"
                        value={employeeDetail.first_name}
                        onChange={(e) =>
                          setEmployeeDetail((prev) => ({ ...prev, first_name: e.target.value }))
                        }
                      />

                      <label className="form-label" htmlFor="employee-last-name">
                        Nachname:
                      </label>
                      <input
                        id="employee-last-name"
                        type="text"
                        value={employeeDetail.last_name}
                        onChange={(e) =>
                          setEmployeeDetail((prev) => ({ ...prev, last_name: e.target.value }))
                        }
                      />

                      <label className="form-label" htmlFor="employee-email">
                        E-Mail:
                      </label>
                      <input
                        id="employee-email"
                        type="email"
                        value={employeeDetail.email}
                        onChange={(e) =>
                          setEmployeeDetail((prev) => ({ ...prev, email: e.target.value }))
                        }
                      />

                      <label className="form-label" htmlFor="employee-department">
                        Abteilung:
                      </label>
                      <input
                        id="employee-department"
                        type="text"
                        value={employeeDetail.department}
                        onChange={(e) =>
                          setEmployeeDetail((prev) => ({ ...prev, department: e.target.value }))
                        }
                      />

                      <label className="form-label" htmlFor="employee-username">
                        Benutzername:
                      </label>
                      <input
                        id="employee-username"
                        type="text"
                        value={employeeDetail.username}
                        onChange={(e) =>
                          setEmployeeDetail((prev) => ({ ...prev, username: e.target.value }))
                        }
                      />

                      <label className="form-label" htmlFor="employee-password">
                        Passwort:
                      </label>
                      <input
                        id="employee-password"
                        type="password"
                        value={employeeDetail.password}
                        onChange={(e) =>
                          setEmployeeDetail((prev) => ({ ...prev, password: e.target.value }))
                        }
                      />

                      <label className="form-label" htmlFor="employee-location">
                        Standort:
                      </label>
                      <select
                        id="employee-location"
                        value={employeeDetail.location_id}
                        onChange={(e) =>
                          setEmployeeDetail((prev) => ({ ...prev, location_id: e.target.value }))
                        }
                      >
                        <option value="0">Bitte wählen</option>
                        {locations.map((loc) => (
                          <option key={loc.id} value={loc.id}>
                            {loc.location}
                          </option>
                        ))}
                      </select>

                      <label className="form-label" htmlFor="employee-job">
                        Job:
                      </label>
                      <select
                        id="employee-job"
                        value={employeeDetail.job_id}
                        onChange={(e) =>
                          setEmployeeDetail((prev) => ({ ...prev, job_id: e.target.value }))
                        }
                      >
                        <option value="0">Bitte wählen</option>
                        {jobs.map((job) => (
                          <option key={job.id} value={job.id}>
                            {job.job}
                          </option>
                        ))}
                      </select>

                      <label className="form-label" htmlFor="employee-role">
                        Rolle:
                      </label>
                      <select
                        id="employee-role"
                        value={employeeDetail.role_id}
                        onChange={(e) =>
                          setEmployeeDetail((prev) => ({ ...prev, role_id: e.target.value }))
                        }
                      >
                        <option value="0">Bitte wählen</option>
                        {roles.map((role) => (
                          <option key={role.id} value={role.id}>
                            {role.role}
                          </option>
                        ))}
                      </select>

                      <label className="form-label" htmlFor="employee-function">
                        Funktion:
                      </label>
                      <select
                        id="employee-function"
                        value={employeeDetail.function_id}
                        onChange={(e) =>
                          setEmployeeDetail((prev) => ({ ...prev, function_id: e.target.value }))
                        }
                      >
                        <option value="0">Bitte wählen</option>
                        {functions.map((func) => (
                          <option key={func.id} value={func.id}>
                            {func.function}
                          </option>
                        ))}
                      </select>

                      <button className="save-location-button" onClick={handleSaveEmployee}>
                        Neuen Mitarbeiter speichern
                      </button>
                    </>
                  ) : (
                    <>
                      <h3>Details</h3>
                      <p>Wählen Sie einen Mitarbeiter aus oder legen Sie einen neuen an.</p>
                    </>
                  )}

                  {employeeMessage && <p className="detail-message">{employeeMessage}</p>}
                </div>
              ) : (
                <>
                  <h3>Details</h3>
                  <p>
                    <strong>Rolle:</strong> {userRole}
                  </p>
                  <p>
                    <strong>Aktueller Bereich:</strong> {activeSection.title}
                  </p>
                </>
              )}
            </aside>
          </>
        )}
      </main>

      <footer className="footer">
        <span>Bei technischen Problemen: Frank anrufen</span>
      </footer>

      {!isLoggedIn && (
        <div className="login-overlay">
          <form className="login-card" onSubmit={handleLogin}>
            <h2>Login</h2>

            <label className="login-label" htmlFor="username">
              Benutzer
            </label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Benutzer"
            />

            <label className="login-label" htmlFor="password">
              Passwort
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Passwort"
            />

            {error && <p className="login-error">{error}</p>}

            <button type="submit" className="login-button">
              Login
            </button>
          </form>
        </div>
      )}
    </div>
  );
}

const root = createRoot(document.getElementById('root'));
root.render(<App />);