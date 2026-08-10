import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';

const API_BASE = process.env.REACT_APP_API_URL || 'http://127.0.0.1/nodejs_projects/kbd_simple_boarding/api';
const LOGIN_URL = `${API_BASE}/login.php`;
const LOCATIONS_URL = `${API_BASE}/location.php`;

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

  const visibleMenu = useMemo(() => {
    if (userRole === 1) return menuButtons;
    if (userRole === 2) return menuButtons.filter((btn) => btn.id !== 'processes');
    if (userRole === 3) return menuButtons.filter((btn) => btn.id === 'overview');
    return [];
  }, [userRole]);

  useEffect(() => {
    if (isLoggedIn && selectedMenu === 'locations') {
      loadLocations();
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
    setDetailMode(null);
    setSelectedLocation(null);
    setDetailLocationValue('');
    setDetailMessage('');
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
                  <p>Verwalten Sie Ihre Standorte hier.</p>

                  {locationsLoading ? (
                    <p>Lade Standorte...</p>
                  ) : (
                    <table className="locations-table">
                      <thead>
                        <tr>
                          <th>Standort</th>
                          <th className="location-table-row-action">
                            <button className="add-location-button" onClick={handleStartNewLocation}>
                              +
                            </button>
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        {locations.map((item) => (
                          <tr key={item.id}>
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
                  {detailMode === 'edit' && selectedLocation ? (
                    <>
                      <h3>Standort bearbeiten</h3>
                      <label className="form-label">ID: {selectedLocation.id}</label>

                      <label className="form-label" htmlFor="location">
                        Standort:
                      </label>
                      <input
                        id="location"
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
                      <label className="form-label">ID:</label>

                      <label className="form-label" htmlFor="new-location">
                        Standort:
                      </label>
                      <input
                        id="new-location"
                        type="text"
                        value={detailLocationValue}
                        onChange={(e) => setDetailLocationValue(e.target.value)}
                      />

                      <button className="save-location-button" onClick={handleSaveLocation}>
                        Neuen Standort anlegen
                      </button>
                    </>
                  ) : (
                    <>
                      <h3>Details</h3>
                      <p>Wähle einen Standort aus oder lege einen neuen an.</p>
                    </>
                  )}

                  {detailMessage && <p className="detail-message">{detailMessage}</p>}
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